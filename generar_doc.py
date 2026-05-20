"""Genera WorkshopSys_ManualDefensa.docx"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

doc = Document()

# ── Estilos base ─────────────────────────────────────────────
style_normal = doc.styles['Normal']
style_normal.font.name = 'Arial'
style_normal.font.size = Pt(11)

for h, sz, bold in [('Heading 1', 16, True), ('Heading 2', 13, True), ('Heading 3', 12, True)]:
    s = doc.styles[h]
    s.font.name = 'Arial'
    s.font.size = Pt(sz)
    s.font.bold = bold
    s.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

TEAL  = RGBColor(0x00, 0x70, 0x70)
BLACK = RGBColor(0x00, 0x00, 0x00)
GRAY  = RGBColor(0x40, 0x40, 0x40)

def heading(text, level=1):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p

def para(text='', bold=False, italic=False, color=None, size=11, align=None, space_after=6):
    p = doc.add_paragraph()
    if text:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(size)
        if color:
            run.font.color.rgb = color
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p

def bullet(text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    run = p.add_run(text)
    run.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(3)
    return p

def page_break():
    doc.add_page_break()

def table_2col(rows, header=None, col_widths=None):
    ncols = len(header) if header else len(rows[0]) if rows else 2
    if col_widths is None:
        col_widths = tuple([6.4 / ncols] * ncols)
    t = doc.add_table(rows=0, cols=ncols)
    t.style = 'Table Grid'
    if header:
        row = t.add_row()
        for i, h in enumerate(header):
            cell = row.cells[i]
            cell.width = Inches(col_widths[i])
            run = cell.paragraphs[0].add_run(h)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
            shading = OxmlElement('w:shd')
            shading.set(qn('w:fill'), '1F497D')
            shading.set(qn('w:val'), 'clear')
            cell._tc.get_or_add_tcPr().append(shading)
    for row_data in rows:
        row = t.add_row()
        for i, val in enumerate(row_data):
            cell = row.cells[i]
            cell.width = Inches(col_widths[i])
            cell.paragraphs[0].add_run(val).font.size = Pt(10)
    doc.add_paragraph()

def qa(num, pregunta, respuesta):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    r = p.add_run(f"P{num}. {pregunta}")
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    p2 = doc.add_paragraph()
    r2 = p2.add_run(respuesta)
    r2.font.size = Pt(10.5)
    p2.paragraph_format.left_indent = Inches(0.3)
    p2.paragraph_format.space_after = Pt(6)

# ════════════════════════════════════════════════════════════
# PORTADA
# ════════════════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('WORKSHOPSYS')
r.font.size = Pt(32)
r.font.bold = True
r.font.color.rgb = TEAL

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run('Sistema de Gestión de Taller Automotriz')
r2.font.size = Pt(18)
r2.font.color.rgb = GRAY

doc.add_paragraph()

p3 = doc.add_paragraph()
p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = p3.add_run('Manual de Usuario y Documento de Defensa')
r3.font.size = Pt(14)
r3.font.bold = True

doc.add_paragraph()

table_2col(
    [['Lenguaje', 'Python 3.x'],
     ['Interfaz', 'PyQt5 (escritorio)'],
     ['Servidor', 'FastAPI + Railway'],
     ['Base de Datos', 'PostgreSQL (nube)'],
     ['IA', 'Regresión Lineal — scikit-learn'],
     ['Comunicación', 'HTTPS / WSS (WebSocket)']],
    header=['Componente', 'Tecnología'],
    col_widths=(2.5, 3.5)
)

page_break()

# ════════════════════════════════════════════════════════════
# ÍNDICE MANUAL
# ════════════════════════════════════════════════════════════
heading('Índice de Contenido', 1)
toc_items = [
    ('1.', 'Manual de Usuario', '3'),
    ('  1.1', 'Inicio de Sesión y Roles', '3'),
    ('  1.2', 'Módulo Clientes', '3'),
    ('  1.3', 'Módulo Proveedores', '4'),
    ('  1.4', 'Módulo Inventario', '4'),
    ('  1.5', 'Módulo Órdenes de Trabajo', '4'),
    ('  1.6', 'Módulo Cotizaciones y Predictor IA', '5'),
    ('  1.7', 'Módulo Notas de Venta', '5'),
    ('  1.8', 'Módulo Notas de Proveedor', '6'),
    ('  1.9', 'Módulo Reportes', '6'),
    ('  1.10', 'Módulo Configuración', '6'),
    ('2.', 'Justificación Módulo 1 — Arquitectura y Programación', '7'),
    ('3.', 'Justificación Módulo 2 — Sistemas Inteligentes', '9'),
    ('4.', 'Justificación Módulo 3 — Sistemas Distribuidos', '11'),
    ('5.', 'Preguntas y Respuestas — Defensa ante Jurado', '13'),
]
for num, title, page in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{num}  {title}")
    run.font.size = Pt(11)
    if not num.startswith(' '):
        run.font.bold = True

page_break()

# ════════════════════════════════════════════════════════════
# 1. MANUAL DE USUARIO
# ════════════════════════════════════════════════════════════
heading('1. Manual de Usuario', 1)
para('Este manual describe el funcionamiento de cada módulo del sistema WorkshopSys, una aplicación de escritorio para la gestión integral de talleres automotrices.')

# 1.1 Login
heading('1.1 Inicio de Sesión y Control de Acceso', 2)
para('Al iniciar la aplicación se presenta la pantalla de login. El usuario debe ingresar su nombre de usuario y contraseña. El sistema valida las credenciales contra el servidor en Railway y carga el perfil correspondiente.')
para('Roles disponibles:', bold=True)
table_2col(
    [['Admin', 'Acceso total: configuración, usuarios, todos los módulos'],
     ['Mecánico', 'Órdenes de trabajo, inventario, consulta de clientes'],
     ['Vendedor', 'Clientes, cotizaciones, notas de venta, reportes'],
     ['Capturista', 'Consulta y captura limitada sin acceso a configuración']],
    header=['Rol', 'Permisos'],
    col_widths=(1.8, 4.6)
)

# 1.2 Clientes
heading('1.2 Módulo — Clientes', 2)
para('Gestión completa de la cartera de clientes del taller.')
bullet('Registrar cliente nuevo: nombre, tipo (Particular/Empresa), contacto, dirección y RFC')
bullet('Buscar clientes por nombre, teléfono o RFC en tiempo real')
bullet('Editar datos de un cliente existente haciendo doble clic en la tabla')
bullet('Eliminar cliente (solo si no tiene documentos relacionados activos)')
bullet('Ver historial de órdenes y cotizaciones asociadas al cliente')

# 1.3 Proveedores
heading('1.3 Módulo — Proveedores', 2)
para('Administración de proveedores de refacciones y consumibles.')
bullet('Alta de proveedor con datos fiscales completos (RFC, razón social)')
bullet('Edición y baja de proveedores')
bullet('Vinculación automática con productos del inventario')
bullet('Acceso al historial de compras (notas de proveedor)')

# 1.4 Inventario
heading('1.4 Módulo — Inventario', 2)
para('Control de existencias de refacciones, consumibles y accesorios.')
bullet('Catálogo de productos con código único, categoría, ubicación física y precios')
bullet('Visualización de stock actual vs. stock mínimo con alerta visual (fondo rojo)')
bullet('Registro de movimientos: Entrada (compras) y Salida (ventas/uso en órdenes)')
bullet('Historial completo de movimientos por producto con fecha y responsable')
bullet('Ajuste manual de inventario con motivo documentado')

# 1.5 Órdenes de Trabajo
heading('1.5 Módulo — Órdenes de Trabajo', 2)
para('Gestión del proceso de servicio mecánico desde la recepción hasta la entrega.')
bullet('Nueva orden: seleccionar cliente, capturar datos del vehículo (marca, modelo, año, placas, color, kilometraje)')
bullet('Agregar servicios/items con descripción detallada')
bullet('Asignar mecánico responsable')
bullet('Seguimiento de estados: Pendiente → En Proceso → Completada → Facturada / Cancelada')
bullet('Fecha de recepción y fecha de entrega prometida')
bullet('Convertir orden completada a Nota de Venta con un clic')
bullet('Búsqueda por folio, cliente o estado')

# 1.6 Cotizaciones
heading('1.6 Módulo — Cotizaciones y Predictor IA', 2)
para('Generación de presupuestos con apoyo del modelo de inteligencia artificial.')
bullet('Crear cotización vinculada a un cliente')
bullet('Agregar servicios manualmente o usar el botón "Obtener" para que la IA sugiera el precio')
bullet('El predictor considera: tipo de servicio, tipo de cliente, mes actual, historial de visitas y días desde última visita')
bullet('Resultado de la IA: precio sugerido + rango mínimo/máximo + nivel de confianza')
bullet('Calcular subtotal, IVA (16%) y total automáticamente')
bullet('Cambiar estado: Pendiente → Aceptada (genera Nota de Venta) / Rechazada')
bullet('Exportar cotización a PDF con datos del taller y logo')

# 1.7 Notas de Venta
heading('1.7 Módulo — Notas de Venta', 2)
para('Facturación y control de cuentas por cobrar.')
bullet('Creación desde cotización aceptada, desde orden completada o directa')
bullet('Registro de pagos parciales y totales con método de pago')
bullet('Control automático de saldo pendiente')
bullet('Estados: Registrado → Pagado Parcialmente → Pagado / Cancelado')
bullet('Historial de abonos con fecha, monto y método de pago')
bullet('Exportación a PDF (nota de venta oficial con datos fiscales del taller)')

# 1.8 Notas de Proveedor
heading('1.8 Módulo — Notas de Proveedor', 2)
para('Registro de compras a proveedores y control de cuentas por pagar.')
bullet('Nueva nota de proveedor vinculada a un proveedor registrado')
bullet('Captura de items comprados con cantidad, descripción y precio')
bullet('Cálculo automático de subtotal + IVA')
bullet('Registro de pagos al proveedor (abonos o liquidación)')
bullet('Genera movimiento de Entrada en inventario al registrar la compra')

# 1.9 Reportes
heading('1.9 Módulo — Reportes', 2)
para('Cinco reportes gerenciales con exportación a PDF y Excel.')
table_2col(
    [['Ventas por Periodo', 'Total facturado, número de notas y ticket promedio en un rango de fechas'],
     ['Servicios Más Solicitados', 'Ranking de servicios por frecuencia y monto generado'],
     ['Clientes Frecuentes', 'Clientes con mayor número de visitas y gasto acumulado'],
     ['Inventario Bajo Stock', 'Productos cuyo stock actual está por debajo del mínimo definido'],
     ['Cuentas por Cobrar', 'Notas de venta con saldo pendiente ordenadas por antigüedad']],
    header=['Reporte', 'Descripción'],
    col_widths=(2.2, 4.2)
)

# 1.10 Configuración
heading('1.10 Módulo — Configuración', 2)
para('Administración del sistema (solo Admin).')
bullet('Datos de la empresa: nombre comercial, razón social, RFC, dirección, teléfonos, logo')
bullet('El logo se almacena en la base de datos y aparece en todos los PDFs generados')
bullet('Gestión de usuarios: crear, editar, activar/desactivar, asignar rol')
bullet('Respaldo: descarga un archivo .json con toda la base de datos')
bullet('Restauración: carga un archivo .json de respaldo y repuebla la BD en Railway')

page_break()

# ════════════════════════════════════════════════════════════
# 2. MÓDULO 1 — ARQUITECTURA
# ════════════════════════════════════════════════════════════
heading('2. Justificación — Módulo 1: Arquitectura y Programación de Sistemas', 1)

heading('1.1 Decisión de Lenguajes de Programación', 2)
para('WorkshopSys utiliza Python como único lenguaje de programación, tanto para el cliente de escritorio como para el servidor. Esta decisión responde a criterios técnicos y de ingeniería:')
bullet('Ecosistema unificado: PyQt5 (GUI), FastAPI (API REST), scikit-learn (ML), pandas (datos), ReportLab (PDFs), SQLAlchemy (ORM), todo en Python.')
bullet('Equipo único: un solo lenguaje elimina el cambio de contexto cognitivo y permite que cualquier desarrollador trabaje en cualquier capa.')
bullet('Productividad: Python permite desarrollar y probar funcionalidades complejas en menos líneas de código que lenguajes tipados estáticamente.')
bullet('Madurez del ecosistema: librerías de producción estables con soporte activo en todas las áreas requeridas por el proyecto.')

heading('1.2 Base de Datos y Estructuras de Datos', 2)
para('Sistema de gestión de base de datos: PostgreSQL alojado en Railway (nube). Acceso mediante SQLAlchemy ORM con el patrón Repository implementado en crud.py.')
para('Estructura de datos — 16 tablas relacionales:', bold=True)
table_2col(
    [['clientes', 'Datos de clientes particulares y empresas'],
     ['proveedores', 'Catálogo de proveedores con datos fiscales'],
     ['inventario', 'Productos, stock actual/mínimo y precios'],
     ['movimientos_inventario', 'Trazabilidad de entradas y salidas de stock'],
     ['ordenes / ordenes_items', 'Órdenes de trabajo y sus servicios'],
     ['cotizaciones / cotizaciones_items', 'Presupuestos y líneas de servicio'],
     ['notas_venta / items / pagos', 'Facturación y registro de abonos'],
     ['notas_proveedor / items / pagos', 'Compras a proveedores y pagos'],
     ['usuarios', 'Cuentas de usuario con roles y hash de contraseña'],
     ['config_empresa', 'Datos del taller incluyendo logo (BLOB)']],
    header=['Tabla(s)', 'Propósito'],
    col_widths=(2.8, 3.6)
)
para('Justificación de PostgreSQL: soporte para tipos de datos avanzados (LargeBinary para logos), transacciones ACID, escalabilidad, y compatibilidad nativa con Railway sin configuración adicional.')

heading('1.3 Metodología de Programación', 2)
para('El proyecto sigue Programación Orientada a Objetos (POO) con separación clara en capas:')
table_2col(
    [['models.py', 'Capa de modelo — clases ORM mapeadas a tablas PostgreSQL'],
     ['crud.py', 'Capa de repositorio — operaciones de acceso a datos desacopladas de la API'],
     ['server/main.py', 'Capa de API — endpoints REST y WebSocket Manager'],
     ['gui/api_client.py', 'Capa de cliente HTTP — abstracción de llamadas al servidor'],
     ['gui/*.py', 'Capa de presentación — ventanas PyQt5 como clases QDialog/QWidget']],
    header=['Archivo', 'Responsabilidad'],
    col_widths=(2.5, 4.0)
)
para('Cada ventana de la interfaz es una clase independiente, favoreciendo la cohesión y el bajo acoplamiento. Los datos fluyen unidireccionalmente: GUI → api_client → servidor → crud → BD.')

heading('1.4 Argumentación con Ingeniería de Software', 2)
bullet('Patrón MVC adaptado: Modelo (models.py + crud.py), Vista (gui/*.py), Controlador (api_client.py + main.py).')
bullet('Inyección de dependencias: FastAPI usa Depends(get_db) para proveer sesiones de BD sin estado compartido entre requests.')
bullet('Patrón Repository: crud.py centraliza toda la lógica de acceso a datos, facilitando pruebas y mantenimiento.')
bullet('Señales/Slots de Qt: el WebSocketClient emite señales Python que las ventanas escuchan, desacoplando completamente la red de la interfaz.')
bullet('WebSocket Manager: gestión de conexiones activas con broadcast a todos los clientes conectados para sincronización en tiempo real.')
bullet('Sistema de roles y permisos: los botones y módulos se muestran u ocultan según el rol del usuario autenticado.')
bullet('Manejo de errores: try/except en todas las capas con mensajes de error al usuario sin exponer detalles técnicos.')

heading('1.5 Modelado del Sistema', 2)
para('Relaciones principales del diagrama entidad-relación:')
bullet('Cliente (1) → (N) Órdenes, Cotizaciones, NotasVenta')
bullet('Proveedor (1) → (N) Productos, NotasProveedor')
bullet('Orden (1) → (N) OrdenItems  |  cascade delete')
bullet('Cotizacion (1) → (N) CotizacionItems  |  cascade delete')
bullet('NotaVenta (1) → (N) NotaVentaItems, NotaVentaPagos  |  cascade delete')
bullet('NotaProveedor (1) → (N) NotaProveedorItems, NotaProveedorPagos  |  cascade delete')
bullet('Producto (1) → (N) MovimientosInventario')
para('Las claves foráneas garantizan integridad referencial. Los cascade delete en items evitan registros huérfanos al eliminar documentos padre.')

page_break()

# ════════════════════════════════════════════════════════════
# 3. MÓDULO 2 — IA
# ════════════════════════════════════════════════════════════
heading('3. Justificación — Módulo 2: Sistemas Inteligentes', 1)

heading('2.1.2 Rama Aplicada: Aprendizaje Automático (Machine Learning)', 2)
para('WorkshopSys implementa un módulo de Machine Learning que predice el precio de servicios automotrices basándose en el historial de cotizaciones del propio taller. El sistema aprende de los datos reales generados en operación y mejora su precisión conforme crece la base de datos.')
para('El módulo se integra directamente en la pantalla de cotizaciones: al ingresar la descripción de un servicio, el usuario puede presionar "Obtener" y el modelo devuelve un precio sugerido con rango de confianza en menos de un segundo.')

heading('2.2 Modelo Matemático', 2)
para('Algoritmo: Regresión Lineal Múltiple con One-Hot Encoding para variables categóricas y StandardScaler para variables numéricas.')
para('Ecuación general:', bold=True)
p = doc.add_paragraph()
r = p.add_run('Precio = β₀ + β₁(servicio) + β₂(tipo_cliente) + β₃(mes) + β₄(historial) + β₅(días_inactivo)')
r.font.size = Pt(11)
r.font.bold = True
r.font.color.rgb = TEAL
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()
para('Ejemplo concreto para Afinación Mayor:', bold=True)
table_2col(
    [['Precio base (β₀)', '$800'],
     ['+150 si tipo_cliente = Empresa', 'β₂ activo'],
     ['+50 si mes = diciembre (temporada alta)', 'β₃ activo'],
     ['-100 si historial > 5 visitas (cliente frecuente)', 'β₄ activo'],
     ['+200 si días_inactivo > 180 (cliente inactivo)', 'β₅ activo'],
     ['= Precio final predicho', '$1,200 aprox.']],
    header=['Factor', 'Efecto'],
    col_widths=(4.0, 2.4)
)

para('Variables de entrada:', bold=True)
table_2col(
    [['Tipo de servicio', 'Categórica', 'One-Hot Encoding', 'Alta'],
     ['Tipo de cliente', 'Categórica', 'One-Hot Encoding', 'Media'],
     ['Mes del año', 'Numérica (1-12)', 'StandardScaler', 'Baja'],
     ['Historial de visitas', 'Numérica (0-50)', 'StandardScaler', 'Media'],
     ['Días de inactividad', 'Numérica (0-730)', 'StandardScaler', 'Media']],
    header=['Variable', 'Tipo', 'Tratamiento', 'Importancia'],
    col_widths=(1.8, 1.6, 1.8, 1.2)
)

para('Métricas de rendimiento del modelo entrenado:', bold=True)
table_2col(
    [['MAE (Error Absoluto Medio)', '$127 MXN', 'En promedio el modelo se equivoca ±$127'],
     ['MAPE (Error Porcentual Medio)', '9.8%', 'Error relativo promedio menor al 10%'],
     ['RMSE (Raíz del Error Cuadrático)', '$165 MXN', 'Penaliza errores grandes'],
     ['R² (Coeficiente de determinación)', '0.87', 'Explica el 87% de la variación de precios']],
    header=['Métrica', 'Valor', 'Interpretación'],
    col_widths=(2.2, 1.2, 3.0)
)

heading('2.3 Justificación del Algoritmo Seleccionado', 2)
para('Se eligió Regresión Lineal Múltiple sobre otras alternativas por las siguientes razones técnicas:')
table_2col(
    [['Interpretabilidad', 'Cada coeficiente β tiene significado directo de negocio. El taller puede entender por qué el sistema sugiere un precio.'],
     ['Velocidad', 'Predicción en microsegundos. No requiere GPU ni infraestructura especial.'],
     ['Datos estructurados', 'Los registros de cotizaciones son tabulares, el escenario ideal para regresión lineal.'],
     ['Volumen de datos', 'Con cientos de cotizaciones es suficiente. Las redes neuronales requieren decenas de miles.'],
     ['Mejora continua', 'El modelo se puede re-entrenar con nuevos datos sin cambiar la arquitectura.']],
    header=['Criterio', 'Justificación'],
    col_widths=(1.8, 4.6)
)
para('Alternativas descartadas:', bold=True)
bullet('Redes Neuronales: requieren miles de datos de entrenamiento y son cajas negras poco interpretables para el negocio.')
bullet('Random Forest: mayor precisión pero menor interpretabilidad; el documento académico justifica la regresión lineal.')
bullet('SVM: innecesariamente complejo para datos tabulares bien estructurados.')

para('Mejoras implementadas en el modelo:', bold=True)
bullet('Normalización de nombres de servicios: eliminación de acentos y caracteres especiales con unicodedata, garantizando que "Afinación" y "afinacion" sean tratados como el mismo servicio.')
bullet('StandardScaler: escala las variables numéricas a la misma unidad de medida, evitando que días_inactivo (0-730) domine sobre mes (1-12) en los coeficientes.')
bullet('Auto-reentrenamiento: el sistema verifica si hay 50+ cotizaciones nuevas y reentrena el modelo automáticamente.')

page_break()

# ════════════════════════════════════════════════════════════
# 4. MÓDULO 3 — DISTRIBUIDOS
# ════════════════════════════════════════════════════════════
heading('4. Justificación — Módulo 3: Sistemas Distribuidos', 1)

heading('3.1 Sistema Descentralizado', 2)
para('WorkshopSys es un sistema verdaderamente distribuido: múltiples clientes de escritorio (PyQt5) instalados en distintas computadoras del taller se conectan a un servidor centralizado en Railway. Los clientes no comparten estado entre sí directamente; toda coordinación pasa por el servidor.')
para('Criterios del checklist cubiertos:')
bullet('3.1.1 Componentes concurrentes: FastAPI usa async/await de Python para manejar múltiples requests simultáneos sin bloquear el servidor. El WebSocket Manager gestiona N conexiones activas en paralelo.')
bullet('3.1.6 Tiempo real vía sockets: WebSocket (WSS) notifica a todos los clientes conectados cuando ocurre un cambio (nuevo cliente, nueva orden, actualización de stock). El cliente PyQt5 usa un QThread dedicado para la conexión WebSocket sin bloquear la interfaz.')
bullet('3.1.7 Seguridad en múltiples arquitecturas: toda la comunicación usa TLS (HTTPS/WSS). Las contraseñas se almacenan como SHA-256. El servidor corre con --proxy-headers para soporte seguro detrás del proxy de Railway.')

heading('3.2 Modelo Cliente-Servidor Desarrollado desde Cero', 2)
para('El sistema no usa un servicio preexistente: tanto el servidor como el cliente fueron programados completamente:')
table_2col(
    [['TallerAPIClient', 'gui/api_client.py', 'Cliente HTTP personalizado con métodos para cada endpoint (get_clientes, crear_orden, etc.)'],
     ['WebSocketClient', 'gui/websocket_client.py', 'Cliente WebSocket en QThread con reconexión automática y manejo de señales Qt'],
     ['FastAPI Server', 'server/main.py', '50+ endpoints REST (GET/POST/PUT/DELETE) + endpoint WebSocket /ws'],
     ['ConnectionManager', 'server/main.py', 'Gestiona conexiones activas y hace broadcast a todos los clientes'],
     ['CRUD Layer', 'server/crud.py', 'Lógica de negocio y acceso a datos desacoplada de los endpoints']],
    header=['Componente', 'Archivo', 'Descripción'],
    col_widths=(1.6, 1.8, 3.0)
)

heading('3.3 Comunicación entre Dispositivos', 2)
para('El sistema establece comunicación entre al menos tres nodos:')
bullet('Nodo 1: PC del taller (cliente PyQt5) — inicia requests HTTP y mantiene conexión WebSocket')
bullet('Nodo 2: Servidor Railway (FastAPI) — procesa la lógica de negocio y coordina la BD')
bullet('Nodo 3: Base de datos PostgreSQL (Railway) — almacenamiento persistente')
para('Flujo de sincronización en tiempo real:')
bullet('Usuario A (PC1) crea una nueva orden → POST /ordenes al servidor')
bullet('Servidor guarda en BD y hace broadcast WebSocket con evento orden_creada')
bullet('Usuario B (PC2) recibe el evento y su tabla de órdenes se actualiza automáticamente')
bullet('Sin necesidad de que B recargue manualmente la pantalla')

heading('3.4 Protocolos de Comunicación Justificados', 2)
table_2col(
    [['HTTPS (TLS 1.2+)', 'Operaciones CRUD (REST)', 'Cifrado extremo a extremo. Railway provee certificado SSL automático. Justificado por manejo de datos comerciales sensibles.'],
     ['WSS (WebSocket Secure)', 'Notificaciones en tiempo real', 'Protocolo full-duplex sobre TLS. Permite push del servidor al cliente sin polling. Justificado por necesidad de sincronización inmediata entre múltiples usuarios.'],
     ['JSON', 'Formato de datos', 'Formato universal, legible y compatible con Python nativo. Todos los endpoints reciben y devuelven JSON.'],
     ['Ping/Pong (30s)', 'Keep-alive WebSocket', 'Evita que el proxy de Railway cierre conexiones inactivas. El cliente detecta timeout en 10s y reconecta.'],
     ['Reconexión (5s)', 'Tolerancia a fallos', 'El cliente reintenta conexión cada 5 segundos ante caída del servidor, garantizando disponibilidad continua.']],
    header=['Protocolo', 'Uso', 'Justificación'],
    col_widths=(1.6, 1.6, 3.2)
)

page_break()

# ════════════════════════════════════════════════════════════
# 5. Q&A — DEFENSA
# ════════════════════════════════════════════════════════════
heading('5. Preguntas y Respuestas — Defensa ante Jurado', 1)
para('Organizado por módulo evaluado. Las respuestas están diseñadas para ser argumentadas oralmente ante un jurado técnico.')

heading('MÓDULO 1 — Arquitectura y Programación', 2)

qa(1, '¿Por qué usaron Python para todo? ¿No sería mejor usar un lenguaje más robusto para el servidor?',
   'Python es perfectamente apto para producción en servidor. FastAPI es uno de los frameworks más rápidos en benchmarks (comparable a Node.js y Go para operaciones I/O). La ventaja de usar Python en todas las capas es que el mismo equipo puede mantener cualquier parte del sistema sin cambiar de lenguaje, reduciendo la curva de aprendizaje y los errores de integración.')

qa(2, '¿Por qué eligieron FastAPI y no Flask o Django?',
   'FastAPI fue elegido por tres razones: primero, soporte nativo de async/await para manejar múltiples conexiones concurrentes sin bloquear. Segundo, generación automática de documentación interactiva (Swagger en /docs) que facilita pruebas. Tercero, validación de tipos con Pydantic integrada. Flask no tiene async nativo y Django es demasiado pesado para una API.')

qa(3, '¿Por qué PostgreSQL y no MySQL o SQLite?',
   'PostgreSQL fue elegido por su soporte de LargeBinary (para almacenar el logo de la empresa en BD), transacciones ACID robustas, y compatibilidad nativa con Railway. SQLite es monousuario y no soporta acceso concurrente desde múltiples clientes. MySQL es una alternativa válida, pero PostgreSQL tiene mejor soporte de tipos de datos avanzados.')

qa(4, '¿Qué es SQLAlchemy y por qué usarlo en lugar de SQL directo?',
   'SQLAlchemy es un ORM (Object-Relational Mapper) que permite trabajar con la BD usando clases Python en lugar de strings SQL. Esto evita inyecciones SQL, hace el código más legible y permite cambiar de motor de BD (SQLite a PostgreSQL) sin reescribir las consultas. El patrón Repository en crud.py centraliza toda la lógica de acceso a datos.')

qa(5, '¿Qué patrón de diseño usaron y cómo se ve en el código?',
   'Usamos una adaptación de MVC: el Modelo es models.py (clases ORM) + crud.py (repositorio), la Vista son los archivos gui/*.py (ventanas PyQt5), y el Controlador es api_client.py en el cliente y main.py en el servidor. Adicionalmente usamos el patrón Observer a través de las señales Qt para actualizar la interfaz ante eventos del WebSocket.')

qa(6, '¿Cómo manejan la seguridad de las contraseñas?',
   'Las contraseñas se almacenan como hash SHA-256 en la base de datos. Nunca se almacena la contraseña en texto plano. Al autenticar, se aplica SHA-256 al password ingresado y se compara con el hash almacenado. Para producción se recomendaría bcrypt con salt, que es más resistente a ataques de diccionario.')

qa(7, '¿Cómo funciona el sistema de roles?',
   'Cada usuario tiene un campo "rol" en la tabla usuarios con valores: Admin, Mecánico, Vendedor o Capturista. Al iniciar sesión, el servidor devuelve el rol del usuario. La ventana principal (MainWindow) recibe el rol y muestra u oculta los botones del menú según los permisos definidos para ese rol. No es un sistema de permisos granulares sino de roles predefinidos.')

qa(8, '¿Qué sucede si la base de datos tiene un fallo?',
   'FastAPI usa el patrón de sesión con try/except/finally en cada endpoint. Si ocurre un error en una operación, se llama db.rollback() para revertir la transacción y se devuelve un HTTP 400 o 500 al cliente. El cliente muestra el mensaje de error al usuario. El servidor en Railway tiene política de reinicio automático configurada en railway.toml.')

qa(9, '¿Cómo está estructurado el proyecto en carpetas?',
   'La raíz tiene main.py (punto de entrada del cliente), server/ (FastAPI: main.py, crud.py, models.py, database.py), gui/ (ventanas PyQt5, api_client.py, websocket_client.py, estilos), ml/ (predictor_ml_final.py, auto_retrain.py), assets/ (imágenes), y scripts de utilidad. Esta separación sigue el principio de responsabilidad única.')

qa(10, '¿Cómo garantizan la integridad de los datos con múltiples usuarios simultáneos?',
   'PostgreSQL maneja la concurrencia con bloqueos a nivel de fila y transacciones ACID. SQLAlchemy usa el patrón Unit of Work: cada request HTTP tiene su propia sesión de BD (yield en get_db), evitando que dos requests compartan estado. FastAPI async permite manejar múltiples requests sin bloquear, pero las operaciones de BD son síncronas para garantizar consistencia.')

heading('MÓDULO 2 — Sistemas Inteligentes', 2)

qa(11, '¿Por qué regresión lineal y no una red neuronal?',
   'La regresión lineal es la herramienta correcta para este problema específico. Tenemos datos estructurados y tabulares, no imágenes ni texto libre. Con cientos de cotizaciones es suficiente; las redes neuronales requieren decenas de miles de muestras para generalizar bien. Además, la regresión lineal es interpretable: el dueño del taller puede entender por qué el sistema sugiere $1,200 para una afinación.')

qa(12, '¿Qué significa R² = 0.87 en términos prácticos?',
   'R² = 0.87 significa que el modelo explica el 87% de la variación en los precios. Si hay diferencia de precio entre dos servicios, el modelo puede explicar el 87% de esa diferencia mediante las 5 variables de entrada. El 13% restante corresponde a factores no capturados (negociaciones especiales, descuentos ocasionales, etc.).')

qa(13, '¿Qué es el MAE y qué implica que sea $127?',
   'MAE (Mean Absolute Error) es el error promedio absoluto en las mismas unidades de la variable objetivo, en este caso pesos mexicanos. Un MAE de $127 significa que en promedio el modelo se equivoca ±$127. Si el precio real es $1,000, el sistema predirá entre $873 y $1,127. Para el contexto de un taller, esto es aceptable como precio de referencia inicial.')

qa(14, '¿Para qué sirve el One-Hot Encoding?',
   'La regresión lineal trabaja con números, no con texto. "Afinación Mayor" no se puede sumar o multiplicar directamente. One-Hot Encoding convierte cada servicio en una columna binaria (0 o 1). Si el servicio es "Afinación Mayor", esa columna vale 1 y todas las demás valen 0. Así el modelo puede asignar un coeficiente β diferente a cada servicio.')

qa(15, '¿Para qué sirve el StandardScaler?',
   'Las variables numéricas tienen escalas muy diferentes: mes va de 1 a 12, días_inactivo va de 0 a 730. En regresión lineal, variables con mayor escala tienden a dominar el ajuste aunque no sean las más importantes. StandardScaler normaliza cada variable a media 0 y desviación estándar 1, poniendo todas en la misma escala para que el modelo las compare justamente.')

qa(16, '¿Cómo sabe el modelo el historial de un cliente?',
   'Al hacer una cotización, el sistema consulta en la BD cuántas cotizaciones previas tiene ese cliente (historial) y cuántos días han pasado desde la última (días_inactivo). Estos valores se pasan al predictor junto con el tipo de servicio y el mes actual. El predictor los escala con el StandardScaler guardado en el .pkl y genera la predicción.')

qa(17, '¿Cuándo y cómo se re-entrena el modelo?',
   'El módulo auto_retrain.py verifica al iniciar la aplicación si hay 50 o más cotizaciones nuevas desde el último entrenamiento. Si es así, ejecuta el reentrenamiento en segundo plano sin interrumpir la aplicación. El nuevo modelo .pkl reemplaza al anterior. También se puede re-entrenar manualmente ejecutando python entrenar_onehot.py.')

qa(18, '¿Qué pasa si se ingresa un servicio que el modelo nunca vio?',
   'El servicio nuevo genera una columna one-hot con valor 0 (no existe en el modelo entrenado). El predictor asigna 0 a todas las columnas de servicio, y la predicción se basa principalmente en el tipo de cliente, mes, historial y días de inactividad. El resultado es un precio genérico razonable pero menos preciso. Conforme ese servicio aparezca en más cotizaciones, el siguiente reentrenamiento lo aprenderá.')

qa(19, '¿Por qué el modelo se guarda como archivo .pkl?',
   '.pkl es el formato de serialización de Python (pickle). Permite guardar el objeto modelo completo (coeficientes β, columnas one-hot, scaler) en un archivo binario y cargarlo después sin re-entrenar. El archivo contiene: el objeto LinearRegression con todos sus coeficientes, la lista de columnas del entrenamiento y el StandardScaler ajustado.')

qa(20, '¿Cómo validaron que el modelo funciona correctamente?',
   'Se utilizó la técnica de división train/test: 80% de los datos para entrenar y 20% para evaluar. El modelo nunca ve los datos de evaluación durante el entrenamiento. Las métricas (MAE, MAPE, R²) se calculan sobre el conjunto de prueba, garantizando que miden la capacidad de generalización real del modelo, no memorización de datos.')

heading('MÓDULO 3 — Sistemas Distribuidos', 2)

qa(21, '¿Por qué este sistema es distribuido y no solo cliente-servidor centralizado?',
   'Es distribuido porque múltiples nodos (PCs del taller) cooperan para completar operaciones. Un cliente genera una orden, el servidor la procesa, la BD la persiste, y todos los demás clientes reciben la actualización vía WebSocket sin intervención del usuario. Los recursos (procesamiento, datos, servicios) se comparten entre nodos geográficamente separados.')

qa(22, '¿Cuál es la diferencia entre HTTPS y WSS en su implementación?',
   'HTTPS (HTTP Secure) es el protocolo para operaciones CRUD: el cliente hace un request, el servidor responde, la conexión se cierra. Es unidireccional y sin estado. WSS (WebSocket Secure) establece una conexión persistente full-duplex: el servidor puede enviar mensajes al cliente en cualquier momento sin que el cliente los solicite. HTTPS para datos, WSS para eventos.')

qa(23, '¿Cómo funciona el WebSocket en el cliente?',
   'WebSocketClient es una clase que hereda de QThread (hilo de Qt). Corre en segundo plano sin bloquear la interfaz gráfica. Usa la librería websocket-client con run_forever() que mantiene la conexión activa. Cuando llega un mensaje JSON del servidor, el método on_message lo parsea y emite una señal Qt (orden_creada, cliente_actualizado, etc.) que la ventana correspondiente escucha.')

qa(24, '¿Qué pasa si se cae el servidor mientras hay clientes conectados?',
   'El WebSocketClient detecta la desconexión en on_close o on_error y emite la señal connection_status(False). La interfaz muestra un indicador de desconexión. El hilo espera 5 segundos y reintenta automáticamente la conexión en un bucle while self.running. Los clientes continúan funcionando en modo degradado hasta que el servidor esté disponible nuevamente.')

qa(25, '¿Cómo evitan que el proxy de Railway cierre las conexiones WebSocket?',
   'Se configuraron dos mecanismos: primero, ping_interval=30 y ping_timeout=10 en run_forever(), que envía pings automáticos cada 30 segundos para mantener viva la conexión. Segundo, en railway.toml se agregó --proxy-headers --forwarded-allow-ips="*" al comando de inicio de uvicorn, permitiendo que el proxy de Railway reenvíe correctamente los headers de upgrade del WebSocket.')

qa(26, '¿Cuántos clientes simultáneos puede manejar el servidor?',
   'FastAPI con uvicorn usa un event loop async que puede manejar miles de conexiones concurrentes en teoría. En práctica, el límite lo impone el plan de Railway (CPU y memoria) y PostgreSQL (conexiones simultáneas). Para un taller con 5-10 usuarios simultáneos, el sistema tiene margen amplio. El connection pool de SQLAlchemy gestiona la reutilización de conexiones a BD.')

qa(27, '¿Por qué pusieron el servidor en Railway y no en un servidor propio?',
   'Railway fue elegido por disponibilidad inmediata (sin configurar infraestructura), soporte nativo de PostgreSQL, HTTPS automático con certificado SSL, dominio público accesible desde cualquier lugar, y costo inicial gratuito para proyectos académicos. Para producción real se podría migrar a AWS, Azure o GCP sin cambiar el código.')

qa(28, '¿Cómo funciona el backup y restore distribuido?',
   'El endpoint GET /backup serializa las 16 tablas de la BD a JSON, convirtiendo fechas a ISO string y bytes (logo) a Base64. El cliente descarga el JSON y lo guarda localmente. Para restaurar, el cliente lee el archivo, lo envía al endpoint POST /restore que borra todas las tablas en orden inverso de FK, reinserta los datos en orden correcto y resetea las secuencias de PostgreSQL.')

qa(29, '¿Cómo sincronización los datos entre múltiples clientes en tiempo real?',
   'El servidor mantiene una lista de conexiones WebSocket activas (ConnectionManager). Cuando se completa una operación CRUD (crear cliente, actualizar orden, etc.), el endpoint hace await manager.broadcast() enviando un mensaje JSON con el tipo de evento y los datos actualizados a TODOS los clientes conectados. Cada cliente tiene handlers para cada tipo de evento que actualizan la interfaz.')

qa(30, '¿Qué protocolo de seguridad usan para proteger los datos en tránsito?',
   'TLS (Transport Layer Security) protege toda la comunicación. Railway provee automáticamente un certificado SSL para el dominio. El cliente PyQt5 usa requests con HTTPS y websocket-client con WSS, verificando el certificado del servidor. Se agregó sslopt={"cert_reqs": ssl.CERT_NONE} en desarrollo para evitar errores con el certificado de Railway en entornos locales.')

qa(31, '¿Cómo manejan errores de red en el cliente?',
   'El TallerAPIClient envuelve cada llamada HTTP en try/except. Si hay un error de conexión, timeout o error HTTP (4xx/5xx), el método devuelve None o False. Las ventanas GUI verifican el resultado y muestran QMessageBox con el error al usuario. El timeout de requests es 10 segundos para GET/PUT/DELETE y 120 segundos para operaciones de restore (que pueden tardar más).')

qa(32, '¿Por qué usan JSON como formato de intercambio y no XML o protobuf?',
   'JSON es el estándar de facto para APIs REST. FastAPI lo serializa/deserializa automáticamente con Pydantic. Python lo maneja nativamente con el módulo json. Es legible por humanos (facilita debugging), soportado universalmente en todos los lenguajes y plataformas, y suficientemente eficiente para el volumen de datos de un taller (sin necesidad de la compresión que ofrece protobuf).')

qa(33, '¿Qué consideraciones de seguridad tomaron para el sistema de usuarios?',
   'Primero, las contraseñas se hashean en el servidor (nunca en el cliente) con SHA-256 antes de almacenarse. Segundo, el sistema de roles restringe qué módulos puede ver cada usuario. Tercero, toda comunicación va cifrada por TLS. Cuarto, el servidor valida que el usuario exista y esté activo antes de cada operación de login. Como mejora futura se implementaría JWT para sesiones sin estado.')

# Guardar
out_path = r"C:\Users\Efrain\Desktop\WorkshopSys_ManualDefensa.docx"
doc.save(out_path)
print(f"OK Documento guardado en: {out_path}")
