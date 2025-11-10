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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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

    ciudad = empresa_data.get('ciudad', '')
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

# --- FUNCIÓN DE HEADER/FOOTER PARA NOTAS, COTIZACIONES, NOTA PROV ---
def _header_footer_platypus(canvas, doc, empresa_data, titulo_doc, datos_doc):
    """
    Dibuja el encabezado y pie de página en CADA página para documentos
    generados con SimpleDocTemplate (Platypus).
    """
    canvas.saveState()
    width, height = letter
    
    # --- 1. Encabezado de la Empresa ---
    _dibujar_encabezado(canvas, empresa_data)
    
    # --- 2. Título del Documento y Datos del Cliente/Proveedor ---
    y_top_doc = 9.0 * inch
    
    # Cliente o Proveedor
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(1 * inch, y_top_doc, datos_doc.get('titulo_entidad', 'CLIENTE:'))
    canvas.setFont("Helvetica", 11)
    canvas.drawString(1 * inch, y_top_doc - 0.2*inch, datos_doc.get('nombre_entidad', ''))
    
    # Datos extra (ej. Proyecto en Cotización)
    if extra := datos_doc.get('linea_extra'):
         canvas.drawString(1 * inch, y_top_doc - 0.4*inch, extra)

    # Folio y Fechas
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawRightString(7.5 * inch, y_top_doc, f"{titulo_doc}: {datos_doc.get('folio', '')}")
    
    canvas.setFont("Helvetica", 11)
    canvas.drawRightString(7.5 * inch, y_top_doc - 0.2*inch, f"Fecha: {datos_doc.get('fecha', '')}")
    
    # Línea extra 1 (ej. Estado o Vigencia)
    if extra1 := datos_doc.get('extra_derecha_1'):
        canvas.drawRightString(7.5 * inch, y_top_doc - 0.4*inch, extra1)

    # Línea extra 2 (ej. Estado)
    if extra2 := datos_doc.get('extra_derecha_2'):
        canvas.drawRightString(7.5 * inch, y_top_doc - 0.6*inch, extra2)

    # --- 3. Pie de Página ---
    fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(1 * inch, 0.75 * inch, f"Generado: {fecha_gen}")
    canvas.drawRightString(width - 1 * inch, 0.75 * inch, f"Página {canvas.getPageNumber()}")
    
    canvas.restoreState()

# --- FUNCIÓN GENERAR_PDF_NOTA_VENTA ---
def generar_pdf_nota_venta(nota_data, empresa_data, save_path):
    """
    Función principal para generar el PDF de una Nota de Venta.
    """
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=1*inch, rightMargin=1*inch,
                                topMargin=3.0*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Estilos ---
        style_body = styles['BodyText']
        style_body.fontSize = 9
        style_body.alignment = TA_LEFT 
        
        style_body_right = ParagraphStyle(name='BodyRight', parent=style_body, alignment=TA_RIGHT)
        
        style_header_base = ParagraphStyle(name='HeaderBase', parent=styles['Normal'],
                                      fontName='Helvetica-Bold', fontSize=10,
                                      textColor=colors.black) 
        style_header_left = ParagraphStyle(name='HeaderLeft', parent=style_header_base, alignment=TA_LEFT)
        style_header_right = ParagraphStyle(name='HeaderRight', parent=style_header_base, alignment=TA_RIGHT)
                                      
        style_total_label = ParagraphStyle(name='TotalLabel', parent=style_body,
                                           alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=11)
        style_total_value = ParagraphStyle(name='TotalValue', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=11)
        style_grand_total = ParagraphStyle(name='GrandTotal', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=12,
                                           textColor=colors.HexColor("#00788E"))

        # --- 1. Tabla de Items ---
        table_data = []
        wrapped_headers = [
            Paragraph("Cant.", style_header_left),
            Paragraph("Descripción", style_header_left),
            Paragraph("P. Unitario", style_header_right),
            Paragraph("IVA %", style_header_right),
            Paragraph("Importe", style_header_right)
        ]
        table_data.append(wrapped_headers)

        items = nota_data.get('items', [])
        for item in items:
            
            cant = str(item['cantidad'])
            desc = Paragraph(item['descripcion'], style_body) 
            precio = f"${item['precio_unitario']:,.2f}"
            iva = f"{item['impuesto']:.1f} %"
            importe = f"${item['importe']:,.2f}" 
            
            wrapped_row = [
                Paragraph(cant, style_body), 
                desc, 
                Paragraph(precio, style_body_right), 
                Paragraph(iva, style_body_right), 
                Paragraph(importe, style_body_right)
            ]
            table_data.append(wrapped_row)
        
        col_widths = [0.6*inch, 3.1*inch, 1*inch, 0.7*inch, 1.1*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1) 

        ts_items = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Estilo de la imagen
            ('LINEABOVE', (0,0), (-1,0), 1.5, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black), 
            
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            
            # Alineación de datos
            ('ALIGN', (0,1), (0,-1), 'LEFT'), 
            ('ALIGN', (1,1), (1,-1), 'LEFT'), 
            ('ALIGN', (2,1), (2,-1), 'RIGHT'), 
            ('ALIGN', (3,1), (3,-1), 'RIGHT'), 
            ('ALIGN', (4,1), (4,-1), 'RIGHT'), 
        ])
        
        items_table.setStyle(ts_items)
        story.append(items_table)
        
        # --- 2. Tabla de Totales ---
        story.append(Spacer(1, 0.2*inch))
        
        subtotal = nota_data.get('subtotal', 0)
        impuestos = nota_data.get('impuestos', 0)
        total = nota_data.get('total', 0)
        total_pagado = nota_data.get('total_pagado', 0)
        saldo = nota_data.get('saldo', 0)

        totals_data = [
            ['', Paragraph('Subtotal:', style_total_label), Paragraph(f'${subtotal:,.2f}', style_total_value)],
            ['', Paragraph('Impuestos:', style_total_label), Paragraph(f'${impuestos:,.2f}', style_total_value)],
            ['', Paragraph('TOTAL:', style_total_label), Paragraph(f'${total:,.2f}', style_grand_total)],
            ['', Paragraph('Total Pagado:', style_total_label), Paragraph(f'${total_pagado:,.2f}', style_total_value)],
            ['', Paragraph('Saldo Pendiente:', style_total_label), Paragraph(f'${saldo:,.2f}', style_grand_total)],
        ]
        
        totals_table = Table(totals_data, colWidths=[4.4*inch, 1.0*inch, 1.1*inch])
        totals_table.setStyle(TableStyle([
            ('LINEABOVE', (1,2), (2,2), 1, colors.HexColor("#00788E")),
            ('TOPPADDING', (0,2), (-1,-1), 4), 
        ]))
        story.append(totals_table)

        # --- 3. Preparar datos para el Header/Footer ---
        fecha_str = nota_data.get('fecha', '')
        fecha_formateada = fecha_str
        if fecha_str:
            try:
                fecha_dt = datetime.fromisoformat(fecha_str) 
                fecha_formateada = fecha_dt.strftime("%d/%m/%Y") 
            except ValueError:
                fecha_formateada = fecha_str.split('T')[0]
        
        datos_doc = {
            'titulo_entidad': 'CLIENTE:',
            'nombre_entidad': nota_data.get('cliente_nombre', ''),
            'folio': nota_data.get('folio', ''),
            'fecha': fecha_formateada,
            'extra_derecha_1': f"Estado: {nota_data.get('estado', '')}", 
            'linea_extra': nota_data.get('observaciones', '') 
        }

        header_footer_func = partial(
            _header_footer_platypus, 
            empresa_data=empresa_data, 
            titulo_doc="NOTA DE VENTA",
            datos_doc=datos_doc
        )
        
        # --- 4. Construir PDF ---
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
    except Exception as e:
        print(f"Error al generar PDF (Platypus): {e}")
        import traceback
        traceback.print_exc()
        return False

