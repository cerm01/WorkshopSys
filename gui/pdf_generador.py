import io
import sys
import subprocess
import os
from datetime import datetime
from functools import partial

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth 
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow no está instalado. pip install Pillow")
    Image = None

from PyQt5.QtWidgets import QFileDialog, QMessageBox

def _dibujar_encabezado(c, empresa_data):
    """Dibuja el logo y los datos de la empresa (CORREGIDO v5)."""

    logo_box_x = 1 * inch
    logo_box_width = 1.5 * inch
    logo_box_height = 1.5 * inch
    logo_box_y_top = 10.7 * inch
    logo_box_y_bottom = logo_box_y_top - logo_box_height

    text_x_start = logo_box_x + logo_box_width + 0.2 * inch 
    text_y_start = logo_box_y_top
    max_text_width = (8.5 * inch) - text_x_start - (1 * inch)

    logo_bytes = empresa_data.get('logo_data')
    if logo_bytes and Image:
        try:
            img_buffer = io.BytesIO(logo_bytes)
            img_reader = ImageReader(img_buffer) 
            c.drawImage(
                img_reader,
                logo_box_x, 
                logo_box_y_bottom, 
                width=logo_box_width,
                height=logo_box_height,
                preserveAspectRatio=True, 
                mask='auto',
                anchor='c'
            )
        except Exception as e:
            print(f"Error al dibujar logo (v5): {e}")

    nombre_empresa = empresa_data.get('nombre_comercial', 'TALLER')
    font_size = 16
    while font_size > 8 and stringWidth(nombre_empresa, "Helvetica-Bold", font_size) > max_text_width:
        font_size -= 1
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(text_x_start, text_y_start, nombre_empresa)

    c.setFont("Helvetica", 10)
    y_addr = text_y_start - 0.2 * inch # Bajar desde el título

    if rfc := empresa_data.get('rfc'):
        c.drawString(text_x_start, y_addr, rfc)
        y_addr -= 0.2 * inch
        
    if calle := empresa_data.get('calle'):
        c.drawString(text_x_start, y_addr, calle)
        y_addr -= 0.2 * inch
    
    colonia = empresa_data.get('colonia', '')
    cp = empresa_data.get('cp', '')
    if colonia or cp:
        linea = f"{colonia}{', ' if colonia and cp else ''}{f'C.P. {cp}' if cp else ''}"
        c.drawString(text_x_start, y_addr, linea)
        y_addr -= 0.2 * inch

    ciudad = empresa_data.get('ciudad', '') # 'ciudad' en la BD es el municipio
    estado = empresa_data.get('estado', '')
    if ciudad or estado:
        linea = f"{ciudad}{', ' if ciudad and estado else ''}{estado}"
        c.drawString(text_x_start, y_addr, linea)
        y_addr -= 0.2 * inch

    tel1 = empresa_data.get('telefono1', '')
    tel2 = empresa_data.get('telefono2', '')
    if tel1 or tel2:
        linea = f"Tel: {tel1}{' / ' if tel1 and tel2 else ''}{tel2}"
        c.drawString(text_x_start, y_addr, linea)
        y_addr -= 0.2 * inch
    
    if email := empresa_data.get('email'):
        c.drawString(text_x_start, y_addr, email)
        y_addr -= 0.2 * inch

    if web := empresa_data.get('sitio_web'):
        c.drawString(text_x_start, y_addr, web)

def _dibujar_tabla_items(c, items, y_start):
    """Dibuja la tabla de conceptos."""
    c.setFont("Helvetica-Bold", 10)
    x_cant = 1.1 * inch
    x_desc = 1.8 * inch
    x_precio = 5.5 * inch
    x_importe = 6.5 * inch
    
    c.drawString(x_cant, y_start, "Cant.")
    c.drawString(x_desc, y_start, "Descripción")
    c.drawRightString(x_precio + 0.7*inch, y_start, "P. Unitario")
    c.drawRightString(x_importe + 0.7*inch, y_start, "Importe")
    c.line(x_cant - 0.1*inch, y_start - 0.1*inch, 7.5*inch, y_start - 0.1*inch)
    
    c.setFont("Helvetica", 9)
    y = y_start - 0.3 * inch
    
    for item in items:
        if item.get('tipo', 'normal') != 'normal': 
            continue
            
        c.drawString(x_cant, y, str(item['cantidad']))
        c.drawString(x_desc, y, item['descripcion'][:60]) # Limitar descripción
        c.drawRightString(x_precio + 0.7*inch, y, f"${item['precio_unitario']:,.2f}")
        c.drawRightString(x_importe + 0.7*inch, y, f"${item['importe']:,.2f}")
        y -= 0.25 * inch
    
    return y 

