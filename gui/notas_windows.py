import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSizePolicy, QApplication,
    QLabel, QLineEdit, QComboBox, QGridLayout, QGroupBox,
    QDoubleSpinBox, QMessageBox, QTableView, QHeaderView,
    QMenu, QAction, QFrame, QWidget, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem, QIcon
# Import styles
from styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2,
    GROUP_BOX_STYLE, LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
)
from datetime import datetime


class NotasWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Notas")
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

        # Crear la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Layout principal 
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # NUEVO: Crear grupo de datos del cliente
        self.crear_grupo_cliente(main_layout)
        
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
        
        # Textos de los botones
        textos_botones = ["Nuevo", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir"]
        
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

    def crear_grupo_cliente(self, parent_layout):
        """Crear grupo de campos para datos del cliente"""
        # Crear GroupBox para cliente
        grupo_cliente = QGroupBox("")
        grupo_cliente.setStyleSheet(GROUP_BOX_STYLE)
        
        # Layout horizontal para los campos
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Campo Cliente
        lbl_cliente = QLabel("Cliente")
        lbl_cliente.setStyleSheet(LABEL_STYLE)
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setStyleSheet(INPUT_STYLE)
        self.txt_cliente.setPlaceholderText("Nombre del cliente")
        
        # Campo Fecha con QDateEdit
        lbl_fecha = QLabel("Fecha")
        lbl_fecha.setStyleSheet(LABEL_STYLE)
        self.date_fecha = QDateEdit()
        self.date_fecha.setCalendarPopup(True)  # Mostrar calendario al hacer clic
        self.date_fecha.setDate(QDate.currentDate())  # Fecha actual por defecto
        self.date_fecha.setDisplayFormat("dd/MM/yyyy")  # Formato de fecha
        
        # Aplicar estilo personalizado al QDateEdit
        self.date_fecha.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 2px solid #F5F5F5;
                border-radius: 6px;
                background-color: #F5F5F5;
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
            
            /* Estilo para el calendario popup */
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
        """)
        
        # Campo Referencia del vehículo/cliente
        lbl_referencia = QLabel("Referencia")
        lbl_referencia.setStyleSheet(LABEL_STYLE)
        self.txt_referencia = QLineEdit()
        self.txt_referencia.setStyleSheet(INPUT_STYLE)
        self.txt_referencia.setPlaceholderText("Ref. vehículo/cliente")
        
        # Agregar widgets al layout
        layout.addWidget(lbl_cliente)
        layout.addWidget(self.txt_cliente, 2)  # Más espacio para cliente
        layout.addWidget(lbl_fecha)
        layout.addWidget(self.date_fecha, 1)
        layout.addWidget(lbl_referencia)
        layout.addWidget(self.txt_referencia, 1)
        
        grupo_cliente.setLayout(layout)
        parent_layout.addWidget(grupo_cliente)

    def obtener_datos_cliente(self):
        """Obtiene los datos del cliente del formulario"""
        return {
            'cliente': self.txt_cliente.text(),
            'fecha': self.date_fecha.date().toString("dd/MM/yyyy"),
            'referencia': self.txt_referencia.text()
        }
    
    def crear_grupo_producto_servicio(self, parent_layout):
        """Crear grupo de campos para producto/servicio"""
        # Crear un groupbox para agrupar los elementos - sin título
        grupo = QGroupBox("")
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        # Crear un grid layout para organizar los campos
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Definir proporciones de columnas (ajustadas para incluir impuestos)
        grid_layout.setColumnStretch(0, 2)    # Producto
        grid_layout.setColumnStretch(1, 1)    # Cantidad
        grid_layout.setColumnStretch(2, 5)    # Descripción (reducido de 6 a 5)
        grid_layout.setColumnStretch(3, 2)    # Precio
        grid_layout.setColumnStretch(4, 2)    # Importe
        grid_layout.setColumnStretch(5, 1)    # Impuestos (nuevo)
        grid_layout.setColumnStretch(6, 1)    # Botón Agregar
        
        # ---- Fila 1: Labels ----
        lbl_producto = QLabel("Producto o Servicio")
        lbl_producto.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_producto, 0, 0)
        
        lbl_cantidad = QLabel("Cantidad")
        lbl_cantidad.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_cantidad, 0, 1)
        
        lbl_descripcion = QLabel("Descripción")
        lbl_descripcion.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_descripcion, 0, 2)
        
        lbl_precio = QLabel("Precio Unitario")
        lbl_precio.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_precio, 0, 3)
        
        lbl_importe = QLabel("Importe")
        lbl_importe.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_importe, 0, 4)
        
        # NUEVO: Label para impuestos
        lbl_impuestos = QLabel("IVA %")
        lbl_impuestos.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_impuestos, 0, 5)
        
        # ---- Fila 2: Campos ----
        self.cmb_producto = QComboBox()
        self.cmb_producto.addItems(["Seleccione...", "Producto", "Servicio"])
        self.cmb_producto.setStyleSheet(INPUT_STYLE)
        grid_layout.addWidget(self.cmb_producto, 1, 0)
        
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setStyleSheet(INPUT_STYLE)
        self.txt_cantidad.setPlaceholderText("Cantidad")
        self.txt_cantidad.setValidator(QDoubleValidator())
        grid_layout.addWidget(self.txt_cantidad, 1, 1)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Ingrese descripción")
        grid_layout.addWidget(self.txt_descripcion, 1, 2)
        
        self.txt_precio = QLineEdit()
        self.txt_precio.setStyleSheet(INPUT_STYLE)
        self.txt_precio.setPlaceholderText("$0.00")
        self.txt_precio.setValidator(QDoubleValidator(0.00, 9999999.99, 2))
        grid_layout.addWidget(self.txt_precio, 1, 3)
        
        self.txt_importe = QDoubleSpinBox()
        self.txt_importe.setReadOnly(True)
        self.txt_importe.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.txt_importe.setRange(0, 9999999.99)
        self.txt_importe.setDecimals(2)
        self.txt_importe.setPrefix("$ ")
        self.txt_importe.setStyleSheet(INPUT_STYLE)
        grid_layout.addWidget(self.txt_importe, 1, 4)
        
        # NUEVO: Campo para impuestos
        self.txt_impuestos = QDoubleSpinBox()
        self.txt_impuestos.setRange(0, 100)
        self.txt_impuestos.setDecimals(2)
        self.txt_impuestos.setSuffix(" %")
        self.txt_impuestos.setValue(16.00)  # IVA por defecto
        self.txt_impuestos.setStyleSheet(INPUT_STYLE)
        grid_layout.addWidget(self.txt_impuestos, 1, 5)
        
        # Botón para agregar a la tabla
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setStyleSheet(FORM_BUTTON_STYLE)
        self.btn_agregar.setCursor(Qt.PointingHandCursor)
        grid_layout.addWidget(self.btn_agregar, 1, 6)  # Cambió de columna 5 a 6
        
        # Establecer el layout del grupo
        grupo.setLayout(grid_layout)
        
        # Añadir el grupo al layout principal
        parent_layout.addWidget(grupo)
    
    def crear_tabla_items(self, parent_layout):
        """Crear tabla para mostrar los items agregados usando QTableView"""
        # Crear modelo de datos
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels(["Cantidad", "Descripción", "Precio Unitario", "Impuestos", "Importe"])
        
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
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Descripción se expande
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Precio Unitario
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Importe
        
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
        
        # Establecer altura para mostrar 20 filas (20 filas * 30px + 40px para el encabezado)
        self.tabla_items.setMinimumHeight(15 * 30 + 40)
        
        # Agregar al layout
        parent_layout.addWidget(self.tabla_items)
    
    def conectar_senales(self):
        """Conectar las señales de los controles"""
        # Calcular importe cuando cambia cantidad o precio unitario
        self.txt_cantidad.textChanged.connect(self.calcular_importe)
        self.txt_precio.textChanged.connect(self.calcular_importe)
        
        # Manejar cambio en el combo de producto/servicio
        self.cmb_producto.currentIndexChanged.connect(self.manejar_cambio_tipo)
        
        # Conectar botón agregar
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        
        # Conectar doble clic en tabla para editar
        self.tabla_items.doubleClicked.connect(self.cargar_item_para_editar)
    
    def mostrar_menu_contextual(self, position):
        """Muestra un menú contextual al hacer clic derecho en una fila de la tabla"""
        # Obtener el índice del elemento seleccionado
        indexes = self.tabla_items.selectedIndexes()
        if not indexes:
            return
            
        # Obtener la fila seleccionada
        fila = indexes[0].row()
        
        # Crear menú contextual
        menu = QMenu(self)
        
        # Determinar restricciones
        es_primera_fila = (fila == 0)
        es_ultima_fila = (fila == self.tabla_model.rowCount() - 1)
        es_servicio = self.tabla_model.index(fila, 0).data() == "-"
        
        # Contar servicios para determinar límites
        servicios_count = 0
        for i in range(self.tabla_model.rowCount()):
            if self.tabla_model.index(i, 0).data() == "-":
                servicios_count += 1
                
        # Restricciones adicionales basadas en tipos de ítem
        no_puede_subir_producto = not es_servicio and fila == servicios_count and fila > 0
        no_puede_bajar_servicio = es_servicio and fila == servicios_count - 1 and fila < self.tabla_model.rowCount() - 1
        
        # Acción para mover arriba
        action_subir = QAction("Mover Arriba", self)
        action_subir.setEnabled(not es_primera_fila and not no_puede_subir_producto)
        action_subir.triggered.connect(lambda: self.mover_fila_arriba(fila))
        menu.addAction(action_subir)
        
        # Acción para mover abajo
        action_bajar = QAction("Mover Abajo", self)
        action_bajar.setEnabled(not es_ultima_fila and not no_puede_bajar_servicio)
        action_bajar.triggered.connect(lambda: self.mover_fila_abajo(fila))
        menu.addAction(action_bajar)
        
        # Separador
        menu.addSeparator()
        
        # Acción para eliminar
        action_eliminar = QAction("Eliminar", self)
        action_eliminar.triggered.connect(lambda: self.eliminar_fila(fila))
        menu.addAction(action_eliminar)
        
        # Mostrar el menú
        menu.exec_(self.tabla_items.viewport().mapToGlobal(position))
    
    def mover_fila_arriba(self, fila):
        """Mueve una fila hacia arriba"""
        if fila <= 0:
            return  # No se puede mover más arriba
        
        # Verificar restricciones de servicios y productos
        es_servicio = self.tabla_model.index(fila, 0).data() == "-"
        es_servicio_arriba = self.tabla_model.index(fila-1, 0).data() == "-"
        
        # Contar servicios para determinar límites
        servicios_count = 0
        for i in range(self.tabla_model.rowCount()):
            if self.tabla_model.index(i, 0).data() == "-":
                servicios_count += 1
        
        # Restricción: un producto no puede moverse a la sección de servicios
        if not es_servicio and es_servicio_arriba and fila == servicios_count:
            self.mostrar_advertencia("No se puede mover un producto a la sección de servicios.")
            return
        
        # Guardar datos de la fila a mover
        datos_fila = []
        for col in range(self.tabla_model.columnCount()):
            datos_fila.append(self.tabla_model.index(fila, col).data())
        
        # Guardar alineaciones
        alineaciones = []
        for col in range(self.tabla_model.columnCount()):
            item = self.tabla_model.item(fila, col)
            if item:
                alineaciones.append(item.textAlignment())
            else:
                alineaciones.append(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Guardar datos de la fila destino
        datos_fila_destino = []
        for col in range(self.tabla_model.columnCount()):
            datos_fila_destino.append(self.tabla_model.index(fila-1, col).data())
        
        # Guardar alineaciones de fila destino
        alineaciones_destino = []
        for col in range(self.tabla_model.columnCount()):
            item = self.tabla_model.item(fila-1, col)
            if item:
                alineaciones_destino.append(item.textAlignment())
            else:
                alineaciones_destino.append(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Intercambiar filas directamente
        for col in range(self.tabla_model.columnCount()):
            # Actualizar fila original con datos del destino
            item1 = QStandardItem(datos_fila_destino[col])
            item1.setTextAlignment(alineaciones_destino[col])
            self.tabla_model.setItem(fila, col, item1)
            
            # Actualizar fila destino con datos originales
            item2 = QStandardItem(datos_fila[col])
            item2.setTextAlignment(alineaciones[col])
            self.tabla_model.setItem(fila-1, col, item2)
        
        # Seleccionar la fila movida
        self.tabla_items.selectRow(fila-1)

        # Intercambiar los valores de IVA
        temp_iva = self.iva_por_fila.get(fila, 16.0)  # Valor por defecto si no existe
        self.iva_por_fila[fila] = self.iva_por_fila.get(fila-1, 16.0)
        self.iva_por_fila[fila-1] = temp_iva

        # Recalcular totales
        self.calcular_totales()
    
    def mover_fila_abajo(self, fila):
        """Mueve una fila hacia abajo"""
        if fila >= self.tabla_model.rowCount() - 1:
            return  # No se puede mover más abajo
        
        # Verificar restricciones de servicios y productos
        es_servicio = self.tabla_model.index(fila, 0).data() == "-"
        es_servicio_abajo = self.tabla_model.index(fila+1, 0).data() == "-"
        
        # Contar servicios para determinar límites
        servicios_count = 0
        for i in range(self.tabla_model.rowCount()):
            if self.tabla_model.index(i, 0).data() == "-":
                servicios_count += 1
        
        # Restricción: un servicio no puede moverse a la sección de productos
        if es_servicio and not es_servicio_abajo and fila == servicios_count - 1:
            self.mostrar_advertencia("No se puede mover un servicio a la sección de productos.")
            return
        
        # Guardar datos de la fila a mover
        datos_fila = []
        for col in range(self.tabla_model.columnCount()):
            datos_fila.append(self.tabla_model.index(fila, col).data())
        
        # Guardar alineaciones
        alineaciones = []
        for col in range(self.tabla_model.columnCount()):
            item = self.tabla_model.item(fila, col)
            if item:
                alineaciones.append(item.textAlignment())
            else:
                alineaciones.append(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Guardar datos de la fila destino
        datos_fila_destino = []
        for col in range(self.tabla_model.columnCount()):
            datos_fila_destino.append(self.tabla_model.index(fila+1, col).data())
        
        # Guardar alineaciones de fila destino
        alineaciones_destino = []
        for col in range(self.tabla_model.columnCount()):
            item = self.tabla_model.item(fila+1, col)
            if item:
                alineaciones_destino.append(item.textAlignment())
            else:
                alineaciones_destino.append(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Intercambiar filas directamente
        for col in range(self.tabla_model.columnCount()):
            # Actualizar fila original con datos del destino
            item1 = QStandardItem(str(datos_fila_destino[col]))
            item1.setTextAlignment(alineaciones_destino[col])
            self.tabla_model.setItem(fila, col, item1)
            
            # Actualizar fila destino con datos originales
            item2 = QStandardItem(str(datos_fila[col]))
            item2.setTextAlignment(alineaciones[col])
            self.tabla_model.setItem(fila+1, col, item2)
        
        # Seleccionar la fila movida
        self.tabla_items.selectRow(fila+1)

        # Intercambiar los valores de IVA
        temp_iva = self.iva_por_fila.get(fila, 16.0)  # Valor por defecto si no existe
        self.iva_por_fila[fila] = self.iva_por_fila.get(fila+1, 16.0)
        self.iva_por_fila[fila+1] = temp_iva
        
        # Recalcular totales
        self.calcular_totales()
    
    def eliminar_fila(self, fila):
        """Elimina una fila de la tabla"""
        # Confirmar eliminación
        msg_box = QMessageBox(QMessageBox.Question, 
                            "Confirmar eliminación", 
                            "¿Está seguro de eliminar este elemento?", 
                            QMessageBox.Yes | QMessageBox.No, 
                            self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        
        yes_button = msg_box.button(QMessageBox.Yes)
        no_button = msg_box.button(QMessageBox.No)
        
        if yes_button:
            yes_button.setText("Sí")
            yes_button.setCursor(Qt.PointingHandCursor)
        
        if no_button:
            no_button.setText("No")
            no_button.setCursor(Qt.PointingHandCursor)
        
        result = msg_box.exec_()
        
        if result == QMessageBox.Yes:
            self.tabla_model.removeRow(fila)

            # Eliminar el IVA y reorganizar los índices
            if fila in self.iva_por_fila:
                del self.iva_por_fila[fila]

            # Reorganizar los índices del diccionario
            nuevo_iva = {}
            for key in self.iva_por_fila:
                if key > fila:
                    nuevo_iva[key - 1] = self.iva_por_fila[key]
                else:
                    nuevo_iva[key] = self.iva_por_fila[key]
            self.iva_por_fila = nuevo_iva

            # Recalcular totales
            self.calcular_totales()
            
            # Si la fila estaba en edición, limpiar el formulario
            if fila == self.fila_en_edicion:
                self.limpiar_formulario()
    

    
    def manejar_cambio_tipo(self):
        """Maneja el cambio en el combo de producto/servicio"""
        seleccion = self.cmb_producto.currentText()
        
        if seleccion == "Servicio":
            # Si es servicio, poner "-" en cantidad y deshabilitar el campo
            self.txt_cantidad.setText("-")
            self.txt_cantidad.setReadOnly(True)
        else:
            # Si no es servicio, habilitar el campo de cantidad y dejarlo vacío si tiene "-"
            if self.txt_cantidad.text() == "-":
                self.txt_cantidad.setText("")
            self.txt_cantidad.setReadOnly(False)
    
    def calcular_importe(self):
        """Calcular el importe basado en cantidad y precio unitario"""
        try:
            # Determinar cantidad según el tipo de producto/servicio
            if self.cmb_producto.currentText() == "Servicio" and self.txt_cantidad.text() == "-":
                cantidad = 1.0  # Si es servicio, considerar como 1 para el cálculo
            else:
                cantidad = float(self.txt_cantidad.text()) if self.txt_cantidad.text() else 0
            
            # Limpiar el texto del precio para manejar posibles formatos como "$1,234.56"
            precio_texto = self.txt_precio.text()
            precio_texto = precio_texto.replace("$", "").replace(",", "").strip()
            precio = float(precio_texto) if precio_texto else 0
            
            importe = cantidad * precio
            self.txt_importe.setValue(importe)
            
            # Formatear el precio con formato de moneda
            if precio > 0 and not self.txt_precio.hasFocus():
                self.txt_precio.setText(f"${precio:.2f}")
        except ValueError:
            # Si hay un error en la conversión, mostrar 0
            self.txt_importe.setValue(0)

    def calcular_totales(self):
        """Calcula y actualiza los totales mostrados"""
        subtotal = 0.0
        total_impuestos = 0.0
        
        # Recorrer todas las filas de la tabla
        for fila in range(self.tabla_model.rowCount()):
            # Obtener el importe de la columna 4 (ahora es la 4 por la nueva columna IVA)
            importe_texto = self.tabla_model.index(fila, 4).data()
            importe = float(importe_texto.replace("$", "").replace(",", "").strip())
            
            # Obtener el porcentaje de IVA almacenado para esta fila
            iva_porcentaje = self.iva_por_fila.get(fila, 16.0)
            iva_monto = importe * (iva_porcentaje / 100)
            
            subtotal += importe
            total_impuestos += iva_monto
        
        total = subtotal + total_impuestos
        
        # Actualizar las etiquetas con formato de moneda
        self.lbl_subtotal_valor.setText(f"$ {subtotal:,.2f}")
        self.lbl_impuestos_valor.setText(f"$ {total_impuestos:,.2f}")
        self.lbl_total_valor.setText(f"$ {total:,.2f}")

    def crear_panel_totales(self, parent_layout):
        """Crear panel para mostrar subtotal, impuestos y total"""
        # Crear un contenedor principal que ocupe todo el ancho
        contenedor_principal = QWidget()
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        # Agregar espacio a la izquierda
        layout_principal.addStretch(6)
        
        # Crear un widget contenedor para el frame
        contenedor_frame = QWidget()
        contenedor_frame.setMaximumWidth(9999)  # Sin límite máximo
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear el frame de totales
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
        
        # Layout horizontal dentro del frame para alinear contenido a la derecha
        main_totales_layout = QHBoxLayout()
        main_totales_layout.addStretch()  # Empuja el contenido a la derecha dentro del frame
        
        # ... resto del código del grid layout (sin cambios) ...
        
        # Layout grid para mejor alineación
        totales_grid = QGridLayout()
        totales_grid.setSpacing(5)
        totales_grid.setContentsMargins(0, 0, 0, 0)
        
        # Estilo para las etiquetas
        label_style = """
            QLabel {
                font-size: 18px;
                color: #333333;
                background: transparent;
                padding: 2px;
            }
        """
        
        label_bold_style = label_style + "font-weight: bold;"
        
        # Crear las etiquetas y valores
        lbl_subtotal_text = QLabel("Subtotal:")
        lbl_subtotal_text.setStyleSheet(label_style)
        lbl_subtotal_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.lbl_subtotal_valor = QLabel("$ 0.00")
        self.lbl_subtotal_valor.setStyleSheet(label_bold_style)
        self.lbl_subtotal_valor.setAlignment(Qt.AlignRight)
        
        lbl_impuestos_text = QLabel("Impuestos:")
        lbl_impuestos_text.setStyleSheet(label_style)
        lbl_impuestos_text.setAlignment(Qt.AlignLeft| Qt.AlignVCenter)
        
        self.lbl_impuestos_valor = QLabel("$ 0.00")
        self.lbl_impuestos_valor.setStyleSheet(label_bold_style)
        self.lbl_impuestos_valor.setAlignment(Qt.AlignRight)
        
        # Línea separadora
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: rgba(0, 120, 142, 0.3); max-height: 1px;")
        
        lbl_total_text = QLabel("Total:")
        lbl_total_text.setStyleSheet(label_style + "font-size: 18px; font-weight: bold;")
        lbl_total_text.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        self.lbl_total_valor = QLabel("$ 0.00")
        self.lbl_total_valor.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #00788E;
                background: transparent;
                padding: 2px;
            }
        """)
        self.lbl_total_valor.setAlignment(Qt.AlignRight)
        
        # Agregar al grid layout
        totales_grid.addWidget(lbl_subtotal_text, 0, 0)
        totales_grid.addWidget(self.lbl_subtotal_valor, 0, 1)
        totales_grid.addWidget(lbl_impuestos_text, 1, 0)
        totales_grid.addWidget(self.lbl_impuestos_valor, 1, 1)
        totales_grid.addWidget(linea, 2, 0, 1, 2)
        totales_grid.addWidget(lbl_total_text, 3, 0)
        totales_grid.addWidget(self.lbl_total_valor, 3, 1)
        
        # Establecer ancho de columnas
        totales_grid.setColumnMinimumWidth(0, 80)
        totales_grid.setColumnMinimumWidth(1, 120)
        
        # Contenedor para el grid
        totales_container = QWidget()
        totales_container.setLayout(totales_grid)
        totales_container.setFixedWidth(220)
        
        main_totales_layout.addWidget(totales_container)
        totales_frame.setLayout(main_totales_layout)
        
        # Agregar el frame al contenedor
        frame_layout.addWidget(totales_frame)
        contenedor_frame.setLayout(frame_layout)
        
        # Agregar el contenedor del frame al layout principal con proporción 1
        layout_principal.addWidget(contenedor_frame, 1)
        
        # Establecer el layout al contenedor principal
        contenedor_principal.setLayout(layout_principal)
        
        # Agregar el contenedor principal al layout padre
        parent_layout.addWidget(contenedor_principal)
        
    
    def agregar_a_tabla(self):
        """Agrega los datos del formulario a la tabla"""
        # Verificar datos obligatorios
        if not self.validar_datos():
            return
            
        # Determinar tipo (producto o servicio)
        tipo = self.cmb_producto.currentText()
        
        # Obtener los datos comunes
        descripcion = self.txt_descripcion.text()
        
        # Formatear precio unitario
        precio_texto = self.txt_precio.text()
        precio_texto = precio_texto.replace("$", "").replace(",", "").strip()
        precio = float(precio_texto)
        precio_formateado = f"${precio:.2f}"
        
        # Procesar según tipo
        if tipo == "Servicio":
            cantidad = "-"
            cantidad_calculo = 1
        else:  # Producto
            cantidad = self.txt_cantidad.text()
            cantidad_calculo = float(cantidad)
        
        # Calcular importe
        importe = cantidad_calculo * precio
        importe_formateado = f"${importe:.2f}"

        # Obtener el porcentaje de IVA
        iva_porcentaje = self.txt_impuestos.value()
        iva_texto = f"{iva_porcentaje:.1f} %"
        
        # Crear items para añadir al modelo
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
        
        # Añadir en la sección correspondiente de la tabla
        fila = None
        
        if tipo == "Servicio":
            # Buscar la última fila de servicios o añadir al inicio
            servicios_count = 0
            for i in range(self.tabla_model.rowCount()):
                if self.tabla_model.index(i, 0).data() == "-":
                    servicios_count += 1
            
            # Insertar después del último servicio
            fila = servicios_count
            self.tabla_model.insertRow(fila)
        else:  # Producto
            # Añadir después de la última fila (al final)
            fila = self.tabla_model.rowCount()
            self.tabla_model.insertRow(fila)
        
        # Establecer los datos en la fila
        self.tabla_model.setItem(fila, 0, item_cantidad)
        self.tabla_model.setItem(fila, 1, item_descripcion)
        self.tabla_model.setItem(fila, 2, item_precio)
        self.tabla_model.setItem(fila, 3, item_iva)
        self.tabla_model.setItem(fila, 4, item_importe)

        # Almacenar el porcentaje de IVA para esta fila
        self.iva_por_fila[fila] = self.txt_impuestos.value()

        # Actualizar totales
        self.calcular_totales()
        
        # Limpiar el formulario para un nuevo ingreso
        self.limpiar_formulario()
        
        # Seleccionar la fila recién agregada
        self.tabla_items.selectRow(fila)

    def cargar_item_para_editar(self, index):
        """Carga los datos de la fila seleccionada en los campos de edición"""
        # Ignorar si se hace clic en la columna de botones
        if index.column() == 4:
            return
            
        fila = index.row()
        
        # Obtener valores de la fila seleccionada
        cantidad = self.tabla_model.index(fila, 0).data()
        descripcion = self.tabla_model.index(fila, 1).data()
        precio = self.tabla_model.index(fila, 2).data()
        iva_texto = self.tabla_model.index(fila, 3).data()
        
        # Limpiar formato de precio (quitar $ y ,)
        precio = precio.replace("$", "").replace(",", "").strip()
        
        # Determinar si es producto o servicio
        if cantidad == "-":
            self.cmb_producto.setCurrentText("Servicio")
            self.txt_cantidad.setText("-")
            self.txt_cantidad.setReadOnly(True)
        else:
            self.cmb_producto.setCurrentText("Producto")
            self.txt_cantidad.setText(cantidad)
            self.txt_cantidad.setReadOnly(False)
        
        self.txt_descripcion.setText(descripcion)
        self.txt_precio.setText(precio)

        # Cargar el IVA almacenado para esta fila
        if fila in self.iva_por_fila:
            self.txt_impuestos.setValue(self.iva_por_fila[fila])
        else:
            self.txt_impuestos.setValue(16.0)  # Valor por defecto si no existe
        
        # Guardar el índice de la fila para poder eliminarla después
        self.fila_en_edicion = fila
        
        # Opcional: Cambiar el botón "Agregar" a "Actualizar"
        self.btn_agregar.setText("Actualizar")
        
        # Desconectar la señal actual y conectar una nueva para actualizar en vez de agregar
        try:
            self.btn_agregar.clicked.disconnect()
        except TypeError:
            pass  # Si no hay conexión, ignorar el error
        
        self.btn_agregar.clicked.connect(self.actualizar_item)

    def actualizar_item(self):
        """Actualiza la fila seleccionada con los nuevos datos"""
        # Verificar datos obligatorios
        if not self.validar_datos():
            return
        
        # Obtener tipo y datos del formulario
        tipo_nuevo = self.cmb_producto.currentText()
        tipo_anterior = "Servicio" if self.tabla_model.index(self.fila_en_edicion, 0).data() == "-" else "Producto"
        
        # Si cambió el tipo, eliminar la fila actual y agregar en la sección correcta
        if tipo_nuevo != tipo_anterior:
            self.tabla_model.removeRow(self.fila_en_edicion)
            self.agregar_a_tabla()
            return
        
        # Si no cambió el tipo, actualizar en la misma posición
        if tipo_nuevo == "Servicio":
            cantidad = "-"
            cantidad_calculo = 1
        else:
            cantidad = self.txt_cantidad.text()
            cantidad_calculo = float(cantidad)
        
        descripcion = self.txt_descripcion.text()
        
        # Formatear precio unitario
        precio_texto = self.txt_precio.text()
        precio_texto = precio_texto.replace("$", "").replace(",", "").strip()
        precio = float(precio_texto)
        precio_formateado = f"${precio:.2f}"
        
        # Obtener el porcentaje de IVA
        iva_texto = f"{self.txt_impuestos.value():.1f} %"

        # Calcular importe
        importe = cantidad_calculo * precio
        importe_formateado = f"${importe:.2f}"
        
        # Actualizar fila en el modelo
        self.tabla_model.setItem(self.fila_en_edicion, 0, QStandardItem(cantidad))
        self.tabla_model.setItem(self.fila_en_edicion, 1, QStandardItem(descripcion))
        self.tabla_model.setItem(self.fila_en_edicion, 2, QStandardItem(precio_formateado))
        self.tabla_model.setItem(self.fila_en_edicion, 3, QStandardItem(iva_texto))
        self.tabla_model.setItem(self.fila_en_edicion, 4, QStandardItem(importe_formateado))

        # Actualizar el IVA almacenado 
        self.iva_por_fila[self.fila_en_edicion] = self.txt_impuestos.value()

        # Recalcular totales
        self.calcular_totales()
        
        # Establecer alineación
        self.tabla_model.item(self.fila_en_edicion, 0).setTextAlignment(Qt.AlignCenter)
        self.tabla_model.item(self.fila_en_edicion, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tabla_model.item(self.fila_en_edicion, 2).setTextAlignment(Qt.AlignCenter)
        self.tabla_model.item(self.fila_en_edicion, 3).setTextAlignment(Qt.AlignCenter)
        self.tabla_model.item(self.fila_en_edicion, 4).setTextAlignment(Qt.AlignCenter)
        
        # Limpiar formulario y restaurar botón
        self.limpiar_formulario()
        
    def mostrar_advertencia(self, mensaje):
        msg_box = QMessageBox(QMessageBox.Warning, "Advertencia", mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        
        ok_button = msg_box.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setText("OK")
            ok_button.setCursor(Qt.PointingHandCursor)
        
        msg_box.exec_()

    def validar_datos(self):
        """Valida que los datos del formulario sean correctos"""
        tipo = self.cmb_producto.currentText()
        
        if tipo == "Seleccione...":
            self.mostrar_advertencia("Seleccione el tipo de ítem (Producto o Servicio).")
            return False
            
        if tipo == "Producto" and (not self.txt_cantidad.text() or self.txt_cantidad.text() == "0"):
            self.mostrar_advertencia("Ingrese una cantidad válida.")
            return False
            
        if not self.txt_descripcion.text():
            self.mostrar_advertencia("Ingrese una descripción.")
            return False
            
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        if not precio_texto or float(precio_texto) <= 0:
            self.mostrar_advertencia("Ingrese un precio válido.")
            return False
            
        return True
    
    def limpiar_formulario(self):
        """Limpia el formulario para un nuevo ingreso"""
        self.cmb_producto.setCurrentIndex(0)  # Seleccione...
        self.txt_cantidad.setReadOnly(False)
        self.txt_cantidad.setText("")
        self.txt_descripcion.setText("")
        self.txt_precio.setText("")
        self.txt_importe.setValue(0)
        self.cmb_producto.setFocus()
        self.txt_impuestos.setValue(16.00)
        
        # Asegurar que el botón tenga el texto correcto
        self.btn_agregar.setText("Agregar")
        
        # Asegurar que esté conectado a la función correcta
        try:
            self.btn_agregar.clicked.disconnect()
        except TypeError:
            pass
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        
        # Resetear fila en edición
        self.fila_en_edicion = -1
    
    def closeEvent(self, event):
        """Evento que se dispara al cerrar la ventana"""
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotasWindow()
    window.show()
    sys.exit(app.exec_())