# --- FUNCIÓN GENERAR_PDF_COTIZACION ---
def generar_pdf_cotizacion(cotizacion_data, empresa_data, save_path):
    """
    Función principal para generar el PDF de una Cotización.
    (Versión actualizada con Platypus para soportar saltos de página)
    """
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=1*inch, rightMargin=1*inch,
                                topMargin=3.0*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Estilos ---
        style_body = styles['BodyText']
        style_body.fontSize = 9
        style_body.alignment = TA_LEFT 
        
        style_body_right = ParagraphStyle(name='BodyRight', parent=style_body, alignment=TA_RIGHT)
        
        style_header_base = ParagraphStyle(name='HeaderBase', parent=styles['Normal'],
                                      fontName='Helvetica-Bold', fontSize=10,
                                      textColor=colors.black) 
        style_header_left = ParagraphStyle(name='HeaderLeft', parent=style_header_base, alignment=TA_LEFT)
        style_header_right = ParagraphStyle(name='HeaderRight', parent=style_header_base, alignment=TA_RIGHT)
                                      
        style_total_label = ParagraphStyle(name='TotalLabel', parent=style_body,
                                           alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=11)
        style_total_value = ParagraphStyle(name='TotalValue', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=11)
        style_grand_total = ParagraphStyle(name='GrandTotal', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=12,
                                           textColor=colors.HexColor("#00788E"))
        
        style_seccion = ParagraphStyle(name='Seccion', parent=styles['Normal'],
                                       fontName='Helvetica-Bold', fontSize=10,
                                       textColor=colors.HexColor("#00788E"),
                                       alignment=TA_LEFT, spaceBefore=6, spaceAfter=2)
        
        style_nota = ParagraphStyle(name='Nota', parent=styles['Italic'],
                                    fontSize=9, textColor=colors.HexColor("#333333"),
                                    alignment=TA_LEFT)
        
        style_condiciones = ParagraphStyle(name='Condiciones', parent=styles['Normal'],
                                           fontSize=8, textColor=colors.HexColor("#333333"),
                                           alignment=TA_LEFT, spaceBefore=6)

        # --- 1. Tabla de Items ---
        table_data = []
        wrapped_headers = [
            Paragraph("Cant.", style_header_left),
            Paragraph("Descripción", style_header_left),
            Paragraph("P. Unitario", style_header_right),
            Paragraph("IVA %", style_header_right),
            Paragraph("Importe", style_header_right)
        ]
        table_data.append(wrapped_headers)

        items = cotizacion_data.get('items', [])
        
        for item in items:
            tipo = item.get('tipo', 'normal')
            
            if tipo == 'normal':
                cant = str(item['cantidad'])
                desc = Paragraph(item['descripcion'], style_body)
                precio = f"${item['precio_unitario']:,.2f}"
                iva = f"{item['impuesto']:.1f} %"
                importe = f"${item['importe']:,.2f}"
                
                wrapped_row = [
                    Paragraph(cant, style_body), 
                    desc, 
                    Paragraph(precio, style_body_right), 
                    Paragraph(iva, style_body_right), 
                    Paragraph(importe, style_body_right)
                ]
                table_data.append(wrapped_row)
            
            else:
                descripcion = item['descripcion']
                if tipo == 'seccion':
                    p = Paragraph(descripcion, style_seccion)
                elif tipo == 'nota':
                    p = Paragraph(descripcion, style_nota)
                elif tipo == 'condiciones':
                    p = Paragraph(descripcion.replace('\n', '<br/>'), style_condiciones)
                else:
                    p = Paragraph(descripcion, style_body)

                table_data.append([p, '', '', '', ''])
                
        
        col_widths = [0.6*inch, 3.1*inch, 1*inch, 0.7*inch, 1.1*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        ts_items = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Estilo de la imagen
            ('LINEABOVE', (0,0), (-1,0), 1.5, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black), 

            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),

            # Alineación de datos
            ('ALIGN', (2,1), (2,-1), 'RIGHT'), 
            ('ALIGN', (3,1), (3,-1), 'RIGHT'), 
            ('ALIGN', (4,1), (4,-1), 'RIGHT'), 
        ])

        # Aplicar estilos de fila
        for i, item in enumerate(items, 1): 
            tipo = item.get('tipo', 'normal')
            if tipo == 'normal':
                ts_items.add('TOPPADDING', (0,i), (-1,i), 4)
                ts_items.add('BOTTOMPADDING', (0,i), (-1,i), 4)
                ts_items.add('VALIGN', (0,i), (-1,i), 'MIDDLE')
            else:
                ts_items.add('SPAN', (0,i), (4,i))
                ts_items.add('TOPPADDING', (0,i), (0,i), 6)
                ts_items.add('BOTTOMPADDING', (0,i), (0,i), 6)
                
                if tipo == 'seccion':
                    ts_items.add('BACKGROUND', (0,i), (0,i), colors.HexColor("#E0F7FA"))
                elif tipo == 'nota':
                    ts_items.add('BACKGROUND', (0,i), (0,i), colors.HexColor("#F5F5F5"))
                elif tipo == 'condiciones':
                    ts_items.add('BACKGROUND', (0,i), (0,i), colors.HexColor("#FFFBEA"))

        items_table.setStyle(ts_items)
        story.append(items_table)
        
        # --- 2. Tabla de Totales ---
        story.append(Spacer(1, 0.2*inch))
        
        subtotal = cotizacion_data.get('subtotal', 0)
        impuestos = cotizacion_data.get('impuestos', 0)
        total = cotizacion_data.get('total', 0)

        totals_data = [
            ['', Paragraph('Subtotal:', style_total_label), Paragraph(f'${subtotal:,.2f}', style_total_value)],
            ['', Paragraph('Impuestos:', style_total_label), Paragraph(f'${impuestos:,.2f}', style_total_value)],
            ['', Paragraph('TOTAL:', style_total_label), Paragraph(f'${total:,.2f}', style_grand_total)],
        ]
        
        totals_table = Table(totals_data, colWidths=[4.4*inch, 1.0*inch, 1.1*inch])
        totals_table.setStyle(TableStyle([
            ('LINEABOVE', (1,2), (2,2), 1, colors.HexColor("#00788E")),
            ('TOPPADDING', (0,2), (-1,2), 4),
        ]))
        story.append(totals_table)

        # --- 3. Preparar datos para el Header/Footer ---
        fecha_str = cotizacion_data.get('fecha', '')
        fecha_formateada = fecha_str
        if fecha_str:
            try:
                fecha_dt = datetime.fromisoformat(fecha_str) 
                fecha_formateada = fecha_dt.strftime("%d/%m/%Y") 
            except ValueError:
                fecha_formateada = fecha_str.split('T')[0]
        
        datos_doc = {
            'titulo_entidad': 'CLIENTE:',
            'nombre_entidad': cotizacion_data.get('cliente_nombre', ''),
            'folio': cotizacion_data.get('folio', ''),
            'fecha': fecha_formateada,
            'extra_derecha_1': f"Vigencia: {cotizacion_data.get('vigencia', '')}",
            'extra_derecha_2': f"Estado: {cotizacion_data.get('estado', '')}",
            'linea_extra': f"Proyecto: {cotizacion_data.get('observaciones', '')}"
        }

        header_footer_func = partial(
            _header_footer_platypus, 
            empresa_data=empresa_data, 
            titulo_doc="COTIZACIÓN",
            datos_doc=datos_doc
        )
        
        # --- 4. Construir PDF ---
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
    except Exception as e:
        print(f"Error al generar PDF de Cotización (Platypus): {e}")
        import traceback
        traceback.print_exc()
        return False