def _dibujar_totales(c, nota_data, y_start):
    """Dibuja el subtotal, impuestos y total."""
    c.setFont("Helvetica-Bold", 11)
    x_label = 5.5 * inch
    x_valor = 6.5 * inch
    
    y = y_start - 0.2*inch
    c.line(x_label - 0.2*inch, y, 7.5*inch, y)
    y -= 0.2 * inch
    
    c.drawString(x_label, y, "Subtotal:")
    c.drawRightString(x_valor + 0.7*inch, y, f"${nota_data.get('subtotal', 0):,.2f}")
    y -= 0.25 * inch

    c.drawString(x_label, y, "Impuestos:")
    c.drawRightString(x_valor + 0.7*inch, y, f"${nota_data.get('impuestos', 0):,.2f}")
    y -= 0.25 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label, y, "TOTAL:")
    c.drawRightString(x_valor + 0.7*inch, y, f"${nota_data.get('total', 0):,.2f}")


def generar_pdf_nota_venta(nota_data, empresa_data, save_path):
    """
    Función principal para generar el PDF de una Nota de Venta.
    """
    try:
        c = canvas.Canvas(save_path, pagesize=letter)
        width, height = letter 
        
        # 1. Encabezado (Logo y Datos Empresa)
        _dibujar_encabezado(c, empresa_data)
        
        # 2. Datos del Cliente y Folio
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, 9.0 * inch, "CLIENTE:")
        c.setFont("Helvetica", 11)
        c.drawString(1 * inch, 8.8 * inch, nota_data.get('cliente_nombre', ''))
        
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(7.5 * inch, 9.0 * inch, f"NOTA: {nota_data.get('folio', '')}")
        
        fecha_str = nota_data.get('fecha', '')
        fecha_formateada = fecha_str # Valor por defecto
        
        if fecha_str:
            try:
                fecha_dt = datetime.fromisoformat(fecha_str) 
                # Formatear a dd/MM/yyyy
                fecha_formateada = fecha_dt.strftime("%d/%m/%Y") 
            except ValueError:
                # Fallback por si acaso
                fecha_formateada = fecha_str.split('T')[0]

        c.setFont("Helvetica", 11)
        c.drawRightString(7.5 * inch, 8.8 * inch, f"Fecha: {fecha_formateada}")
        c.drawRightString(7.5 * inch, 8.6 * inch, f"Estado: {nota_data.get('estado', '')}")

        # 3. Tabla de Items
        y_tabla = 8.0 * inch
        y_final_tabla = _dibujar_tabla_items(c, nota_data.get('items', []), y_tabla)
        
        # 4. Totales
        _dibujar_totales(c, nota_data, y_final_tabla)
        
        # 5. Guardar el PDF
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def generar_pdf_cotizacion(cotizacion_data, empresa_data, save_path):
    """
    Función principal para generar el PDF de una Cotización.
    """
    try:
        c = canvas.Canvas(save_path, pagesize=letter)
        width, height = letter 
        
        # 1. Encabezado 
        _dibujar_encabezado(c, empresa_data)
        
        # 2. Datos del Cliente y Folio
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, 9.0 * inch, "CLIENTE:")
        c.setFont("Helvetica", 11)
        c.drawString(1 * inch, 8.8 * inch, cotizacion_data.get('cliente_nombre', ''))
        
        if proyecto := cotizacion_data.get('observaciones'):
             c.drawString(1 * inch, 8.6 * inch, f"Proyecto: {proyecto}")

        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(7.5 * inch, 9.0 * inch, f"COTIZACIÓN: {cotizacion_data.get('folio', '')}")
        
        # Formatear fecha de creación (ISO)
        fecha_str = cotizacion_data.get('fecha', '')
        fecha_formateada = fecha_str
        if fecha_str:
            try:
                fecha_dt = datetime.fromisoformat(fecha_str) 
                fecha_formateada = fecha_dt.strftime("%d/%m/%Y") 
            except ValueError:
                fecha_formateada = fecha_str.split('T')[0]

        c.setFont("Helvetica", 11)
        c.drawRightString(7.5 * inch, 8.8 * inch, f"Fecha: {fecha_formateada}")
        
        vigencia_str = cotizacion_data.get('vigencia', '') 
        c.drawRightString(7.5 * inch, 8.6 * inch, f"Vigencia: {vigencia_str}")
        
        c.drawRightString(7.5 * inch, 8.4 * inch, f"Estado: {cotizacion_data.get('estado', '')}")

        # 3. Tabla de Items
        y_tabla = 8.0 * inch
        y_final_tabla = _dibujar_tabla_items(c, cotizacion_data.get('items', []), y_tabla)
        
        # 4. Totales
        _dibujar_totales(c, cotizacion_data, y_final_tabla)
        
        # 5. Guardar el PDF
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF de Cotización: {e}")
        import traceback
        traceback.print_exc()
        return False

