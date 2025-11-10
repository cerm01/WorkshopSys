import io
import sys
import subprocess
import os
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth 
from reportlab.lib.utils import ImageReader 

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow no está instalado. pip install Pillow")
    Image = None

from PyQt5.QtWidgets import QFileDialog, QMessageBox
# QDate ya no es necesario aquí si usamos datetime
# from PyQt5.QtCore import QDate 


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