# --- FUNCIÓN! HEADER/FOOTER PARA ÓRDENES ---
def _header_footer_orden_trabajo(canvas, doc, empresa_data, orden_data):
    """
    Dibuja el encabezado y pie de página específico para Órdenes de Trabajo,
    incluyendo los datos del vehículo.
    """
    canvas.saveState()
    width, height = letter
    
    # --- 1. Encabezado de la Empresa ---
    _dibujar_encabezado(canvas, empresa_data)
    
    # --- 2. Datos de la Orden (Cliente, Folio, Vehículo) ---
    
    # --- Cliente ---
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(1 * inch, 9.0 * inch, "CLIENTE:")
    canvas.setFont("Helvetica", 11)
    canvas.drawString(1 * inch, 8.8 * inch, orden_data.get('cliente_nombre', ''))

    # --- Folio y Fechas ---
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawRightString(7.5 * inch, 9.0 * inch, f"ORDEN DE TRABAJO: {orden_data.get('folio', '')}")
    
    fecha_str = orden_data.get('fecha_recepcion', '')
    fecha_formateada = fecha_str
    if fecha_str:
        try:
            fecha_dt = datetime.fromisoformat(fecha_str) 
            fecha_formateada = fecha_dt.strftime("%d/%m/%Y %H:%M") 
        except ValueError:
            fecha_formateada = fecha_str.split('T')[0]

    canvas.setFont("Helvetica", 11)
    canvas.drawRightString(7.5 * inch, 8.8 * inch, f"Fecha Recepción: {fecha_formateada}")
    canvas.drawRightString(7.5 * inch, 8.6 * inch, f"Estado: {orden_data.get('estado', '')}")
    
    # --- Datos del Vehículo ---
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(1 * inch, 8.3 * inch, "VEHÍCULO:") 
    canvas.setFont("Helvetica", 10)
    
    y_vehiculo = 8.1 * inch 
    
    canvas.drawString(1.1 * inch, y_vehiculo, f"Marca: {orden_data.get('vehiculo_marca', '')}")
    canvas.drawString(3.5 * inch, y_vehiculo, f"Modelo: {orden_data.get('vehiculo_modelo', '')}")
    canvas.drawString(1.1 * inch, y_vehiculo - 0.2*inch, f"Año: {orden_data.get('vehiculo_ano', '')}")
    canvas.drawString(3.5 * inch, y_vehiculo - 0.2*inch, f"Placas: {orden_data.get('vehiculo_placas', '')}")

    # --- 3. Pie de Página ---
    fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(1 * inch, 0.75 * inch, f"Generado: {fecha_gen}")
    canvas.drawRightString(width - 1 * inch, 0.75 * inch, f"Página {canvas.getPageNumber()}")
    
    canvas.restoreState()