def _dibujar_datos_orden(c, orden_data):
    """Dibuja los datos del cliente, vehículo y folio para la Orden de Trabajo."""
    # --- Cliente ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, 9.0 * inch, "CLIENTE:")
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, 8.8 * inch, orden_data.get('cliente_nombre', ''))

    # --- Folio y Fechas ---
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(7.5 * inch, 9.0 * inch, f"ORDEN DE TRABAJO: {orden_data.get('folio', '')}")
    
    # Formatear fecha de recepción (ISO con hora)
    fecha_str = orden_data.get('fecha_recepcion', '')
    fecha_formateada = fecha_str
    if fecha_str:
        try:
            fecha_dt = datetime.fromisoformat(fecha_str) 
            fecha_formateada = fecha_dt.strftime("%d/%m/%Y %H:%M") # Incluimos la hora
        except ValueError:
            fecha_formateada = fecha_str.split('T')[0]

    c.setFont("Helvetica", 11)
    c.drawRightString(7.5 * inch, 8.8 * inch, f"Fecha Recepción: {fecha_formateada}")
    c.drawRightString(7.5 * inch, 8.6 * inch, f"Estado: {orden_data.get('estado', '')}")
    
    # --- Datos del Vehículo ---
    c.setFont("Helvetica-Bold", 12)
    # Posicionamos esta sección más abajo
    c.drawString(1 * inch, 8.3 * inch, "VEHÍCULO:") 
    c.setFont("Helvetica", 10)
    
    y_vehiculo = 8.1 * inch # Posición Y para los datos del auto
    
    # Datos en 2 columnas para ahorrar espacio
    c.drawString(1.1 * inch, y_vehiculo, f"Marca: {orden_data.get('vehiculo_marca', '')}")
    c.drawString(3.5 * inch, y_vehiculo, f"Modelo: {orden_data.get('vehiculo_modelo', '')}")
    c.drawString(1.1 * inch, y_vehiculo - 0.2*inch, f"Año: {orden_data.get('vehiculo_ano', '')}")
    c.drawString(3.5 * inch, y_vehiculo - 0.2*inch, f"Placas: {orden_data.get('vehiculo_placas', '')}")

def _dibujar_tabla_items_orden(c, items, y_start):
    """Dibuja la tabla de conceptos para la Orden (solo Cantidad y Descripción)."""
    c.setFont("Helvetica-Bold", 10)
    x_cant = 1.1 * inch
    x_desc = 1.8 * inch
    
    c.drawString(x_cant, y_start, "Cant.")
    c.drawString(x_desc, y_start, "Descripción del Servicio / Observaciones")
    c.line(x_cant - 0.1*inch, y_start - 0.1*inch, 7.5*inch, y_start - 0.1*inch)
    
    c.setFont("Helvetica", 9)
    y = y_start - 0.3 * inch
    
    for item in items:
        # Ignorar items que no son 'normales'
        if item.get('tipo', 'normal') != 'normal': 
            continue
            
        c.drawString(x_cant, y, str(item['cantidad']))
        # Damos más espacio a la descripción (90 caracteres)
        c.drawString(x_desc, y, item['descripcion'][:90]) 
        y -= 0.25 * inch # Siguiente línea
    
    return y # Devuelve la última posición Y

