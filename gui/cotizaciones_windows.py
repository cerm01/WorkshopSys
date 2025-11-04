import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSizePolicy, QApplication,
    QLabel, QLineEdit, QGridLayout, QGroupBox,
    QDoubleSpinBox, QMessageBox, QTableView, QHeaderView,
    QMenu, QAction, QFrame, QWidget, QDateEdit, QComboBox,
    QInputDialog, QCompleter,
    QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem, QIcon, QColor, QFont

# Import styles
from styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2,
    GROUP_BOX_STYLE, LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
)
from datetime import datetime, timedelta
from db_helper import db_helper


class CotizacionesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clientes_dict = {}
        self.main_window = parent
        self.setWindowTitle("Cotizaciones")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)

        # Aplicar estilos
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        # Variable para seguimiento de edición
        self.fila_en_edicion = -1

        # Diccionario para almacenar el IVA de cada fila
        self.iva_por_fila = {}      

        # Diccionario para almacenar el tipo de cada fila
        self.tipo_por_fila = {}  # 'normal', 'nota', 'seccion', 'condiciones'

        # Variables BD
        self.cotizacion_actual_id = None
        self.modo_edicion = False

        # Crear la interfaz
        self.setup_ui()

        self.cargar_clientes_autocompletado()

        # Estado inicial
        self.controlar_estado_campos(True)
    
    def setup_ui(self):
        """Configurar la interfaz de usuario  """
        # Layout principal 
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear grupo de datos del cliente para cotización
        self.crear_grupo_cotizacion(main_layout)
        
        # Crear el contenedor para los datos de producto/servicio
        self.crear_grupo_producto_servicio(main_layout)
        
        # Crear tabla para mostrar los items agregados
        self.crear_tabla_items(main_layout)

        # Crear panel de totales
        self.crear_panel_totales(main_layout)
        
        # Añadir espacio flexible para empujar los botones hacia abajo
        main_layout.addStretch(1)
        
        # Crear layout para los botones (fila horizontal)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        botones_layout.setContentsMargins(0, 0, 0, 0)
        
        # Textos de los botones específicos para cotizaciones
        textos_botones = ["Nueva", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir", "Generar Nota"]
        
        # Crear los botones y añadirlos al layout
        self.botones = []
        
        for texto in textos_botones:
            boton = QPushButton(texto)
            boton.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            boton.setCursor(Qt.PointingHandCursor)
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            botones_layout.addWidget(boton)
            self.botones.append(boton)
        
        # Añadir el layout de botones al layout principal
        main_layout.addLayout(botones_layout)

        # Asignar el layout al diálogo
        self.setLayout(main_layout)
        
        # Conectar señales
        self.conectar_senales()

    def crear_grupo_cotizacion(self, parent_layout):
        """Crear grupo de campos para datos de la cotización  """
        # Crear GroupBox para cotización
        grupo_cotizacion = QGroupBox("")
        grupo_cotizacion.setStyleSheet(GROUP_BOX_STYLE)
        
        # Layout horizontal para los campos
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Campo Folio de Cotización
        lbl_folio = QLabel("Folio Cotización")
        lbl_folio.setStyleSheet(LABEL_STYLE)
        self.txt_folio = QLineEdit()
        self.txt_folio.setStyleSheet(INPUT_STYLE + """
            QLineEdit {
                background-color: #E8E8E8;
                color: #666666;
            }
        """)
        self.txt_folio.setReadOnly(True)
        self.txt_folio.setPlaceholderText("COT-Auto") # Placeholder
        
        # Campo Cliente
        lbl_cliente = QLabel("Cliente")
        lbl_cliente.setStyleSheet(LABEL_STYLE)
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setStyleSheet(INPUT_STYLE)
        self.txt_cliente.setPlaceholderText("Escriba para buscar cliente...")
        
        # Campo Fecha de Cotización
        lbl_fecha = QLabel("Fecha Cotización")
        lbl_fecha.setStyleSheet(LABEL_STYLE)
        self.date_fecha = QDateEdit()
        self.date_fecha.setCalendarPopup(True)
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setDisplayFormat("dd/MM/yyyy")
        
        # Campo Vigencia con calendario
        lbl_vigencia = QLabel("Vigencia Hasta")
        lbl_vigencia.setStyleSheet(LABEL_STYLE)
        self.date_vigencia = QDateEdit()
        self.date_vigencia.setCalendarPopup(True)
        fecha_vigencia = QDate.currentDate().addDays(30)
        self.date_vigencia.setDate(fecha_vigencia)
        self.date_vigencia.setDisplayFormat("dd/MM/yyyy")
        
        # Campo Proyecto/Referencia
        lbl_proyecto = QLabel("Proyecto")
        lbl_proyecto.setStyleSheet(LABEL_STYLE)
        self.txt_proyecto = QLineEdit()
        self.txt_proyecto.setStyleSheet(INPUT_STYLE)
        self.txt_proyecto.setPlaceholderText("Nombre del proyecto")
        
        # Aplicar estilo común a ambos calendarios
        estilo_calendario = self._obtener_estilo_calendario()
        self.date_fecha.setStyleSheet(estilo_calendario)
        self.date_vigencia.setStyleSheet(estilo_calendario)
        
        # Agregar widgets al layout
        layout.addWidget(lbl_folio)
        layout.addWidget(self.txt_folio, 1)
        layout.addWidget(lbl_cliente)
        layout.addWidget(self.txt_cliente, 2)
        layout.addWidget(lbl_fecha)
        layout.addWidget(self.date_fecha, 1)
        layout.addWidget(lbl_vigencia)
        layout.addWidget(self.date_vigencia, 1)
        layout.addWidget(lbl_proyecto)
        layout.addWidget(self.txt_proyecto, 2)
        
        grupo_cotizacion.setLayout(layout)
        parent_layout.addWidget(grupo_cotizacion)

    def _obtener_estilo_calendario(self):
        """Retorna el estilo CSS común para los calendarios  """
        return """
            QDateEdit {
                padding: 8px;
                border: 2px solid #F5F5FF;
                border-radius: 6px;
                background-color: #F5F5FF;
                min-height: 25px;
                font-size: 16px;
                margin-top: 0px;
            }
            QDateEdit:focus {
                border: 2px solid #2CD5C4;
                background-color: white;
            }
            QDateEdit::drop-down {
                border: 0px;
                background: transparent;
                subcontrol-position: right center;
                width: 30px;
            }
            QDateEdit::down-arrow {
                image: url(assets/icons/calendario.png);
                width: 16px;
                height: 16px;
            }
            QCalendarWidget {
                background-color: white;
                border: 2px solid #00788E;
                border-radius: 8px;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #00788E;
                border: none;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #2CD5C4;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #00788E;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                border: 1px solid #00788E;
                border-radius: 4px;
                padding: 2px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                color: #333333;
                selection-background-color: #2CD5C4;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #999999;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #00788E;
                border-radius: 4px;
            }
        """

    def conectar_senales(self):
        """Conectar las señales de los controles (Fusionado)"""
        # UI connections
        self.txt_cantidad.textChanged.connect(self.calcular_importe)
        self.txt_precio.textChanged.connect(self.calcular_importe)
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        
        self.tabla_items.doubleClicked.connect(self.cargar_item_para_editar)
        
        self.date_fecha.dateChanged.connect(self.validar_fechas)
        self.date_vigencia.dateChanged.connect(self.validar_fechas)

        # Conexiones de botones principales
        self.botones[0].clicked.connect(self.nueva_cotizacion)
        self.botones[1].clicked.connect(self.guardar_cotizacion)
        # Botón "Cancelar"
        self.botones[2].clicked.connect(self.cancelar_cotizacion) 
        self.botones[3].clicked.connect(self.buscar_cotizacion)
        self.botones[4].clicked.connect(self.editar_cotizacion)
        # Botón "Limpiar"
        self.botones[5].clicked.connect(self.nueva_cotizacion)
        # self.botones[6] (Imprimir)
        # --- MODIFICACIÓN 2: Conectar el botón 7 ---
        self.botones[7].clicked.connect(self.generar_nota_desde_cotizacion) # Generar Nota

    def validar_fechas(self):
        """Valida que la fecha de vigencia sea posterior a la fecha de cotización  """
        fecha_cot = self.date_fecha.date()
        fecha_vig = self.date_vigencia.date()
        
        if fecha_vig <= fecha_cot:
            # Ajustar automáticamente la vigencia a 30 días después
            nueva_vigencia = fecha_cot.addDays(30)
            self.date_vigencia.setDate(nueva_vigencia)
    
    def crear_grupo_producto_servicio(self, parent_layout):
        """Crear grupo de campos para productos/servicios  """
        grupo = QGroupBox("")
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        # Crear un grid layout para organizar los campos
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Ajuste de columnas
        grid_layout.setColumnStretch(0, 1)    # Cantidad
        grid_layout.setColumnStretch(1, 6)    # Descripción
        grid_layout.setColumnStretch(2, 2)    # Precio
        grid_layout.setColumnStretch(3, 2)    # Importe
        grid_layout.setColumnStretch(4, 1)    # IVA
        grid_layout.setColumnStretch(5, 1)    # Botón
        
        # Labels
        lbl_cantidad = QLabel("Cantidad")
        lbl_cantidad.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_cantidad, 0, 0)
        
        lbl_descripcion = QLabel("Descripción")
        lbl_descripcion.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_descripcion, 0, 1)
        
        lbl_precio = QLabel("Precio Unitario")
        lbl_precio.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_precio, 0, 2)
        
        lbl_importe = QLabel("Importe")
        lbl_importe.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_importe, 0, 3)
        
        lbl_impuestos = QLabel("IVA %")
        lbl_impuestos.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_impuestos, 0, 4)
        
        # Campos de entrada
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setStyleSheet(INPUT_STYLE)
        self.txt_cantidad.setPlaceholderText("Cant.")
        self.txt_cantidad.setValidator(QDoubleValidator())
        grid_layout.addWidget(self.txt_cantidad, 1, 0)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Ingrese descripción del producto o servicio a cotizar")
        grid_layout.addWidget(self.txt_descripcion, 1, 1)
        
        self.txt_precio = QLineEdit()
        self.txt_precio.setStyleSheet(INPUT_STYLE)
        self.txt_precio.setPlaceholderText("$0.00")
        self.txt_precio.setValidator(QDoubleValidator(0.00, 9999999.99, 2))
        grid_layout.addWidget(self.txt_precio, 1, 2)
        
        self.txt_importe = QDoubleSpinBox()
        self.txt_importe.setReadOnly(True)
        self.txt_importe.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.txt_importe.setRange(0, 9999999.99)
        self.txt_importe.setDecimals(2)
        self.txt_importe.setPrefix("$ ")
        self.txt_importe.setStyleSheet(INPUT_STYLE)
        grid_layout.addWidget(self.txt_importe, 1, 3)
        
        self.txt_impuestos = QDoubleSpinBox()
        self.txt_impuestos.setRange(0, 100)
        self.txt_impuestos.setDecimals(2)
        self.txt_impuestos.setSuffix(" %")
        self.txt_impuestos.setValue(16.00)
        self.txt_impuestos.setStyleSheet(INPUT_STYLE)
        grid_layout.addWidget(self.txt_impuestos, 1, 4)
        
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setStyleSheet(FORM_BUTTON_STYLE)
        self.btn_agregar.setCursor(Qt.PointingHandCursor)
        grid_layout.addWidget(self.btn_agregar, 1, 5)
        
        # Establecer el layout del grupo
        grupo.setLayout(grid_layout)
        
        # Añadir el grupo al layout principal
        parent_layout.addWidget(grupo)
    
    def crear_tabla_items(self, parent_layout):
        """Crear tabla para mostrar los items cotizados  """
        # Crear modelo de datos
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels(["Cantidad", "Descripción", "Precio Unitario", "IVA", "Importe"])
        
        # Crear vista de tabla
        self.tabla_items = QTableView()
        self.tabla_items.setModel(self.tabla_model)
        self.tabla_items.horizontalHeader().setVisible(True)
        self.tabla_items.verticalHeader().setVisible(False)

        # Bloquear edición de celdas
        self.tabla_items.setEditTriggers(QTableView.NoEditTriggers)
        
        # Aplicar estilo para la tabla
        self.tabla_items.setStyleSheet(TABLE_STYLE)
        
        # Configurar ancho de columnas
        header = self.tabla_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Fijar altura del encabezado
        header.setFixedHeight(40)
        
        # Fijar altura de cada fila a 30px
        self.tabla_items.verticalHeader().setDefaultSectionSize(30)
        
        # Configurar comportamiento de selección
        self.tabla_items.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_items.setSelectionMode(QTableView.SingleSelection)
        
        # Habilitar menú contextual
        self.tabla_items.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_items.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        
        # Establecer altura
        self.tabla_items.setMinimumHeight(15 * 30 + 40)
        
        # Agregar al layout
        parent_layout.addWidget(self.tabla_items)

    # ===================================================================
    # = MÉTODOS DE BD
    # ===================================================================

    def guardar_cotizacion(self):
        """Guardar cotización"""
        # Validar cliente
        nombre_cliente = self.txt_cliente.text()
        cliente_id = self.clientes_dict.get(nombre_cliente)
        
        if not cliente_id:
            self.mostrar_advertencia("Seleccione un cliente válido de la lista")
            return
        
        # Validar items
        if self.tabla_model.rowCount() == 0:
            self.mostrar_advertencia("Agregue al menos un item")
            return
        
        try:
            cotizacion_data = {
                'cliente_id': cliente_id,  # Usar ID validado
                'estado': 'Pendiente',
                'vigencia': self.date_vigencia.date().toString("dd/MM/yyyy"),
                'observaciones': self.txt_proyecto.text()
            }
            
            # Preparar items (solo normales)
            items = []
            for fila in range(self.tabla_model.rowCount()):
                if self.tipo_por_fila.get(fila, 'normal') != 'normal':
                    continue
                
                items.append({
                    'cantidad': int(self.tabla_model.item(fila, 0).text()),
                    'descripcion': self.tabla_model.item(fila, 1).text(),
                    'precio_unitario': float(self.tabla_model.item(fila, 2).text().replace('$', '').replace(',', '')),
                    'importe': float(self.tabla_model.item(fila, 4).text().replace('$', '').replace(',', '')),
                    'impuesto': self.iva_por_fila.get(fila, 16.0)
                })
            
            if self.modo_edicion and self.cotizacion_actual_id:
                cotizacion = db_helper.actualizar_cotizacion(self.cotizacion_actual_id, cotizacion_data, items)
                mensaje = "Cotización actualizada"
            else:
                cotizacion = db_helper.crear_cotizacion(cotizacion_data, items)
                mensaje = "Cotización guardada"
            
            if cotizacion:
                self.mostrar_exito(f"{mensaje}: {cotizacion['folio']}")
                self.txt_folio.setText(cotizacion['folio'])
                self.cotizacion_actual_id = cotizacion['id']
                self.modo_edicion = False
                self.controlar_estado_campos(False) # Deshabilita campos
            else:
                self.mostrar_error("No se pudo guardar")
            
        except Exception as e:
            self.mostrar_error(f"Error: {e}")

    def nueva_cotizacion(self):
        """Limpiar para nueva (Adaptado)"""
        self.cotizacion_actual_id = None
        self.modo_edicion = False
        self.txt_folio.clear()
        self.txt_folio.setPlaceholderText("COT-Auto")
        
        # Limpiar campos de la UI original
        self.txt_cliente.clear()
        self.txt_proyecto.clear()
        self.date_fecha.setDate(QDate.currentDate())
        self.date_vigencia.setDate(QDate.currentDate().addDays(30))
        
        self.tabla_model.setRowCount(0)
        self.iva_por_fila.clear()
        self.tipo_por_fila.clear()
        
        self.limpiar_formulario_items()
        self.calcular_totales()
        self.controlar_estado_campos(True) # Habilita campos
        self.modo_edicion = True # Modo edición se activa para una nueva

    def buscar_cotizacion(self):
        """Buscar cotización  """
        folio, ok = QInputDialog.getText(self, "Buscar Cotización", "Ingrese el Folio:")
        
        if ok and folio:
            try:
                # Asumimos que db_helper puede buscar por folio o id
                cotizaciones = db_helper.buscar_cotizaciones(folio=folio)
                if cotizaciones:
                    self.cargar_cotizacion_en_formulario(cotizaciones[0])
                    self.mostrar_exito("Cotización cargada. Presione 'Editar' para modificar.")
                else:
                    self.mostrar_advertencia("Cotización no encontrada")
            except Exception as e:
                self.mostrar_error(f"Error al buscar: {e}")

    def cargar_cotizacion_en_formulario(self, cotizacion):
        """Cargar en formulario"""
        self.nueva_cotizacion() # Limpia todo primero (y habilita campos)
        
        # Se asigna el ID y el modo_edicion ANTES de llamar a controlar_estado_campos
        self.cotizacion_actual_id = cotizacion['id']
        self.modo_edicion = False
        
        self.controlar_estado_campos(False) # Bloquea campos, pero ahora SÍ habilitará "Editar"

        self.txt_folio.setText(cotizacion['folio'])
        # Cargar datos en los widgets
        self.txt_cliente.setText(cotizacion.get('cliente_nombre', ''))
        self.txt_proyecto.setText(cotizacion.get('observaciones', ''))
        
        if cotizacion.get('created_at'): # Usar 'created_at' para la fecha de la cotización
             try:
                 # Asumir formato ISO 8601 o similar si viene de BD
                 fecha_dt = datetime.fromisoformat(cotizacion['created_at'])
                 self.date_fecha.setDate(QDate(fecha_dt.year, fecha_dt.month, fecha_dt.day))
             except (ValueError, TypeError):
                 # Fallback por si el formato es dd/MM/yyyy
                 try:
                     self.date_fecha.setDate(QDate.fromString(cotizacion['created_at'].split(' ')[0], "dd/MM/yyyy"))
                 except:
                     self.date_fecha.setDate(QDate.currentDate()) # Fallback final
        
        if cotizacion.get('vigencia'):
            self.date_vigencia.setDate(QDate.fromString(cotizacion['vigencia'], "dd/MM/yyyy"))

        # Cargar cliente por ID
        for nombre, id_cliente in self.clientes_dict.items():
            if id_cliente == cotizacion['cliente_id']:
                self.txt_cliente.setText(nombre)
                break
        
        self.tabla_model.setRowCount(0)
        self.iva_por_fila.clear()
        self.tipo_por_fila.clear()
        
        # Reconstruir la tabla
        items_ordenados = cotizacion.get('items', [])
        
        # Detectar si hay items con 'tipo'
        if any('tipo' in item for item in items_ordenados):
            items_ordenados = sorted(items_ordenados, key=lambda x: x.get('orden', 0))
        
        for item in items_ordenados:
            tipo = item.get('tipo', 'normal')
            fila = self.tabla_model.rowCount()

            if tipo == 'normal':
                self._agregar_item_tabla(
                    str(item['cantidad']),
                    item['descripcion'],
                    item['precio_unitario'],
                    item['impuesto']
                )
            else:
                # Cargar nota, sección o condiciones
                item_especial = QStandardItem(item['descripcion'])
                self.tabla_model.insertRow(fila)
                self.tabla_model.setItem(fila, 0, item_especial)
                self.tabla_items.setSpan(fila, 0, 1, 5)
                self.tipo_por_fila[fila] = tipo
                
                if tipo == 'nota':
                    item_especial.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    item_especial.setBackground(QColor(245, 245, 245))
                    item_especial.setForeground(QColor(100, 100, 100))
                elif tipo == 'seccion':
                    item_especial.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    item_especial.setBackground(QColor(0, 120, 142, 30))
                    item_especial.setForeground(QColor(0, 120, 142))
                    font = item_especial.font(); font.setBold(True); font.setPointSize(10)
                    item_especial.setFont(font)
                elif tipo == 'condiciones':
                    item_especial.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    item_especial.setBackground(QColor(255, 250, 205))
                    item_especial.setForeground(QColor(50, 50, 50))
                    self.tabla_items.setRowHeight(fila, 80)

        self.calcular_totales()
        
        # Si la cotización ya fue Aceptada, deshabilitar "Generar Nota"
        if cotizacion.get('estado') == 'Aceptada' or cotizacion.get('nota_folio'):
            self.botones[7].setEnabled(False)
            if cotizacion.get('nota_folio'):
                self.botones[7].setToolTip(f"Ya se generó la nota: {cotizacion['nota_folio']}")
            else:
                self.botones[7].setToolTip("Esta cotización ya fue convertida a nota.")
        else:
            self.botones[7].setEnabled(True)
            self.botones[7].setToolTip("Generar Nota de Venta a partir de esta cotización.")


    def _agregar_item_tabla(self, cantidad, descripcion, precio, iva_porcentaje):
        """Helper agregar item   - Adaptado para tabla UI"""
        cantidad_num = float(cantidad)
        importe = cantidad_num * precio
        
        item_cantidad = QStandardItem(cantidad)
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        item_descripcion = QStandardItem(descripcion)
        item_descripcion.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        item_precio = QStandardItem(f"${precio:.2f}")
        item_precio.setTextAlignment(Qt.AlignCenter)
        item_iva = QStandardItem(f"{iva_porcentaje:.1f} %")
        item_iva.setTextAlignment(Qt.AlignCenter)
        item_importe = QStandardItem(f"${importe:.2f}")
        item_importe.setTextAlignment(Qt.AlignCenter)
        
        fila = self.tabla_model.rowCount()
        self.tabla_model.appendRow([item_cantidad, item_descripcion, item_precio, item_iva, item_importe])
        self.iva_por_fila[fila] = iva_porcentaje
        self.tipo_por_fila[fila] = 'normal'

    def editar_cotizacion(self):
        """Habilitar edición  """
        if not self.cotizacion_actual_id:
            self.mostrar_advertencia("Primero busque y cargue una cotización para editar.")
            return
        
        # No permitir editar una cotización ya Aceptada
        cotizacion = db_helper.buscar_cotizaciones(folio=self.txt_folio.text())[0]
        if cotizacion.get('estado') == 'Aceptada':
            self.mostrar_advertencia("No se puede editar una cotización que ya fue aceptada y convertida a nota.")
            return

        self.modo_edicion = True
        self.controlar_estado_campos(True)

        if hasattr(self, 'botones') and len(self.botones) > 1:
            self.botones[1].setText("Actualizar") 

    def cancelar_cotizacion(self):
        """Cancelar cotización en BD y limpiar formulario"""
        if not self.cotizacion_actual_id:
            self.mostrar_advertencia("No hay cotización para cancelar")
            return
        
        respuesta = QMessageBox.question(
            self, 
            "Confirmar Cancelación", 
            f"¿Cancelar la cotización {self.txt_folio.text()}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            if db_helper.cancelar_cotizacion(self.cotizacion_actual_id):
                self.mostrar_exito("Cotización cancelada")
                self.nueva_cotizacion()
            else:
                self.mostrar_error("No se pudo cancelar (puede estar ya cancelada)")
                
    def controlar_estado_campos(self, habilitar):
        """Habilitar/deshabilitar campos"""
        # Campos de encabezado
        self.txt_cliente.setEnabled(habilitar)
        self.txt_proyecto.setEnabled(habilitar)
        self.date_fecha.setEnabled(habilitar)
        self.date_vigencia.setEnabled(habilitar)

        # Campos de formulario de items
        self.txt_cantidad.setEnabled(habilitar)
        self.txt_descripcion.setEnabled(habilitar)
        self.txt_precio.setEnabled(habilitar)
        self.txt_impuestos.setEnabled(habilitar)
        self.btn_agregar.setEnabled(habilitar)

        if habilitar:
            self.tabla_items.setEditTriggers(QTableView.DoubleClicked)
        else:
            self.tabla_items.setEditTriggers(QTableView.NoEditTriggers)

        # Control de botones principales
        self.botones[0].setEnabled(True) # Nueva (siempre activa)
        self.botones[1].setEnabled(habilitar) # Guardar
        self.botones[2].setEnabled(True) # Cancelar (ahora siempre activa, como en Notas)
        self.botones[3].setEnabled(True) # Buscar (siempre activo)
        # Editar solo se habilita si hay una cotización cargada Y no estamos en modo edición
        self.botones[4].setEnabled(bool(self.cotizacion_actual_id) and not habilitar) 
        self.botones[5].setEnabled(True) # Limpiar (siempre activo)
        # Imprimir/Generar Nota solo si hay una cotización cargada
        self.botones[6].setEnabled(bool(self.cotizacion_actual_id)) # Imprimir
        self.botones[7].setEnabled(bool(self.cotizacion_actual_id)) # Generar Nota

        # Si estamos deshabilitando campos (ej. al cargar) Y hay una cotización
        if not habilitar and self.cotizacion_actual_id:
            try:
                cotizacion = db_helper.buscar_cotizaciones(folio=self.txt_folio.text())[0]
                if cotizacion.get('estado') == 'Aceptada' or cotizacion.get('nota_folio'):
                    self.botones[7].setEnabled(False)
                    if cotizacion.get('nota_folio'):
                        self.botones[7].setToolTip(f"Ya se generó la nota: {cotizacion['nota_folio']}")
            except:
                pass


    def cargar_clientes_autocompletado(self):
        """Cargar clientes y configurar autocompletado"""
        try:
            clientes = db_helper.get_clientes()
            self.clientes_dict.clear()
            
            nombres = []
            for cliente in clientes:
                nombre_completo = f"{cliente['nombre']} - {cliente['tipo']}"
                nombres.append(nombre_completo)
                self.clientes_dict[nombre_completo] = cliente['id']
            
            completer = QCompleter(nombres)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.setMaxVisibleItems(9)
            completer.popup().setStyleSheet("""
                QListView {
                    background-color: white;
                    border: 2px solid #2CD5C4;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 16px;
                    min-height: 60px;
                }
                QListView::item {
                    padding: 10px;
                    border-radius: 3px;
                    min-height: 30px;
                }
                QListView::item:hover {
                    background-color: #E0F7FA;
                }
                QListView::item:selected {
                    background-color: #2CD5C4;
                    color: white;
                }
            """)
            
            self.txt_cliente.setCompleter(completer)
            
        except Exception as e:
            print(f"Error al cargar clientes: {e}")

    # ===================================================================
    # = MÉTODO NUEVO PARA GENERAR NOTA
    # ===================================================================
    
    def generar_nota_desde_cotizacion(self):
        """
        Toma la cotización actual y genera una Nota de Venta.
        """
        # Validar que hay una cotización cargada
        if not self.cotizacion_actual_id:
            self.mostrar_advertencia("Cargue una cotización guardada antes de generar la nota.")
            return
        
        # Validar que no tenga ya una nota generada
        cotizacion_actual = db_helper.buscar_cotizaciones(folio=self.txt_folio.text())[0]
        if cotizacion_actual.get('nota_folio'):
            self.mostrar_advertencia(
                f"Esta cotización ya generó la nota: {cotizacion_actual['nota_folio']}\n"
                "No se puede generar otra nota."
            )
            return  

        # Validar el cliente
        nombre_cliente = self.txt_cliente.text()
        cliente_id = self.clientes_dict.get(nombre_cliente)
        
        if not cliente_id:
            self.mostrar_advertencia("Cliente no válido. Seleccione un cliente de la lista.")
            return
            
        # Preparar datos para la Nota de Venta
        try:
            # Fecha: La del día actual
            fecha_hoy = QDate.currentDate().toPyDate()
            # Referencia: Tomada del campo 'Proyecto'
            referencia = self.txt_proyecto.text()

            nota_data = {
                'cliente_id': cliente_id,
                'fecha': fecha_hoy,
                'observaciones': referencia, # 'observaciones' en la nota
                'metodo_pago': None # Las notas nuevas inician sin método de pago
            }

            # Preparar los items
            items_para_nota = []
            for fila in range(self.tabla_model.rowCount()):
                tipo = self.tipo_por_fila.get(fila, 'normal')
                
                # Solo transferir items 'normales' (ignorar notas, secciones)
                if tipo == 'normal':
                    cantidad = int(self.tabla_model.item(fila, 0).text())
                    descripcion = self.tabla_model.item(fila, 1).text()
                    precio_unitario = float(self.tabla_model.item(fila, 2).text().replace('$', '').replace(',', ''))
                    impuesto_porcentaje = self.iva_por_fila.get(fila, 16.0)
                    importe = cantidad * precio_unitario
                    
                    items_para_nota.append({
                        'cantidad': cantidad,
                        'descripcion': descripcion,
                        'precio_unitario': precio_unitario,
                        'importe': importe,
                        'impuesto': impuesto_porcentaje
                    })

            if not items_para_nota:
                self.mostrar_advertencia("La cotización no tiene items para transferir a la nota.")
                return

            # Llamar al db_helper para crear la nota
            nueva_nota = db_helper.crear_nota(nota_data, items_para_nota, cotizacion_folio=self.txt_folio.text())
            
            if nueva_nota and nueva_nota.get('folio'):
                # Actualizar cotización con vinculación
                cotizacion_data_update = {
                    'cliente_id': cliente_id,
                    'estado': 'Aceptada',
                    'vigencia': self.date_vigencia.date().toString("dd/MM/yyyy"),
                    'observaciones': self.txt_proyecto.text()
                }
                
                db_helper.actualizar_cotizacion(
                    self.cotizacion_actual_id, 
                    cotizacion_data_update, 
                    items_para_nota,
                    nota_folio=nueva_nota['folio']  # ← Vincular
                )
                
                self.mostrar_exito(
                    f"Nota generada: {nueva_nota['folio']}\n"
                    f"Desde cotización: {self.txt_folio.text()}"
                )
                
        except Exception as e:
            self.mostrar_error(f"Error al crear la nota: {e}")
            import traceback
            traceback.print_exc()

    # ===================================================================
    # = MÉTODOS MENÚ CONTEXTUAL Y TABLA
    # ===================================================================
    
    def mostrar_menu_contextual(self, position):
        """Muestra un menú contextual al hacer clic derecho en una fila de la tabla  """
        # Solo mostrar menú si estamos en modo edición
        if not self.modo_edicion:
            return
            
        indexes = self.tabla_items.selectedIndexes()
        
        menu = QMenu(self)
        
        # Opciones de insertar (siempre disponibles en modo edición)
        menu.addSection("Insertar")
        action_nota = QAction("➕ Agregar Nota", self)
        action_nota.triggered.connect(self.insertar_nota)
        menu.addAction(action_nota)
        
        action_seccion = QAction("📁 Agregar Sección", self)
        action_seccion.triggered.connect(self.insertar_seccion)
        menu.addAction(action_seccion)
        
        action_condiciones = QAction("📋 Agregar Condiciones", self)
        action_condiciones.triggered.connect(self.insertar_condiciones)
        menu.addAction(action_condiciones)
        
        menu.addSeparator()
        
        if indexes:
            fila = indexes[0].row()
            tipo_fila = self.tipo_por_fila.get(fila, 'normal')
            
            menu.addSection("Acciones de Fila")
            
            # Opción de editar (para items 'normal' se usa doble clic)
            if tipo_fila in ['nota', 'seccion', 'condiciones']:
                action_editar = QAction("✏️ Editar", self)
                action_editar.triggered.connect(lambda: self.editar_elemento_especial(fila))
                menu.addAction(action_editar)
            elif tipo_fila == 'normal':
                action_editar_item = QAction("✏️ Editar Item", self)
                action_editar_item.triggered.connect(lambda: self.cargar_item_para_editar(indexes[0]))
                menu.addAction(action_editar_item)

            menu.addSeparator()
            
            es_primera_fila = (fila == 0)
            es_ultima_fila = (fila == self.tabla_model.rowCount() - 1)
            
            action_subir = QAction("Mover Arriba", self)
            action_subir.setEnabled(not es_primera_fila)
            action_subir.triggered.connect(lambda: self.mover_fila_arriba(fila))
            menu.addAction(action_subir)
            
            action_bajar = QAction("Mover Abajo", self)
            action_bajar.setEnabled(not es_ultima_fila)
            action_bajar.triggered.connect(lambda: self.mover_fila_abajo(fila))
            menu.addAction(action_bajar)
            
            menu.addSeparator()
            
            action_eliminar = QAction("Eliminar", self)
            action_eliminar.triggered.connect(lambda: self.eliminar_fila(fila))
            menu.addAction(action_eliminar)
        
        menu.exec_(self.tabla_items.viewport().mapToGlobal(position))

    def insertar_nota(self):
        """Inserta una fila de tipo nota  """
        texto, ok = QInputDialog.getText(
            self, "Agregar Nota", "Ingrese el texto de la nota:", QLineEdit.Normal, ""
        )
        if ok and texto:
            fila = self.tabla_model.rowCount()
            self.tabla_model.insertRow(fila)
            
            item_nota = QStandardItem(f"📝 {texto}")
            item_nota.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_nota.setBackground(QColor(245, 245, 245))
            item_nota.setForeground(QColor(100, 100, 100))
            
            self.tabla_model.setItem(fila, 0, item_nota)
            self.tabla_items.setSpan(fila, 0, 1, 5)
            self.tipo_por_fila[fila] = 'nota'
            self.calcular_totales()

    def insertar_seccion(self):
        """Inserta una fila de tipo sección  """
        texto, ok = QInputDialog.getText(
            self, "Agregar Sección", "Nombre de la sección:", QLineEdit.Normal, ""
        )
        if ok and texto:
            fila = self.tabla_model.rowCount()
            self.tabla_model.insertRow(fila)
            
            item_seccion = QStandardItem(texto.upper())
            item_seccion.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_seccion.setBackground(QColor(0, 120, 142, 30))
            item_seccion.setForeground(QColor(0, 120, 142))
            
            font = item_seccion.font(); font.setBold(True); font.setPointSize(10)
            item_seccion.setFont(font)
            
            self.tabla_model.setItem(fila, 0, item_seccion)
            self.tabla_items.setSpan(fila, 0, 1, 5)
            self.tipo_por_fila[fila] = 'seccion'
            self.calcular_totales()

    def insertar_condiciones(self):
        """Inserta condiciones comerciales  """
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar Condiciones Comerciales")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        label = QLabel("Ingrese las condiciones comerciales:")
        layout.addWidget(label)
        
        text_edit = QTextEdit()
        text_edit.setPlainText("• Tiempo de entrega: \n• Forma de pago: \n• Garantía: ")
        layout.addWidget(text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            texto = text_edit.toPlainText()
            if texto:
                fila = self.tabla_model.rowCount()
                self.tabla_model.insertRow(fila)
                
                item_condiciones = QStandardItem(f"📋 CONDICIONES COMERCIALES:\n{texto}")
                item_condiciones.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                item_condiciones.setBackground(QColor(255, 250, 205))
                item_condiciones.setForeground(QColor(50, 50, 50))
                
                self.tabla_model.setItem(fila, 0, item_condiciones)
                self.tabla_items.setSpan(fila, 0, 1, 5)
                self.tipo_por_fila[fila] = 'condiciones'
                self.tabla_items.setRowHeight(fila, 80)
                self.calcular_totales()

    def editar_elemento_especial(self, fila):
        """Edita una nota, sección o condiciones existente  """
        tipo = self.tipo_por_fila.get(fila, 'normal')
        if tipo == 'normal': return
        
        item_actual = self.tabla_model.item(fila, 0)
        if not item_actual: return
        
        texto_actual = item_actual.text()
        
        if tipo == 'nota':
            texto_actual = texto_actual.replace("📝 ", "")
            texto_nuevo, ok = QInputDialog.getText(
                self, "Editar Nota", "Modifique el texto de la nota:", QLineEdit.Normal, texto_actual
            )
            if ok and texto_nuevo:
                item_actual.setText(f"📝 {texto_nuevo}")
                
        elif tipo == 'seccion':
            texto_nuevo, ok = QInputDialog.getText(
                self, "Editar Sección", "Modifique el nombre de la sección:", QLineEdit.Normal, texto_actual
            )
            if ok and texto_nuevo:
                item_actual.setText(texto_nuevo.upper())
                
        elif tipo == 'condiciones':
            texto_actual = texto_actual.replace("📋 CONDICIONES COMERCIALES:\n", "")
            dialog = QDialog(self)
            dialog.setWindowTitle("Editar Condiciones Comerciales")
            dialog.setMinimumWidth(500)
            layout = QVBoxLayout()
            label = QLabel("Modifique las condiciones comerciales:")
            layout.addWidget(label)
            text_edit = QTextEdit()
            text_edit.setPlainText(texto_actual)
            layout.addWidget(text_edit)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                texto_nuevo = text_edit.toPlainText()
                if texto_nuevo:
                    item_actual.setText(f"📋 CONDICIONES COMERCIALES:\n{texto_nuevo}")
    
    def mover_fila_arriba(self, fila):
        """Mover fila hacia arriba  """
        if fila <= 0: return
        self._intercambiar_filas(fila, fila - 1)
        self.tabla_items.selectRow(fila - 1)
        self.calcular_totales()
    
    def mover_fila_abajo(self, fila):
        """Mover fila hacia abajo  """
        if fila >= self.tabla_model.rowCount() - 1: return
        self._intercambiar_filas(fila, fila + 1)
        self.tabla_items.selectRow(fila + 1)
        self.calcular_totales()
    
    def _intercambiar_filas(self, fila1, fila2):
        """Helper para mover filas  """
        for col in range(self.tabla_model.columnCount()):
            item1 = self.tabla_model.takeItem(fila1, col)
            item2 = self.tabla_model.takeItem(fila2, col)
            self.tabla_model.setItem(fila1, col, item2)
            self.tabla_model.setItem(fila2, col, item1)
        
        temp_iva = self.iva_por_fila.get(fila1, 16.0)
        self.iva_por_fila[fila1] = self.iva_por_fila.get(fila2, 16.0)
        self.iva_por_fila[fila2] = temp_iva
        
        temp_tipo = self.tipo_por_fila.get(fila1, 'normal')
        self.tipo_por_fila[fila1] = self.tipo_por_fila.get(fila2, 'normal')
        self.tipo_por_fila[fila2] = temp_tipo
        
        # Restaurar spans y alturas
        for fila in [fila1, fila2]:
            tipo = self.tipo_por_fila.get(fila, 'normal')
            if tipo in ['nota', 'seccion', 'condiciones']:
                self.tabla_items.setSpan(fila, 0, 1, 5)
                if tipo == 'condiciones': self.tabla_items.setRowHeight(fila, 80)
                else: self.tabla_items.setRowHeight(fila, 30)
            else:
                self.tabla_items.setSpan(fila, 0, 1, 1)
                for col in range(1, 5): self.tabla_items.setSpan(fila, col, 1, 1)
                self.tabla_items.setRowHeight(fila, 30)
    
    def eliminar_fila(self, fila):
        """Elimina una fila de la tabla"""
        msg_box = QMessageBox(QMessageBox.Question, 
                            "Confirmar", "¿Eliminar este elemento?", 
                            QMessageBox.Yes | QMessageBox.No, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.tabla_model.removeRow(fila)
            
            # Reorganizar índices del diccionario IVA y tipos
            nuevo_iva = {}
            nuevo_tipo = {}
            
            for key in range(self.tabla_model.rowCount()):
                if key < fila:
                    nuevo_iva[key] = self.iva_por_fila.get(key, 16.0)
                    nuevo_tipo[key] = self.tipo_por_fila.get(key, 'normal')
                else:
                    nuevo_iva[key] = self.iva_por_fila.get(key + 1, 16.0)
                    nuevo_tipo[key] = self.tipo_por_fila.get(key + 1, 'normal')
            
            self.iva_por_fila = nuevo_iva
            self.tipo_por_fila = nuevo_tipo
            
            self.calcular_totales()
            
            if fila == self.fila_en_edicion:
                self.limpiar_formulario_items()
    
    def calcular_importe(self):
        """Calcular el importe  """
        try:
            cantidad = float(self.txt_cantidad.text()) if self.txt_cantidad.text() else 0
            precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
            precio = float(precio_texto) if precio_texto else 0
            
            importe = cantidad * precio
            self.txt_importe.setValue(importe)
            
            if precio > 0 and not self.txt_precio.hasFocus():
                self.txt_precio.setText(f"${precio:.2f}")
        except ValueError:
            self.txt_importe.setValue(0)
    
    def calcular_totales(self):
        """Calcula y actualiza los totales  """
        subtotal = 0.0
        total_impuestos = 0.0
        
        for fila in range(self.tabla_model.rowCount()):
            if self.tipo_por_fila.get(fila, 'normal') != 'normal':
                continue
                
            importe_item = self.tabla_model.item(fila, 4)
            if importe_item:
                importe_texto = importe_item.text()
                importe = float(importe_texto.replace("$", "").replace(",", "").strip())
                iva_porcentaje = self.iva_por_fila.get(fila, 16.0)
                iva_monto = importe * (iva_porcentaje / 100)
                
                subtotal += importe
                total_impuestos += iva_monto
        
        total = subtotal + total_impuestos
        
        self.lbl_subtotal_valor.setText(f"$ {subtotal:,.2f}")
        self.lbl_impuestos_valor.setText(f"$ {total_impuestos:,.2f}")
        self.lbl_total_valor.setText(f"$ {total:,.2f}")
    
    def crear_panel_totales(self, parent_layout):
        """Crear panel para mostrar totales  """
        contenedor_principal = QWidget()
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.addStretch(6)
        
        contenedor_frame = QWidget()
        contenedor_frame.setMaximumWidth(9999)
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        totales_frame = QFrame()
        totales_frame.setFrameStyle(QFrame.StyledPanel)
        totales_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 250),
                    stop: 1 rgba(245, 245, 245, 250)
                );
                border: 1px solid rgba(0, 120, 142, 0.2);
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
            }
        """)
        
        main_totales_layout = QHBoxLayout()
        main_totales_layout.addStretch()
        
        totales_grid = QGridLayout()
        totales_grid.setSpacing(5)
        totales_grid.setContentsMargins(0, 0, 0, 0)
        
        label_style = "QLabel { font-size: 18px; color: #333333; background: transparent; padding: 2px; }"
        label_bold_style = label_style + "font-weight: bold;"
        
        lbl_subtotal_text = QLabel("Subtotal:")
        lbl_subtotal_text.setStyleSheet(label_style)
        lbl_subtotal_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.lbl_subtotal_valor = QLabel("$ 0.00")
        self.lbl_subtotal_valor.setStyleSheet(label_bold_style)
        self.lbl_subtotal_valor.setAlignment(Qt.AlignRight)
        
        lbl_impuestos_text = QLabel("Impuestos:")
        lbl_impuestos_text.setStyleSheet(label_style)
        lbl_impuestos_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.lbl_impuestos_valor = QLabel("$ 0.00")
        self.lbl_impuestos_valor.setStyleSheet(label_bold_style)
        self.lbl_impuestos_valor.setAlignment(Qt.AlignRight)
        
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: rgba(0, 120, 142, 0.3); max-height: 1px;")
        
        lbl_total_text = QLabel("Total:")
        lbl_total_text.setStyleSheet(label_style + "font-size: 18px; font-weight: bold;")
        lbl_total_text.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        self.lbl_total_valor = QLabel("$ 0.00")
        self.lbl_total_valor.setStyleSheet("""
            QLabel { font-size: 18px; font-weight: bold; color: #00788E; background: transparent; padding: 2px; }
        """)
        self.lbl_total_valor.setAlignment(Qt.AlignRight)
        
        totales_grid.addWidget(lbl_subtotal_text, 0, 0)
        totales_grid.addWidget(self.lbl_subtotal_valor, 0, 1)
        totales_grid.addWidget(lbl_impuestos_text, 1, 0)
        totales_grid.addWidget(self.lbl_impuestos_valor, 1, 1)
        totales_grid.addWidget(linea, 2, 0, 1, 2)
        totales_grid.addWidget(lbl_total_text, 3, 0)
        totales_grid.addWidget(self.lbl_total_valor, 3, 1)
        
        totales_grid.setColumnMinimumWidth(0, 80)
        totales_grid.setColumnMinimumWidth(1, 120)
        
        totales_container = QWidget()
        totales_container.setLayout(totales_grid)
        totales_container.setFixedWidth(220)
        
        main_totales_layout.addWidget(totales_container)
        totales_frame.setLayout(main_totales_layout)
        
        frame_layout.addWidget(totales_frame)
        contenedor_frame.setLayout(frame_layout)
        
        layout_principal.addWidget(contenedor_frame, 1)
        contenedor_principal.setLayout(layout_principal)
        parent_layout.addWidget(contenedor_principal)
    
    def agregar_a_tabla(self):
        """Agrega los datos del formulario a la tabla  """
        if not self.validar_datos():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        precio = float(precio_texto)
        precio_formateado = f"${precio:.2f}"
        cantidad_calculo = float(cantidad) if cantidad else 1
        importe = cantidad_calculo * precio
        importe_formateado = f"${importe:.2f}"
        iva_porcentaje = self.txt_impuestos.value()
        iva_texto = f"{iva_porcentaje:.1f} %"
        
        item_cantidad = QStandardItem(cantidad)
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        item_descripcion = QStandardItem(descripcion)
        item_descripcion.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        item_precio = QStandardItem(precio_formateado)
        item_precio.setTextAlignment(Qt.AlignCenter)
        item_iva = QStandardItem(iva_texto)
        item_iva.setTextAlignment(Qt.AlignCenter)
        item_importe = QStandardItem(importe_formateado)
        item_importe.setTextAlignment(Qt.AlignCenter)
        
        fila = self.tabla_model.rowCount()
        self.tabla_model.insertRow(fila)
        
        self.tabla_model.setItem(fila, 0, item_cantidad)
        self.tabla_model.setItem(fila, 1, item_descripcion)
        self.tabla_model.setItem(fila, 2, item_precio)
        self.tabla_model.setItem(fila, 3, item_iva)
        self.tabla_model.setItem(fila, 4, item_importe)
        
        self.iva_por_fila[fila] = iva_porcentaje
        self.tipo_por_fila[fila] = 'normal' # Marcar como normal
        
        self.calcular_totales()
        self.limpiar_formulario_items()
        self.tabla_items.selectRow(fila)
    
    def cargar_item_para_editar(self, index):
        """Carga los datos de la fila   - con chequeo de modo_edicion"""
        if not self.modo_edicion:
            return
            
        fila = index.row()
        tipo_fila = self.tipo_por_fila.get(fila, 'normal')
        
        if tipo_fila in ['nota', 'seccion', 'condiciones']:
            self.editar_elemento_especial(fila)
            return
        
        cantidad = self.tabla_model.index(fila, 0).data()
        descripcion = self.tabla_model.index(fila, 1).data()
        precio = self.tabla_model.index(fila, 2).data()
        precio = precio.replace("$", "").replace(",", "").strip()
        
        self.txt_cantidad.setText(cantidad)
        self.txt_descripcion.setText(descripcion)
        self.txt_precio.setText(precio)

        if fila in self.iva_por_fila:
            self.txt_impuestos.setValue(self.iva_por_fila[fila])
        else:
            self.txt_impuestos.setValue(16.0)
        
        self.fila_en_edicion = fila
        
        self.btn_agregar.setText("Actualizar")
        try: self.btn_agregar.clicked.disconnect()
        except TypeError: pass
        self.btn_agregar.clicked.connect(self.actualizar_item)
    
    def actualizar_item(self):
        """Actualiza el item en edición  """
        if not self.validar_datos():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        precio = float(precio_texto)
        precio_formateado = f"${precio:.2f}"
        cantidad_calculo = float(cantidad) if cantidad else 1
        importe = cantidad_calculo * precio
        importe_formateado = f"${importe:.2f}"
        iva_texto = f"{self.txt_impuestos.value():.1f} %"
        
        self.tabla_model.setItem(self.fila_en_edicion, 0, QStandardItem(cantidad))
        self.tabla_model.setItem(self.fila_en_edicion, 1, QStandardItem(descripcion))
        self.tabla_model.setItem(self.fila_en_edicion, 2, QStandardItem(precio_formateado))
        self.tabla_model.setItem(self.fila_en_edicion, 3, QStandardItem(iva_texto))
        self.tabla_model.setItem(self.fila_en_edicion, 4, QStandardItem(importe_formateado))

        self.iva_por_fila[self.fila_en_edicion] = self.txt_impuestos.value()
        
        # Restaurar alineaciones
        self.tabla_model.item(self.fila_en_edicion, 0).setTextAlignment(Qt.AlignCenter)
        self.tabla_model.item(self.fila_en_edicion, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tabla_model.item(self.fila_en_edicion, 2).setTextAlignment(Qt.AlignCenter)
        self.tabla_model.item(self.fila_en_edicion, 3).setTextAlignment(Qt.AlignCenter)
        self.tabla_model.item(self.fila_en_edicion, 4).setTextAlignment(Qt.AlignCenter)
        
        self.calcular_totales()
        self.limpiar_formulario_items()
    
    # ===================================================================
    # = HELPERS
    # ===================================================================

    def mostrar_advertencia(self, mensaje):
        """Muestra un mensaje de advertencia  """
        msg_box = QMessageBox(QMessageBox.Warning, "Advertencia", mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()
    
    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito  """
        QMessageBox.information(self, "Éxito", mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error  """
        msg = QMessageBox(QMessageBox.Critical, "Error", mensaje, QMessageBox.Ok, self)
        msg.setStyleSheet(MESSAGE_BOX_STYLE)
        msg.exec_()

    def validar_datos(self):
        """Valida los datos del formulario de items  """
        if not self.txt_cantidad.text() or self.txt_cantidad.text() == "0":
            self.mostrar_advertencia("Ingrese una cantidad válida.")
            return False
        
        if not self.txt_descripcion.text():
            self.mostrar_advertencia("Ingrese una descripción.")
            return False
        
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        if not precio_texto or float(precio_texto) <= 0:
            self.mostrar_advertencia("Ingrese un precio unitario válido.")
            return False
        
        return True
    
    def limpiar_formulario_items(self):
        """Limpia los campos del formulario de entrada  """
        self.txt_cantidad.setText("")
        self.txt_descripcion.setText("")
        self.txt_precio.setText("")
        self.txt_importe.setValue(0)
        self.txt_impuestos.setValue(16.00)
        self.txt_cantidad.setFocus()
        
        self.btn_agregar.setText("Agregar")
        try: self.btn_agregar.clicked.disconnect()
        except TypeError: pass
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        
        self.fila_en_edicion = -1
    
    def closeEvent(self, event):
        """Evento que se dispara al cerrar la ventana  """
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CotizacionesWindow()
    window.show()
    sys.exit(app.exec_())