# --- FUNCIÓN GENERAR_PDF_ORDEN_TRABAJO ---
def generar_pdf_orden_trabajo(orden_data, empresa_data, save_path):
    """
    Función principal para generar el PDF de una Orden de Trabajo.
    (Versión actualizada con Platypus para soportar saltos de página)
    """
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=1*inch, rightMargin=1*inch,
                                topMargin=3.4*inch, bottomMargin=1*inch) # Margen superior más grande
        
        story = []
        styles = getSampleStyleSheet()

        # --- Estilos ---
        style_body = styles['BodyText']
        style_body.fontSize = 9
        style_body.alignment = TA_LEFT
        
        style_header_base = ParagraphStyle(name='HeaderBase', parent=styles['Normal'],
                                      fontName='Helvetica-Bold', fontSize=10,
                                      textColor=colors.black) 
        style_header_left = ParagraphStyle(name='HeaderLeft', parent=style_header_base, alignment=TA_LEFT)

        # --- 1. Tabla de Items (Solo Cantidad y Descripción) ---
        table_data = []
        wrapped_headers = [
            Paragraph("Cant.", style_header_left),
            Paragraph("Descripción del Servicio / Observaciones", style_header_left),
        ]
        table_data.append(wrapped_headers)

        items = orden_data.get('items', [])
        for item in items:
            if item.get('tipo', 'normal') != 'normal': 
                continue
                
            cant = str(item['cantidad'])
            desc = Paragraph(item['descripcion'], style_body) # Permite wrapping
            
            wrapped_row = [
                Paragraph(cant, style_body), 
                desc
            ]
            table_data.append(wrapped_row)
        
        # Ancho de columnas (total 6.5 pulgadas)
        col_widths = [0.6*inch, 5.9*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Estilo de tabla (como la imagen)
        ts_items = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Estilo de la imagen
            ('LINEABOVE', (0,0), (-1,0), 1.5, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black), 
            
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            
            ('ALIGN', (0,1), (0,-1), 'LEFT'), 
            ('ALIGN', (1,1), (1,-1), 'LEFT'), 
        ])
        
        items_table.setStyle(ts_items)
        story.append(items_table)
        
        # --- 2. Preparar datos para el Header/Footer ---
        header_footer_func = partial(
            _header_footer_orden_trabajo, 
            empresa_data=empresa_data, 
            orden_data=orden_data
        )
        
        # --- 3. Construir PDF ---
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
    except Exception as e:
        print(f"Error al generar PDF de Orden (Platypus): {e}")
        import traceback
        traceback.print_exc()
        return False
    