def generar_pdf_orden_trabajo(orden_data, empresa_data, save_path):
    """
    Función principal para generar el PDF de una Orden de Trabajo.
    """
    try:
        c = canvas.Canvas(save_path, pagesize=letter)
        
        # 1. Encabezado 
        _dibujar_encabezado(c, empresa_data)
        
        # 2. Datos del Cliente, Vehículo y Folio
        _dibujar_datos_orden(c, orden_data)
        
        # 3. Tabla de Items
        y_tabla = 7.7 * inch
        y_final_tabla = _dibujar_tabla_items_orden(c, orden_data.get('items', []), y_tabla)
        
        # 4. Guardar el PDF
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF de Orden: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def _dibujar_datos_proveedor(c, nota_data):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, 9.0 * inch, "PROVEEDOR:")
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, 8.8 * inch, nota_data.get('proveedor_nombre', ''))

    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(7.5 * inch, 9.0 * inch, f"NOTA PROVEEDOR: {nota_data.get('folio', '')}")
    
    fecha_str = nota_data.get('fecha', '')
    fecha_formateada = fecha_str
    if fecha_str:
        try:
            fecha_dt = datetime.fromisoformat(fecha_str) 
            fecha_formateada = fecha_dt.strftime("%d/%m/%Y") 
        except ValueError:
            fecha_formateada = fecha_str.split('T')[0]

    c.setFont("Helvetica", 11)
    c.drawRightString(7.5 * inch, 8.8 * inch, f"Fecha: {fecha_formateada}")
    c.drawRightString(7.5 * inch, 8.6 * inch, f"Estado: {nota_data.get('estado', '')}")

def generar_pdf_nota_proveedor(nota_data, empresa_data, save_path):
    try:
        c = canvas.Canvas(save_path, pagesize=letter)
        
        _dibujar_encabezado(c, empresa_data)
        
        _dibujar_datos_proveedor(c, nota_data)

        y_tabla = 8.0 * inch
        y_final_tabla = _dibujar_tabla_items(c, nota_data.get('items', []), y_tabla)
        
        _dibujar_totales(c, nota_data, y_final_tabla)
        
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF de Nota Proveedor: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def _dibujar_datos_estado_cuenta(c, cliente_nombre, fecha_ini, fecha_fin):
    """Dibuja los datos del cliente y el rango de fechas."""
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, 9.0 * inch, "CLIENTE:")
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, 8.8 * inch, cliente_nombre)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(7.5 * inch, 9.0 * inch, "ESTADO DE CUENTA DE CLIENTE")
    
    c.setFont("Helvetica", 11)
    c.drawRightString(7.5 * inch, 8.8 * inch, f"Del: {fecha_ini.strftime('%d/%m/%Y')}")
    c.drawRightString(7.5 * inch, 8.6 * inch, f"Al: {fecha_fin.strftime('%d/%m/%Y')}")

def _dibujar_tabla_estado_cuenta(c, transacciones, y_start):
    """Dibuja la tabla de transacciones (cargos, abonos, balance)."""
    c.setFont("Helvetica-Bold", 9)
    x_fecha = 1.1 * inch
    x_doc = 1.9 * inch
    x_conc = 2.8 * inch
    x_cargo = 5.0 * inch
    x_abono = 5.9 * inch
    x_bal = 6.8 * inch
    
    y = y_start
    c.drawString(x_fecha, y, "Fecha")
    c.drawString(x_doc, y, "Documento")
    c.drawString(x_conc, y, "Concepto")
    c.drawRightString(x_cargo + 0.7*inch, y, "Cargo")
    c.drawRightString(x_abono + 0.7*inch, y, "Abono")
    c.drawRightString(x_bal + 0.7*inch, y, "Balance")
    y -= 0.1 * inch
    c.line(x_fecha - 0.1*inch, y, 7.5*inch, y)
    
    c.setFont("Helvetica", 8)
    y -= 0.2 * inch
    
    balance_actual = 0.0
    
    for trx in transacciones:
        cargo = trx.get('cargo', 0)
        abono = trx.get('abono', 0)
        balance_actual += (cargo - abono)
        
        c.drawString(x_fecha, y, trx['fecha'].strftime("%d/%m/%Y"))
        c.drawString(x_doc, y, trx['documento'])
        c.drawString(x_conc, y, trx.get('concepto', '')[:40]) # Acortar concepto
        
        if cargo > 0:
            c.drawRightString(x_cargo + 0.7*inch, y, f"${cargo:,.2f}")
        if abono > 0:
            c.drawRightString(x_abono + 0.7*inch, y, f"${abono:,.2f}")
        
        c.drawRightString(x_bal + 0.7*inch, y, f"${balance_actual:,.2f}")
        y -= 0.22 * inch
        
    return y

