import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSizePolicy, QApplication,
    QLabel, QLineEdit, QGridLayout, QGroupBox,
    QMessageBox, QTableView, QHeaderView,
    QMenu, QAction, QFrame, QWidget, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QFont

# Import styles
from styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2,
    GROUP_BOX_STYLE, LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
)


class OrdenesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Órdenes de Trabajo")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Configuración inicial
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        # Variables de control
        self.fila_en_edicion = -1
        self.tipo_por_fila = {}  # 'normal', 'nota', 'seccion'

        # Crear la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear grupos de información
        self.crear_grupo_orden(main_layout)
        self.crear_grupo_vehiculo(main_layout)
        self.crear_grupo_servicio(main_layout)
        self.crear_tabla_items(main_layout)
        
        # Botones de acción
        main_layout.addStretch(1)
        self.crear_botones(main_layout)

        self.setLayout(main_layout)
        self.conectar_senales()

    def crear_grupo_orden(self, parent_layout):
        """Crear grupo de campos para datos de la orden"""
        grupo_orden = QGroupBox("")
        grupo_orden.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Folio de la orden (solo lectura)
        lbl_folio = QLabel("Folio Orden")
        lbl_folio.setStyleSheet(LABEL_STYLE)
        self.txt_folio = QLineEdit()
        self.txt_folio.setStyleSheet(INPUT_STYLE + """
            QLineEdit {
                background-color: #E8E8E8;
                color: #666666;
            }
        """)
        self.txt_folio.setReadOnly(True)
        self.txt_folio.setPlaceholderText("ORD-00000")
        
        # Cliente
        lbl_cliente = QLabel("Cliente")
        lbl_cliente.setStyleSheet(LABEL_STYLE)
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setStyleSheet(INPUT_STYLE)
        self.txt_cliente.setPlaceholderText("Nombre del cliente")
        
        # Fecha
        lbl_fecha = QLabel("Fecha")
        lbl_fecha.setStyleSheet(LABEL_STYLE)
        self.date_fecha = QDateEdit()
        self.date_fecha.setCalendarPopup(True)
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setDisplayFormat("dd/MM/yyyy")
        self.date_fecha.setStyleSheet(self._obtener_estilo_calendario())
        
        # Estado de la orden
        lbl_estado = QLabel("Estado")
        lbl_estado.setStyleSheet(LABEL_STYLE)
        self.txt_estado = QLineEdit()
        self.txt_estado.setStyleSheet(INPUT_STYLE)
        self.txt_estado.setText("PENDIENTE")
        self.txt_estado.setPlaceholderText("Estado de la orden")
        
        # Agregar widgets al layout
        layout.addWidget(lbl_folio)
        layout.addWidget(self.txt_folio, 1)
        layout.addWidget(lbl_cliente)
        layout.addWidget(self.txt_cliente, 2)
        layout.addWidget(lbl_fecha)
        layout.addWidget(self.date_fecha, 1)
        layout.addWidget(lbl_estado)
        layout.addWidget(self.txt_estado, 1)
        
        grupo_orden.setLayout(layout)
        parent_layout.addWidget(grupo_orden)

    def crear_grupo_vehiculo(self, parent_layout):
        """Crear grupo de campos para datos del vehículo"""
        grupo_vehiculo = QGroupBox("")
        grupo_vehiculo.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QGridLayout()
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Labels y campos del vehículo
        campos = [
            ("Marca", "txt_marca", "Marca del vehículo"),
            ("Modelo", "txt_modelo", "Modelo del vehículo"),
            ("Año", "txt_ano", "Año"),
            ("Placa", "txt_placa", "Placa del vehículo")
        ]
        
        for i, (texto, nombre_campo, placeholder) in enumerate(campos):
            # Crear label
            label = QLabel(texto)
            label.setStyleSheet(LABEL_STYLE)
            layout.addWidget(label, 0, i)
            
            # Crear campo de texto
            campo = QLineEdit()
            campo.setStyleSheet(INPUT_STYLE)
            campo.setPlaceholderText(placeholder)
            setattr(self, nombre_campo, campo)  # Asignar como atributo de la clase
            layout.addWidget(campo, 1, i)
        
        grupo_vehiculo.setLayout(layout)
        parent_layout.addWidget(grupo_vehiculo)

    def crear_grupo_servicio(self, parent_layout):
        """Crear grupo para agregar servicios/trabajos"""
        grupo = QGroupBox("")
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Configurar columnas - Sin precio ni IVA
        grid_layout.setColumnStretch(0, 1)    # Cantidad
        grid_layout.setColumnStretch(1, 8)    # Descripción (más ancho)
        grid_layout.setColumnStretch(2, 1)    # Botón
        
        # Labels
        lbl_cantidad = QLabel("Cantidad")
        lbl_cantidad.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_cantidad, 0, 0)
        
        lbl_descripcion = QLabel("Descripción del Servicio/Trabajo")
        lbl_descripcion.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_descripcion, 0, 1)
        
        # Campos de entrada
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setStyleSheet(INPUT_STYLE)
        self.txt_cantidad.setPlaceholderText("Cant.")
        grid_layout.addWidget(self.txt_cantidad, 1, 0)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Descripción del trabajo a realizar")
        grid_layout.addWidget(self.txt_descripcion, 1, 1)
        
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setStyleSheet(FORM_BUTTON_STYLE)
        self.btn_agregar.setCursor(Qt.PointingHandCursor)
        grid_layout.addWidget(self.btn_agregar, 1, 2)
        
        grupo.setLayout(grid_layout)
        parent_layout.addWidget(grupo)
    
    def crear_tabla_items(self, parent_layout):
        """Crear tabla para mostrar los trabajos/servicios"""
        # Modelo de datos - Solo cantidad y descripción
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels(["Cantidad", "Descripción del Trabajo/Servicio"])
        
        # Vista de tabla
        self.tabla_items = QTableView()
        self.tabla_items.setModel(self.tabla_model)
        self.tabla_items.horizontalHeader().setVisible(True)
        self.tabla_items.verticalHeader().setVisible(False)
        self.tabla_items.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_items.setStyleSheet(TABLE_STYLE)
        
        # Configurar columnas
        header = self.tabla_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Descripción
        header.setFixedHeight(40)
        
        # Configurar filas
        self.tabla_items.verticalHeader().setDefaultSectionSize(30)
        self.tabla_items.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_items.setSelectionMode(QTableView.SingleSelection)
        
        # Menú contextual
        self.tabla_items.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_items.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        
        self.tabla_items.setMinimumHeight(15 * 30 + 40)
        parent_layout.addWidget(self.tabla_items)

    def crear_botones(self, parent_layout):
        """Crear botones de acción"""
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        textos_botones = ["Nueva", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir"]
        self.botones = []
        
        for texto in textos_botones:
            boton = QPushButton(texto)
            boton.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            boton.setCursor(Qt.PointingHandCursor)
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            botones_layout.addWidget(boton)
            self.botones.append(boton)
        
        parent_layout.addLayout(botones_layout)

    def _obtener_estilo_calendario(self):
        """Estilo para el calendario"""
        return """
            QDateEdit {
                padding: 8px;
                border: 2px solid #F5F5F5;
                border-radius: 6px;
                background-color: #F5F5F5;
                min-height: 25px;
                font-size: 16px;
            }
            QDateEdit:focus {
                border: 2px solid #2CD5C4;
                background-color: white;
            }
            QDateEdit::drop-down {
                border: 0px;
                background: transparent;
                width: 30px;
            }
            QDateEdit::down-arrow {
                image: url(assets/icons/calendario.png);
                width: 16px;
                height: 16px;
            }
        """

    def conectar_senales(self):
        """Conectar señales de controles"""
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        self.tabla_items.doubleClicked.connect(self.cargar_item_para_editar)

    def mostrar_menu_contextual(self, position):
        """Menú contextual para la tabla"""
        indexes = self.tabla_items.selectedIndexes()
        menu = QMenu(self)
        
        # Opciones de inserción
        menu.addSection("Insertar")
        action_nota = QAction("➕ Agregar Nota", self)
        action_nota.triggered.connect(self.insertar_nota)
        menu.addAction(action_nota)
        
        action_seccion = QAction("📁 Agregar Sección", self)
        action_seccion.triggered.connect(self.insertar_seccion)
        menu.addAction(action_seccion)
        
        # Opciones de fila seleccionada
        if indexes:
            fila = indexes[0].row()
            tipo_fila = self.tipo_por_fila.get(fila, 'normal')
            
            menu.addSeparator()
            menu.addSection("Acciones")
            
            # Editar para notas y secciones
            if tipo_fila in ['nota', 'seccion']:
                action_editar = QAction("✏️ Editar", self)
                action_editar.triggered.connect(lambda: self.editar_elemento_especial(fila))
                menu.addAction(action_editar)
                menu.addSeparator()
            
            # Mover filas
            action_subir = QAction("Mover Arriba", self)
            action_subir.setEnabled(fila > 0)
            action_subir.triggered.connect(lambda: self.mover_fila_arriba(fila))
            menu.addAction(action_subir)
            
            action_bajar = QAction("Mover Abajo", self)
            action_bajar.setEnabled(fila < self.tabla_model.rowCount() - 1)
            action_bajar.triggered.connect(lambda: self.mover_fila_abajo(fila))
            menu.addAction(action_bajar)
            
            menu.addSeparator()
            action_eliminar = QAction("Eliminar", self)
            action_eliminar.triggered.connect(lambda: self.eliminar_fila(fila))
            menu.addAction(action_eliminar)
        
        menu.exec_(self.tabla_items.viewport().mapToGlobal(position))

    def insertar_nota(self):
        """Insertar una nota en la orden"""
        from PyQt5.QtWidgets import QInputDialog
        
        texto, ok = QInputDialog.getText(self, "Agregar Nota", "Texto de la nota:")
        if ok and texto:
            fila = self.tabla_model.rowCount()
            self.tabla_model.insertRow(fila)
            
            item_nota = QStandardItem(f"📝 {texto}")
            item_nota.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_nota.setBackground(QColor(245, 245, 245))
            item_nota.setForeground(QColor(100, 100, 100))
            
            self.tabla_model.setItem(fila, 0, item_nota)
            self.tabla_items.setSpan(fila, 0, 1, 2)  # Ocupar 2 columnas
            self.tipo_por_fila[fila] = 'nota'

    def insertar_seccion(self):
        """Insertar una sección en la orden"""
        from PyQt5.QtWidgets import QInputDialog
        
        texto, ok = QInputDialog.getText(self, "Agregar Sección", "Nombre de la sección:")
        if ok and texto:
            fila = self.tabla_model.rowCount()
            self.tabla_model.insertRow(fila)
            
            item_seccion = QStandardItem(texto.upper())
            item_seccion.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_seccion.setBackground(QColor(0, 120, 142, 30))
            item_seccion.setForeground(QColor(0, 120, 142))
            
            font = item_seccion.font()
            font.setBold(True)
            font.setPointSize(10)
            item_seccion.setFont(font)
            
            self.tabla_model.setItem(fila, 0, item_seccion)
            self.tabla_items.setSpan(fila, 0, 1, 2)  # Ocupar 2 columnas
            self.tipo_por_fila[fila] = 'seccion'

    def editar_elemento_especial(self, fila):
        """Editar nota o sección"""
        from PyQt5.QtWidgets import QInputDialog
        
        tipo = self.tipo_por_fila.get(fila, 'normal')
        if tipo == 'normal':
            return
        
        item_actual = self.tabla_model.item(fila, 0)
        if not item_actual:
            return
        
        texto_actual = item_actual.text()
        
        if tipo == 'nota':
            texto_actual = texto_actual.replace("📝 ", "")
            titulo = "Editar Nota"
            mensaje = "Modifique el texto de la nota:"
        else:  # sección
            titulo = "Editar Sección"
            mensaje = "Modifique el nombre de la sección:"
        
        texto_nuevo, ok = QInputDialog.getText(self, titulo, mensaje, QLineEdit.Normal, texto_actual)
        
        if ok and texto_nuevo:
            if tipo == 'nota':
                item_actual.setText(f"📝 {texto_nuevo}")
                item_actual.setBackground(QColor(245, 245, 245))
                item_actual.setForeground(QColor(100, 100, 100))
            else:  # sección
                item_actual.setText(texto_nuevo.upper())
                item_actual.setBackground(QColor(0, 120, 142, 30))
                item_actual.setForeground(QColor(0, 120, 142))
                
                font = item_actual.font()
                font.setBold(True)
                font.setPointSize(10)
                item_actual.setFont(font)

    def mover_fila_arriba(self, fila):
        """Mover fila hacia arriba"""
        if fila <= 0:
            return
        self._intercambiar_filas(fila, fila - 1)
        self.tabla_items.selectRow(fila - 1)

    def mover_fila_abajo(self, fila):
        """Mover fila hacia abajo"""
        if fila >= self.tabla_model.rowCount() - 1:
            return
        self._intercambiar_filas(fila, fila + 1)
        self.tabla_items.selectRow(fila + 1)

    def _intercambiar_filas(self, fila1, fila2):
        """Intercambiar dos filas en la tabla"""
        # Intercambiar items
        for col in range(self.tabla_model.columnCount()):
            item1 = self.tabla_model.takeItem(fila1, col)
            item2 = self.tabla_model.takeItem(fila2, col)
            self.tabla_model.setItem(fila1, col, item2)
            self.tabla_model.setItem(fila2, col, item1)
        
        # Intercambiar tipos
        temp_tipo = self.tipo_por_fila.get(fila1, 'normal')
        self.tipo_por_fila[fila1] = self.tipo_por_fila.get(fila2, 'normal')
        self.tipo_por_fila[fila2] = temp_tipo
        
        # Restaurar spans
        for fila in [fila1, fila2]:
            if self.tipo_por_fila.get(fila, 'normal') in ['nota', 'seccion']:
                self.tabla_items.setSpan(fila, 0, 1, 2)
            else:
                self.tabla_items.setSpan(fila, 0, 1, 1)

    def eliminar_fila(self, fila):
        """Eliminar fila de la tabla"""
        msg_box = QMessageBox(
            QMessageBox.Question, 
            "Confirmar eliminación", 
            "¿Está seguro de eliminar este elemento?", 
            QMessageBox.Yes | QMessageBox.No, 
            self
        )
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.tabla_model.removeRow(fila)
            
            # Reorganizar tipos
            nuevo_tipo = {}
            for key in range(self.tabla_model.rowCount()):
                if key < fila:
                    nuevo_tipo[key] = self.tipo_por_fila.get(key, 'normal')
                else:
                    nuevo_tipo[key] = self.tipo_por_fila.get(key + 1, 'normal')
            
            self.tipo_por_fila = nuevo_tipo
            
            if fila == self.fila_en_edicion:
                self.limpiar_formulario()

    def agregar_a_tabla(self):
        """Agregar trabajo/servicio a la tabla"""
        if not self.validar_datos():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        
        # Crear items
        item_cantidad = QStandardItem(cantidad)
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        
        item_descripcion = QStandardItem(descripcion)
        item_descripcion.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Agregar fila
        fila = self.tabla_model.rowCount()
        self.tabla_model.insertRow(fila)
        self.tabla_model.setItem(fila, 0, item_cantidad)
        self.tabla_model.setItem(fila, 1, item_descripcion)
        
        # Limpiar formulario
        self.limpiar_formulario()
        self.tabla_items.selectRow(fila)

    def cargar_item_para_editar(self, index):
        """Cargar item para edición"""
        fila = index.row()
        tipo_fila = self.tipo_por_fila.get(fila, 'normal')
        
        if tipo_fila in ['nota', 'seccion']:
            self.editar_elemento_especial(fila)
            return
        
        # Cargar datos normales
        cantidad = self.tabla_model.index(fila, 0).data()
        descripcion = self.tabla_model.index(fila, 1).data()
        
        self.txt_cantidad.setText(cantidad)
        self.txt_descripcion.setText(descripcion)
        
        self.fila_en_edicion = fila
        self.btn_agregar.setText("Actualizar")
        
        # Cambiar función del botón
        try:
            self.btn_agregar.clicked.disconnect()
        except TypeError:
            pass
        self.btn_agregar.clicked.connect(self.actualizar_item)

    def actualizar_item(self):
        """Actualizar item en edición"""
        if not self.validar_datos():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        
        self.tabla_model.setItem(self.fila_en_edicion, 0, QStandardItem(cantidad))
        self.tabla_model.setItem(self.fila_en_edicion, 1, QStandardItem(descripcion))
        
        # Restaurar alineaciones
        self.tabla_model.item(self.fila_en_edicion, 0).setTextAlignment(Qt.AlignCenter)
        self.tabla_model.item(self.fila_en_edicion, 1).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.limpiar_formulario()

    def validar_datos(self):
        """Validar datos antes de agregar"""
        if not self.txt_cantidad.text() or self.txt_cantidad.text() == "0":
            self.mostrar_advertencia("Ingrese una cantidad válida.")
            return False
        
        if not self.txt_descripcion.text():
            self.mostrar_advertencia("Ingrese una descripción del trabajo.")
            return False
        
        return True

    def mostrar_advertencia(self, mensaje):
        """Mostrar mensaje de advertencia"""
        msg_box = QMessageBox(QMessageBox.Warning, "Advertencia", mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()

    def limpiar_formulario(self):
        """Limpiar campos del formulario"""
        self.txt_cantidad.setText("")
        self.txt_descripcion.setText("")
        self.txt_cantidad.setFocus()
        
        self.btn_agregar.setText("Agregar")
        
        try:
            self.btn_agregar.clicked.disconnect()
        except TypeError:
            pass
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        
        self.fila_en_edicion = -1

    def obtener_datos_orden(self):
        """Obtener datos de la orden"""
        return {
            'folio': self.txt_folio.text(),
            'cliente': self.txt_cliente.text(),
            'fecha': self.date_fecha.date().toString("dd/MM/yyyy"),
            'estado': self.txt_estado.text(),
            'marca': self.txt_marca.text(),
            'modelo': self.txt_modelo.text(),
            'ano': self.txt_ano.text(),
            'placa': self.txt_placa.text()
        }

    def closeEvent(self, event):
        """Evento al cerrar ventana"""
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrdenesWindow()
    window.show()
    sys.exit(app.exec_())