# --- Nota Proveedor ---
def generar_pdf_nota_proveedor(nota_data, empresa_data, save_path):
    """
    Función principal para generar el PDF de una Nota de Proveedor.
    (Versión actualizada con Platypus para soportar saltos de página)
    """
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=1*inch, rightMargin=1*inch,
                                topMargin=3.0*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Estilos ---
        style_body = styles['BodyText']
        style_body.fontSize = 9
        style_body.alignment = TA_LEFT 
        
        style_body_right = ParagraphStyle(name='BodyRight', parent=style_body, alignment=TA_RIGHT)

        style_header_base = ParagraphStyle(name='HeaderBase', parent=styles['Normal'],
                                      fontName='Helvetica-Bold', fontSize=10,
                                      textColor=colors.black) 
        style_header_left = ParagraphStyle(name='HeaderLeft', parent=style_header_base, alignment=TA_LEFT)
        style_header_right = ParagraphStyle(name='HeaderRight', parent=style_header_base, alignment=TA_RIGHT)
                                      
        style_total_label = ParagraphStyle(name='TotalLabel', parent=style_body,
                                           alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=11)
        style_total_value = ParagraphStyle(name='TotalValue', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=11)
        style_grand_total = ParagraphStyle(name='GrandTotal', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=12,
                                           textColor=colors.HexColor("#00788E"))

        # --- 1. Tabla de Items ---
        table_data = []
        wrapped_headers = [
            Paragraph("Cant.", style_header_left),
            Paragraph("Descripción", style_header_left),
            Paragraph("P. Unitario", style_header_right),
            Paragraph("IVA %", style_header_right),
            Paragraph("Importe", style_header_right)
        ]
        table_data.append(wrapped_headers)

        items = nota_data.get('items', [])
        for item in items:
            cant = str(item['cantidad'])
            desc = Paragraph(item['descripcion'], style_body) 
            precio = f"${item['precio_unitario']:,.2f}"
            iva = f"{item['impuesto']:.1f} %"
            importe = f"${item['importe']:,.2f}"
            
            wrapped_row = [
                Paragraph(cant, style_body), 
                desc, 
                Paragraph(precio, style_body_right), 
                Paragraph(iva, style_body_right), 
                Paragraph(importe, style_body_right)
            ]
            table_data.append(wrapped_row)
        
        col_widths = [0.6*inch, 3.1*inch, 1*inch, 0.7*inch, 1.1*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        ts_items = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Estilo de la imagen
            ('LINEABOVE', (0,0), (-1,0), 1.5, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black), 

            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            
            # Alineación de datos
            ('ALIGN', (0,1), (0,-1), 'LEFT'), 
            ('ALIGN', (1,1), (1,-1), 'LEFT'), 
            ('ALIGN', (2,1), (2,-1), 'RIGHT'), 
            ('ALIGN', (3,1), (3,-1), 'RIGHT'), 
            ('ALIGN', (4,1), (4,-1), 'RIGHT'), 
        ])
        
        items_table.setStyle(ts_items)
        story.append(items_table)
        
        # --- 2. Tabla de Totales ---
        story.append(Spacer(1, 0.2*inch))
        
        subtotal = nota_data.get('subtotal', 0)
        impuestos = nota_data.get('impuestos', 0)
        total = nota_data.get('total', 0)
        total_pagado = nota_data.get('total_pagado', 0)
        saldo = nota_data.get('saldo', 0)

        totals_data = [
            ['', Paragraph('Subtotal:', style_total_label), Paragraph(f'${subtotal:,.2f}', style_total_value)],
            ['', Paragraph('Impuestos:', style_total_label), Paragraph(f'${impuestos:,.2f}', style_total_value)],
            ['', Paragraph('TOTAL:', style_total_label), Paragraph(f'${total:,.2f}', style_grand_total)],
            ['', Paragraph('Total Pagado:', style_total_label), Paragraph(f'${total_pagado:,.2f}', style_total_value)],
            ['', Paragraph('Saldo Pendiente:', style_total_label), Paragraph(f'${saldo:,.2f}', style_grand_total)],
        ]
        
        totals_table = Table(totals_data, colWidths=[4.4*inch, 1.0*inch, 1.1*inch])
        totals_table.setStyle(TableStyle([
            ('LINEABOVE', (1,2), (2,2), 1, colors.HexColor("#00788E")),
            ('TOPPADDING', (0,2), (-1,-1), 4),
        ]))
        story.append(totals_table)

        # --- 3. Preparar datos para el Header/Footer ---
        fecha_str = nota_data.get('fecha', '')
        fecha_formateada = fecha_str
        if fecha_str:
            try:
                fecha_dt = datetime.fromisoformat(fecha_str) 
                fecha_formateada = fecha_dt.strftime("%d/%m/%Y") 
            except ValueError:
                fecha_formateada = fecha_str.split('T')[0]
        
        datos_doc = {
            'titulo_entidad': 'PROVEEDOR:',
            'nombre_entidad': nota_data.get('proveedor_nombre', ''),
            'folio': nota_data.get('folio', ''),
            'fecha': fecha_formateada,
            'extra_derecha_1': f"Estado: {nota_data.get('estado', '')}",
            'linea_extra': f"Referencia: {nota_data.get('observaciones', '')}"
        }

        header_footer_func = partial(
            _header_footer_platypus, 
            empresa_data=empresa_data, 
            titulo_doc="NOTA PROVEEDOR",
            datos_doc=datos_doc
        )
        
        # --- 4. Construir PDF ---
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
    except Exception as e:
        print(f"Error al generar PDF de Nota Proveedor (Platypus): {e}")
        import traceback
        traceback.print_exc()
        return False
    
# --- Estado de Cuenta Cliente (REESCRITA CON PLATYPUS) ---