def _dibujar_totales_estado_cuenta(c, totales, y_start):
    """Dibuja los totales del estado de cuenta."""
    c.setFont("Helvetica-Bold", 11)
    x_label = 5.0 * inch
    x_valor = 6.5 * inch
    
    y = y_start - 0.2*inch
    c.line(x_label - 0.2*inch, y, 7.5*inch, y)
    y -= 0.2 * inch
    
    c.drawString(x_label, y, "Total Cargos (Notas):")
    c.drawRightString(x_valor + 0.7*inch, y, f"${totales['cargos']:,.2f}")
    y -= 0.25 * inch

    c.drawString(x_label, y, "Total Abonos (Pagos):")
    c.drawRightString(x_valor + 0.7*inch, y, f"${totales['abonos']:,.2f}")
    y -= 0.25 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label, y, "Saldo del Periodo:")
    c.drawRightString(x_valor + 0.7*inch, y, f"${totales['saldo']:,.2f}")

def generar_pdf_estado_cuenta(cliente_nombre, transacciones, totales, fechas, empresa_data, save_path):
    """Función principal para generar el PDF de Estado de Cuenta."""
    try:
        c = canvas.Canvas(save_path, pagesize=letter)
        
        _dibujar_encabezado(c, empresa_data)
        
        _dibujar_datos_estado_cuenta(c, cliente_nombre, fechas['ini'], fechas['fin'])

        y_tabla = 8.3 * inch
        y_final_tabla = _dibujar_tabla_estado_cuenta(c, transacciones, y_tabla)
        
        # Posicionar los totales un poco más abajo si la tabla es corta
        y_totales = min(y_final_tabla, 4.0 * inch)
        _dibujar_totales_estado_cuenta(c, totales, y_totales)
        
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF de Estado de Cuenta: {e}")
        import traceback
        traceback.print_exc()
        return False

def _dibujar_datos_estado_cuenta_proveedor(c, proveedor_nombre, fecha_ini, fecha_fin):
    """Dibuja los datos del proveedor y el rango de fechas."""
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, 9.0 * inch, "PROVEEDOR:")
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, 8.8 * inch, proveedor_nombre)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(7.5 * inch, 9.0 * inch, "ESTADO DE CUENTA DE PROVEEDOR")
    
    c.setFont("Helvetica", 11)
    c.drawRightString(7.5 * inch, 8.8 * inch, f"Del: {fecha_ini.strftime('%d/%m/%Y')}")
    c.drawRightString(7.5 * inch, 8.6 * inch, f"Al: {fecha_fin.strftime('%d/%m/%Y')}")

def _dibujar_totales_estado_cuenta_proveedor(c, totales, y_start):
    """Dibuja los totales del estado de cuenta del proveedor."""
    c.setFont("Helvetica-Bold", 11)
    x_label = 4.8 * inch
    x_valor = 7.4 * inch
    
    y = y_start - 0.2*inch
    c.line(x_label - 0.2*inch, y, 7.5*inch, y)
    y -= 0.2 * inch
    
    c.drawString(x_label, y, "Total Cargos (Notas Prov):")
    c.drawRightString(x_valor + 0.7*inch, y, f"${totales['cargos']:,.2f}")
    y -= 0.25 * inch

    c.drawString(x_label, y, "Total Abonos (Pagos Realizados):")
    c.drawRightString(x_valor + 0.7*inch, y, f"${totales['abonos']:,.2f}")
    y -= 0.25 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label, y, "Saldo por Pagar del Periodo:")
    c.drawRightString(x_valor + 0.7*inch, y, f"${totales['saldo']:,.2f}")

def generar_pdf_estado_cuenta_proveedor(proveedor_nombre, transacciones, totales, fechas, empresa_data, save_path):
    """Función principal para generar el PDF de Estado de Cuenta de Proveedor."""
    try:
        c = canvas.Canvas(save_path, pagesize=letter)
        
        _dibujar_encabezado(c, empresa_data)
        
        _dibujar_datos_estado_cuenta_proveedor(c, proveedor_nombre, fechas['ini'], fechas['fin'])

        # Reutilizamos la función de la tabla de clientes, ya que es idéntica
        y_tabla = 8.3 * inch
        y_final_tabla = _dibujar_tabla_estado_cuenta(c, transacciones, y_tabla)
        
        y_totales = min(y_final_tabla, 4.0 * inch)
        _dibujar_totales_estado_cuenta_proveedor(c, totales, y_totales)
        
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF de Estado de Cuenta Proveedor: {e}")
        import traceback
        traceback.print_exc()
        return False

def _dibujar_datos_orden_compra(c, proveedor_nombre):
    """Dibuja los datos del proveedor para la Orden de Compra."""
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, 9.0 * inch, "PROVEEDOR:")
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, 8.8 * inch, proveedor_nombre)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(7.5 * inch, 9.0 * inch, "ORDEN DE COMPRA")
    
    c.setFont("Helvetica", 11)
    c.drawRightString(7.5 * inch, 8.8 * inch, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

def _dibujar_tabla_items_orden_compra(c, items, y_start):
    """Dibuja la tabla de conceptos para la Orden de Compra."""
    c.setFont("Helvetica-Bold", 10)
    x_cant = 1.1 * inch
    x_cod = 1.8 * inch
    x_desc = 3.0 * inch
    x_precio = 5.5 * inch
    x_importe = 6.5 * inch
    
    c.drawString(x_cant, y_start, "Cant.")
    c.drawString(x_cod, y_start, "Código")
    c.drawString(x_desc, y_start, "Descripción")
    c.drawRightString(x_precio + 0.7*inch, y_start, "P. Compra")
    c.drawRightString(x_importe + 0.7*inch, y_start, "Importe")
    c.line(x_cant - 0.1*inch, y_start - 0.1*inch, 7.5*inch, y_start - 0.1*inch)
    
    c.setFont("Helvetica", 9)
    y = y_start - 0.3 * inch
    
    for item in items:
        c.drawString(x_cant, y, str(item['cantidad_a_pedir']))
        c.drawString(x_cod, y, item['codigo'])
        c.drawString(x_desc, y, item['nombre'][:40]) # Limitar descripción
        c.drawRightString(x_precio + 0.7*inch, y, f"${item['precio_compra']:,.2f}")
        c.drawRightString(x_importe + 0.7*inch, y, f"${item['importe']:,.2f}")
        y -= 0.25 * inch
    
    return y 

def _dibujar_totales_orden_compra(c, totales, y_start):
    """Dibuja el subtotal, impuestos y total de la Orden de Compra."""
    c.setFont("Helvetica-Bold", 11)
    x_label = 5.5 * inch
    x_valor = 6.5 * inch
    
    y = y_start - 0.2*inch
    c.line(x_label - 0.2*inch, y, 7.5*inch, y)
    y -= 0.2 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label, y, "TOTAL:")
    c.drawRightString(x_valor + 0.7*inch, y, f"${totales['total']:,.2f}")

def generar_pdf_orden_compra(proveedor_nombre, items_pedido, totales, empresa_data, save_path):
    """Función principal para generar el PDF de Orden de Compra."""
    try:
        c = canvas.Canvas(save_path, pagesize=letter)
        
        _dibujar_encabezado(c, empresa_data)
        
        _dibujar_datos_orden_compra(c, proveedor_nombre)

        y_tabla = 8.0 * inch
        y_final_tabla = _dibujar_tabla_items_orden_compra(c, items_pedido, y_tabla)
        
        _dibujar_totales_orden_compra(c, totales, y_final_tabla)
        
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF de Orden de Compra: {e}")
        import traceback
        traceback.print_exc()
        return False