def generar_pdf_estado_cuenta(cliente_nombre, transacciones, totales, fechas, empresa_data, save_path):
    """
    Función principal para generar el PDF de Estado de Cuenta de Cliente.
    (Versión actualizada con Platypus para soportar saltos de página)
    """
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=1*inch, rightMargin=1*inch,
                                topMargin=3.0*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Estilos ---
        style_body = styles['BodyText']
        style_body.fontSize = 8 # Letra más pequeña para E.C.
        style_body.alignment = TA_LEFT 
        
        style_body_right = ParagraphStyle(name='BodyRight', parent=style_body, alignment=TA_RIGHT)
        
        style_header_base = ParagraphStyle(name='HeaderBase', parent=styles['Normal'],
                                      fontName='Helvetica-Bold', fontSize=9,
                                      textColor=colors.black) 
        style_header_left = ParagraphStyle(name='HeaderLeft', parent=style_header_base, alignment=TA_LEFT)
        style_header_right = ParagraphStyle(name='HeaderRight', parent=style_header_base, alignment=TA_RIGHT)
                                      
        style_total_label = ParagraphStyle(name='TotalLabel', parent=style_body,
                                           alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=11)
        style_total_value = ParagraphStyle(name='TotalValue', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=11)
        style_grand_total = ParagraphStyle(name='GrandTotal', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=12,
                                           textColor=colors.HexColor("#D32F2F")) # Saldo deudor en rojo

        # --- 1. Tabla de Transacciones ---
        table_data = []
        wrapped_headers = [
            Paragraph("Fecha", style_header_left),
            Paragraph("Documento", style_header_left),
            Paragraph("Concepto", style_header_left),
            Paragraph("Cargo", style_header_right),
            Paragraph("Abono", style_header_right),
            Paragraph("Balance", style_header_right)
        ]
        table_data.append(wrapped_headers)

        balance_actual = 0.0
        for trx in transacciones:
            cargo = trx.get('cargo', 0)
            abono = trx.get('abono', 0)
            balance_actual += (cargo - abono)
            
            fecha_str = trx['fecha'].strftime("%d/%m/%Y")
            doc_str = trx['documento']
            conc_str = Paragraph(trx.get('concepto', '')[:40], style_body) # Acortar y wrappear
            cargo_str = f"${cargo:,.2f}" if cargo > 0 else ""
            abono_str = f"${abono:,.2f}" if abono > 0 else ""
            bal_str = f"${balance_actual:,.2f}"
            
            wrapped_row = [
                Paragraph(fecha_str, style_body), 
                Paragraph(doc_str, style_body), 
                conc_str, 
                Paragraph(cargo_str, style_body_right), 
                Paragraph(abono_str, style_body_right),
                Paragraph(bal_str, style_body_right)
            ]
            table_data.append(wrapped_row)
        
        col_widths = [0.8*inch, 1.0*inch, 2.0*inch, 0.9*inch, 0.9*inch, 0.9*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        ts_items = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEABOVE', (0,0), (-1,0), 1.5, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black), 
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            ('ALIGN', (0,1), (1,-1), 'LEFT'), 
            ('ALIGN', (3,1), (-1,-1), 'RIGHT'), 
        ])
        
        items_table.setStyle(ts_items)
        story.append(items_table)
        
        # --- 2. Tabla de Totales ---
        story.append(Spacer(1, 0.2*inch))

        # Si el saldo es <= 0 (a favor), ponerlo en verde
        if totales['saldo'] <= 0.01:
            style_grand_total.textColor = colors.HexColor("#006400")

        totals_data = [
            ['', Paragraph('Total Cargos (Notas):', style_total_label), Paragraph(f"${totales['cargos']:,.2f}", style_total_value)],
            ['', Paragraph('Total Abonos (Pagos):', style_total_label), Paragraph(f"${totales['abonos']:,.2f}", style_total_value)],
            ['', Paragraph('Saldo del Periodo:', style_total_label), Paragraph(f"${totales['saldo']:,.2f}", style_grand_total)],
        ]
        
        totals_table = Table(totals_data, colWidths=[3.2*inch, 1.6*inch, 1.7*inch])
        totals_table.setStyle(TableStyle([
            ('LINEABOVE', (1,2), (2,2), 1, colors.HexColor("#00788E")),
            ('TOPPADDING', (0,0), (-1,-1), 4), 
        ]))
        story.append(totals_table)

        # --- 3. Preparar datos para el Header/Footer ---
        datos_doc = {
            'titulo_entidad': 'CLIENTE:',
            'nombre_entidad': cliente_nombre,
            'folio': '', # No aplica folio
            'fecha': '', # No aplica fecha
            'extra_derecha_1': f"Del: {fechas['ini'].strftime('%d/%m/%Y')}",
            'extra_derecha_2': f"Al: {fechas['fin'].strftime('%d/%m/%Y')}",
        }

        header_footer_func = partial(
            _header_footer_platypus, 
            empresa_data=empresa_data, 
            titulo_doc="ESTADO DE CUENTA",
            datos_doc=datos_doc
        )
        
        # --- 4. Construir PDF ---
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
    except Exception as e:
        print(f"Error al generar PDF de Estado de Cuenta (Platypus): {e}")
        import traceback
        traceback.print_exc()
        return False

# --- Estado de Cuenta Proveedor (REESCRITA CON PLATYPUS) ---