def _header_footer_reporte(canvas, doc, empresa_data, titulo_reporte, fechas_str):
    """Dibuja el encabezado y pie de página en CADA página del reporte."""
    canvas.saveState()
    width, height = letter
    
    # --- Encabezado ---
    # Reutilizamos la función de encabezado estándar
    _dibujar_encabezado(canvas, empresa_data)
    
    # --- Título del Reporte ---
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(width / 2.0, 8.8 * inch, titulo_reporte)
    
    if fechas_str:
        canvas.setFont("Helvetica", 11)
        canvas.drawCentredString(width / 2.0, 8.6 * inch, fechas_str)

    # --- Pie de Página ---
    fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(1 * inch, 0.75 * inch, f"Generado: {fecha_gen}")
    canvas.drawRightString(width - 1 * inch, 0.75 * inch, f"Página {canvas.getPageNumber()}")
    
    canvas.restoreState()

def generar_pdf_reporte(titulo_reporte, fecha_ini_str, fecha_fin_str, headers, data, empresa_data, save_path, fechas_habilitadas=True):
    """
    Función principal para generar el PDF de un Reporte (con Platypus).
    """
    try:
        # 1. Crear el documento con márgenes
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=0.75*inch, rightMargin=0.75*inch,
                                topMargin=2.8*inch, bottomMargin=1*inch) # Margen superior amplio para header
        
        story = []
        
        # 2. Definir Estilos de Párrafo
        styles = getSampleStyleSheet()
        
        # Estilo para el cuerpo de la tabla (con wrapping)
        style_body = styles['BodyText']
        style_body.fontSize = 9
        style_body.alignment = TA_LEFT # Default a la izquierda
        
        # Estilo para los encabezados de la tabla
        style_header = styles['Normal']
        style_header.fontName = 'Helvetica-Bold'
        style_header.fontSize = 10
        style_header.textColor = colors.whitesmoke
        style_header.alignment = TA_CENTER

        # 3. Convertir datos (strings) a Paragraphs
        
        # Encabezados
        wrapped_headers = [Paragraph(h, style_header) for h in headers]
        
        # Datos
        wrapped_data = []
        for row in data:
            wrapped_row = [Paragraph(cell, style_body) for cell in row]
            wrapped_data.append(wrapped_row)
            
        table_data = [wrapped_headers] + wrapped_data
        # --- FIN DE CORRECCIÓN (Problema 3) ---
        
        # 4. Calcular anchos de columna (distribución equitativa)
        num_cols = len(headers)
        ancho_disponible = doc.width # Ancho usable (total - márgenes)
        col_widths = [ancho_disponible / num_cols] * num_cols
        
        # 5. Definir Estilo de Tabla
        ts = TableStyle([
            # Encabezado
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#00788E")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinear verticalmente
            
            # Cuerpo
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('ALIGN', (0,1), (-1,-1), 'LEFT'), # Default: Alinear párrafos a la izquierda
            
            # Rejilla
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#00788E")),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
        ])
        
        # 6. Ajustar alineación para columnas que parezcan números o moneda
        # Esto sobrescribe el 'ALIGN' default para columnas específicas
        for col_idx, header in enumerate(headers):
            header_lower = header.lower()
            # Si el header contiene estas palabras, alinea la columna a la derecha
            if any(s in header_lower for s in ['total', 'monto', 'saldo', 'precio', 'cant', 'stock', 'id', 'vendido', 'notas', 'folio', 'fecha']):
                ts.add('ALIGN', (col_idx, 1), (col_idx, -1), 'RIGHT')

        # 7. Crear objeto Tabla y aplicar estilo
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(ts)
        
        story.append(t)
        
        # 8. Construir PDF
        
        # Definir el string de fechas que se pasará al encabezado
        if fechas_habilitadas:
            fechas_str = f"Periodo del {fecha_ini_str} al {fecha_fin_str}"
        else:
            fechas_str = "Reporte General (Sin filtro de fecha)"
        
        header_footer_func = partial(
            _header_footer_reporte, 
            empresa_data=empresa_data, 
            titulo_reporte=titulo_reporte,
            fechas_str=fechas_str
        )
        
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
        
    except Exception as e:
        print(f"Error al generar PDF de Reporte: {e}")
        import traceback
        traceback.print_exc()
        return False