def generar_pdf_estado_cuenta_proveedor(proveedor_nombre, transacciones, totales, fechas, empresa_data, save_path):
    """
    Función principal para generar el PDF de Estado de Cuenta de Proveedor.
    (Versión actualizada con Platypus para soportar saltos de página)
    """
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=1*inch, rightMargin=1*inch,
                                topMargin=3.0*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Estilos ---
        style_body = styles['BodyText']
        style_body.fontSize = 8
        style_body.alignment = TA_LEFT 
        
        style_body_right = ParagraphStyle(name='BodyRight', parent=style_body, alignment=TA_RIGHT)
        
        style_header_base = ParagraphStyle(name='HeaderBase', parent=styles['Normal'],
                                      fontName='Helvetica-Bold', fontSize=9,
                                      textColor=colors.black) 
        style_header_left = ParagraphStyle(name='HeaderLeft', parent=style_header_base, alignment=TA_LEFT)
        style_header_right = ParagraphStyle(name='HeaderRight', parent=style_header_base, alignment=TA_RIGHT)
                                      
        style_total_label = ParagraphStyle(name='TotalLabel', parent=style_body,
                                           alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=10) # Un poco más pequeño
        style_total_value = ParagraphStyle(name='TotalValue', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=10)
        style_grand_total = ParagraphStyle(name='GrandTotal', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=11,
                                           textColor=colors.HexColor("#D32F2F")) # Saldo deudor en rojo

        # --- 1. Tabla de Transacciones ---
        table_data = []
        wrapped_headers = [
            Paragraph("Fecha", style_header_left),
            Paragraph("Documento", style_header_left),
            Paragraph("Concepto", style_header_left),
            Paragraph("Cargo", style_header_right),
            Paragraph("Abono", style_header_right),
            Paragraph("Balance", style_header_right)
        ]
        table_data.append(wrapped_headers)

        balance_actual = 0.0
        for trx in transacciones:
            cargo = trx.get('cargo', 0)
            abono = trx.get('abono', 0)
            balance_actual += (cargo - abono)
            
            fecha_str = trx['fecha'].strftime("%d/%m/%Y")
            doc_str = trx['documento']
            conc_str = Paragraph(trx.get('concepto', '')[:40], style_body) # Acortar y wrappear
            cargo_str = f"${cargo:,.2f}" if cargo > 0 else ""
            abono_str = f"${abono:,.2f}" if abono > 0 else ""
            bal_str = f"${balance_actual:,.2f}"
            
            wrapped_row = [
                Paragraph(fecha_str, style_body), 
                Paragraph(doc_str, style_body), 
                conc_str, 
                Paragraph(cargo_str, style_body_right), 
                Paragraph(abono_str, style_body_right),
                Paragraph(bal_str, style_body_right)
            ]
            table_data.append(wrapped_row)
        
        col_widths = [0.8*inch, 1.0*inch, 2.0*inch, 0.9*inch, 0.9*inch, 0.9*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        ts_items = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEABOVE', (0,0), (-1,0), 1.5, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black), 
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            ('ALIGN', (0,1), (1,-1), 'LEFT'), 
            ('ALIGN', (3,1), (-1,-1), 'RIGHT'), 
        ])
        
        items_table.setStyle(ts_items)
        story.append(items_table)
        
        # --- 2. Tabla de Totales ---
        story.append(Spacer(1, 0.2*inch))

        if totales['saldo'] <= 0.01: # Si hemos pagado de más (saldo a favor)
            style_grand_total.textColor = colors.HexColor("#006400") # Verde

        totals_data = [
            ['', Paragraph('Total Cargos (Notas Prov):', style_total_label), Paragraph(f"${totales['cargos']:,.2f}", style_total_value)],
            ['', Paragraph('Total Abonos (Pagos):', style_total_label), Paragraph(f"${totales['abonos']:,.2f}", style_total_value)],
            ['', Paragraph('Saldo por Pagar:', style_total_label), Paragraph(f"${totales['saldo']:,.2f}", style_grand_total)],
        ]
        
        totals_table = Table(totals_data, colWidths=[3.2*inch, 1.6*inch, 1.7*inch])
        totals_table.setStyle(TableStyle([
            ('LINEABOVE', (1,2), (2,2), 1, colors.HexColor("#00788E")),
            ('TOPPADDING', (0,0), (-1,-1), 4), 
        ]))
        story.append(totals_table)

        # --- 3. Preparar datos para el Header/Footer ---
        datos_doc = {
            'titulo_entidad': 'PROVEEDOR:',
            'nombre_entidad': proveedor_nombre,
            'folio': '', 
            'fecha': '', 
            'extra_derecha_1': f"Del: {fechas['ini'].strftime('%d/%m/%Y')}",
            'extra_derecha_2': f"Al: {fechas['fin'].strftime('%d/%m/%Y')}",
        }

        header_footer_func = partial(
            _header_footer_platypus, 
            empresa_data=empresa_data, 
            titulo_doc="ESTADO DE CUENTA PROVEEDOR",
            datos_doc=datos_doc
        )
        
        # --- 4. Construir PDF ---
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
    except Exception as e:
        print(f"Error al generar PDF de Estado de Cuenta Proveedor (Platypus): {e}")
        import traceback
        traceback.print_exc()
        return False

# --- Orden de Compra (REESCRITA CON PLATYPUS) ---

def generar_pdf_orden_compra(proveedor_nombre, items_pedido, totales, empresa_data, save_path):
    """
    Función principal para generar el PDF de Orden de Compra.
    (Versión actualizada con Platypus para soportar saltos de página)
    """
    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                leftMargin=1*inch, rightMargin=1*inch,
                                topMargin=3.0*inch, bottomMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Estilos ---
        style_body = styles['BodyText']
        style_body.fontSize = 9
        style_body.alignment = TA_LEFT
        
        style_body_right = ParagraphStyle(name='BodyRight', parent=style_body, alignment=TA_RIGHT)

        style_header_base = ParagraphStyle(name='HeaderBase', parent=styles['Normal'],
                                      fontName='Helvetica-Bold', fontSize=10,
                                      textColor=colors.black) 
        style_header_left = ParagraphStyle(name='HeaderLeft', parent=style_header_base, alignment=TA_LEFT)
        style_header_right = ParagraphStyle(name='HeaderRight', parent=style_header_base, alignment=TA_RIGHT)
                                      
        style_total_label = ParagraphStyle(name='TotalLabel', parent=style_body,
                                           alignment=TA_RIGHT, fontName='Helvetica-Bold', fontSize=11)
        style_grand_total = ParagraphStyle(name='GrandTotal', parent=style_body_right,
                                           fontName='Helvetica-Bold', fontSize=12,
                                           textColor=colors.HexColor("#00788E"))

        # --- 1. Tabla de Items ---
        table_data = []
        wrapped_headers = [
            Paragraph("Cant.", style_header_left),
            Paragraph("Código", style_header_left),
            Paragraph("Descripción", style_header_left),
            Paragraph("P. Compra", style_header_right),
            Paragraph("Importe", style_header_right)
        ]
        table_data.append(wrapped_headers)

        for item in items_pedido:
            cant = str(item['cantidad_a_pedir'])
            cod = Paragraph(item['codigo'], style_body)
            desc = Paragraph(item['nombre'], style_body) # Usamos 'nombre'
            precio = f"${item['precio_compra']:,.2f}"
            importe = f"${item['importe']:,.2f}"
            
            wrapped_row = [
                Paragraph(cant, style_body), 
                cod,
                desc, 
                Paragraph(precio, style_body_right), 
                Paragraph(importe, style_body_right)
            ]
            table_data.append(wrapped_row)
        
        col_widths = [0.6*inch, 1.0*inch, 2.7*inch, 1.1*inch, 1.1*inch]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        ts_items = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEABOVE', (0,0), (-1,0), 1.5, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black), 
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            ('ALIGN', (0,1), (2,-1), 'LEFT'), 
            ('ALIGN', (3,1), (-1,-1), 'RIGHT'), 
        ])
        
        items_table.setStyle(ts_items)
        story.append(items_table)
        
        # --- 2. Tabla de Totales ---
        story.append(Spacer(1, 0.2*inch))
        
        total = totales.get('total', 0)

        totals_data = [
            ['', Paragraph('TOTAL:', style_total_label), Paragraph(f'${total:,.2f}', style_grand_total)],
        ]
        
        totals_table = Table(totals_data, colWidths=[4.4*inch, 1.0*inch, 1.1*inch])
        totals_table.setStyle(TableStyle([
            ('LINEABOVE', (1,0), (2,0), 1, colors.HexColor("#00788E")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(totals_table)

        # --- 3. Preparar datos para el Header/Footer ---
        datos_doc = {
            'titulo_entidad': 'PROVEEDOR:',
            'nombre_entidad': proveedor_nombre,
            'folio': '', # No usa folio
            'fecha': datetime.now().strftime('%d/%m/%Y'),
        }

        header_footer_func = partial(
            _header_footer_platypus, 
            empresa_data=empresa_data, 
            titulo_doc="ORDEN DE COMPRA",
            datos_doc=datos_doc
        )
        
        # --- 4. Construir PDF ---
        doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
        return True
    except Exception as e:
        print(f"Error al generar PDF de Orden de Compra (Platypus): {e}")
        import traceback
        traceback.print_exc()
        return False

# --- Reportes (Ya usa Platypus) ---
def _header_footer_reporte(canvas, doc, empresa_data, titulo_reporte, fechas_str):
    """Dibuja el encabezado y pie de página en CADA página del reporte."""
    canvas.saveState()
    width, height = letter
    
    # --- Encabezado ---
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
                                topMargin=2.8*inch, bottomMargin=1*inch) 
        
        story = []
        
        # 2. Definir Estilos de Párrafo
        styles = getSampleStyleSheet()
        
        style_body = styles['BodyText']
        style_body.fontSize = 9
        style_body.alignment = TA_LEFT 
        
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
        
        # 4. Calcular anchos de columna
        num_cols = len(headers)
        ancho_disponible = doc.width 
        col_widths = [ancho_disponible / num_cols] * num_cols
        
        # 5. Definir Estilo de Tabla
        ts = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#00788E")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
            
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('ALIGN', (0,1), (-1,-1), 'LEFT'), 
            
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#00788E")),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
        ])
        
        # 6. Ajustar alineación para columnas que parezcan números o moneda
        for col_idx, header in enumerate(headers):
            header_lower = header.lower()
            if any(s in header_lower for s in ['total', 'monto', 'saldo', 'precio', 'cant', 'stock', 'id', 'vendido', 'notas', 'folio', 'fecha']):
                ts.add('ALIGN', (col_idx, 1), (col_idx, -1), 'RIGHT')

        # 7. Crear objeto Tabla y aplicar estilo
        t = Table(table_data, colWidths=col_widths, repeatRows=1) # repeatRows=1
        t.setStyle(ts)
        
        story.append(t)
        
        # 8. Construir PDF
        
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