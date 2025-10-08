import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, 
    QLabel, QLineEdit, QGridLayout, QGroupBox, QMessageBox, 
    QTableView, QHeaderView, QFrame, QWidget, QDateEdit, 
    QComboBox, QSpacerItem, QInputDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# Importar estilos
from styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE, 
    LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
)

class ClientesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Gestión de Clientes")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Configuración inicial
        self.setMinimumSize(1200, 700)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        # Variables de control
        self.cliente_en_edicion = None
        self.modo_edicion = False
        
        # Simulación de base de datos
        self.clientes_data = []
        self.proximo_id = 1
        
        # Configurar interfaz
        self.setup_ui()
        self.conectar_senales()
        self.cargar_datos_ejemplo()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Formulario de cliente (compacto)
        self.crear_formulario_cliente(main_layout)
        
        # Botones de acción del formulario
        self.crear_botones_accion(main_layout)
        
        # Layout horizontal: Tabla + Panel de detalles
        contenedor_horizontal = QHBoxLayout()
        contenedor_horizontal.setSpacing(10)
        
        # Tabla (lado izquierdo - 70%)
        self.crear_tabla_clientes_compacta(contenedor_horizontal)
        
        # Panel de detalles (lado derecho - 30%)
        self.crear_panel_detalle(contenedor_horizontal)
        
        main_layout.addLayout(contenedor_horizontal, 1)
        
        # Botones principales
        self.crear_botones_principales(main_layout)
        
        self.setLayout(main_layout)

    def crear_formulario_cliente(self, parent_layout):
        """Crear formulario con 4 columnas balanceadas"""
        grupo_form = QGroupBox()
        grupo_form.setStyleSheet(GROUP_BOX_STYLE)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 15)
        
        # FILA 1: Nombre | Tipo | Email | Teléfono
        grid.addWidget(QLabel("Nombre Completo"), 0, 0)
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setStyleSheet(INPUT_STYLE)
        self.txt_nombre.setPlaceholderText("Nombre completo del cliente")
        grid.addWidget(self.txt_nombre, 1, 0)
        
        grid.addWidget(QLabel("Tipo Cliente"), 0, 1)
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.setStyleSheet(INPUT_STYLE)
        self.cmb_tipo.addItems(["Particular", "Empresa", "Gobierno"])
        grid.addWidget(self.cmb_tipo, 1, 1)
        
        grid.addWidget(QLabel("Email"), 0, 2)
        self.txt_email = QLineEdit()
        self.txt_email.setStyleSheet(INPUT_STYLE)
        self.txt_email.setPlaceholderText("correo@ejemplo.com")
        grid.addWidget(self.txt_email, 1, 2)
        
        grid.addWidget(QLabel("Teléfono"), 0, 3)
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setStyleSheet(INPUT_STYLE)
        self.txt_telefono.setPlaceholderText("(123) 456-7890")
        grid.addWidget(self.txt_telefono, 1, 3)
        
        # FILA 2: Calle | Colonia | CP | Ciudad
        grid.addWidget(QLabel("Calle y Número"), 2, 0)
        self.txt_calle = QLineEdit()
        self.txt_calle.setStyleSheet(INPUT_STYLE)
        self.txt_calle.setPlaceholderText("Calle y número")
        grid.addWidget(self.txt_calle, 3, 0)
        
        grid.addWidget(QLabel("Colonia"), 2, 1)
        self.txt_colonia = QLineEdit()
        self.txt_colonia.setStyleSheet(INPUT_STYLE)
        self.txt_colonia.setPlaceholderText("Colonia o fraccionamiento")
        grid.addWidget(self.txt_colonia, 3, 1)
        
        grid.addWidget(QLabel("Código Postal"), 2, 2)
        self.txt_cp = QLineEdit()
        self.txt_cp.setStyleSheet(INPUT_STYLE)
        self.txt_cp.setPlaceholderText("00000")
        self.txt_cp.setMaxLength(5)
        grid.addWidget(self.txt_cp, 3, 2)
        
        grid.addWidget(QLabel("Ciudad"), 2, 3)
        self.txt_ciudad = QLineEdit()
        self.txt_ciudad.setStyleSheet(INPUT_STYLE)
        self.txt_ciudad.setPlaceholderText("Ciudad")
        grid.addWidget(self.txt_ciudad, 3, 3)
        
        # FILA 3: Estado | País | RFC | ID
        grid.addWidget(QLabel("Estado"), 4, 0)
        self.cmb_estado = QComboBox()
        self.cmb_estado.setStyleSheet(INPUT_STYLE)
        self.cmb_estado.addItems([
            "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
            "Chiapas", "Chihuahua", "Coahuila", "Colima", "Durango", "Guanajuato",
            "Guerrero", "Hidalgo", "Jalisco", "México", "Michoacán", "Morelos",
            "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
            "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
            "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"
        ])
        self.cmb_estado.setCurrentText("Jalisco")
        grid.addWidget(self.cmb_estado, 5, 0)
        
        grid.addWidget(QLabel("País"), 4, 1)
        self.txt_pais = QLineEdit()
        self.txt_pais.setStyleSheet(INPUT_STYLE)
        self.txt_pais.setText("México")
        self.txt_pais.setPlaceholderText("País")
        grid.addWidget(self.txt_pais, 5, 1)
        
        grid.addWidget(QLabel("RFC"), 4, 2)
        self.txt_rfc = QLineEdit()
        self.txt_rfc.setStyleSheet(INPUT_STYLE)
        self.txt_rfc.setPlaceholderText("RFC (opcional)")
        grid.addWidget(self.txt_rfc, 5, 2)
        
        # ID (solo lectura)
        grid.addWidget(QLabel("ID Cliente"), 4, 3)
        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        self.txt_id.setStyleSheet(INPUT_STYLE + "background-color: #E8E8E8; color: #666;")
        self.txt_id.setPlaceholderText("Autogenerado")
        grid.addWidget(self.txt_id, 5, 3)
        
        # Configurar columnas con el mismo ancho
        for col in range(4):
            grid.setColumnStretch(col, 1)
        
        # Aplicar estilos a labels
        for i in range(grid.rowCount()):
            for j in range(grid.columnCount()):
                item = grid.itemAtPosition(i, j)
                if item and isinstance(item.widget(), QLabel):
                    item.widget().setStyleSheet(LABEL_STYLE)
        
        grupo_form.setLayout(grid)
        parent_layout.addWidget(grupo_form)

    def crear_botones_accion(self, parent_layout):
        """Botones ocultos para funcionalidad interna"""
        self.btn_agregar = QPushButton()
        self.btn_actualizar = QPushButton()
        self.btn_cancelar = QPushButton()
        self.btn_limpiar = QPushButton()

    def crear_tabla_clientes_compacta(self, parent_layout):
        """Tabla con campos principales solamente"""
        widget_tabla = QWidget()
        layout_tabla = QVBoxLayout()
        layout_tabla.setContentsMargins(0, 0, 0, 0)
        
        # Etiqueta de la tabla
        lbl_titulo = QLabel("📋 Lista de Clientes")
        lbl_titulo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2CD5C4, stop: 1 #00788E
                );
                padding: 8px;
                border-radius: 5px;
                margin-bottom: 5px;
            }
        """)
        layout_tabla.addWidget(lbl_titulo)
        
        # Modelo compacto
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Email", "Teléfono"
        ])
        
        self.tabla_clientes = QTableView()
        self.tabla_clientes.setModel(self.tabla_model)
        self.tabla_clientes.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_clientes.setSelectionMode(QTableView.SingleSelection)
        self.tabla_clientes.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_clientes.setStyleSheet(TABLE_STYLE)
        
        header = self.tabla_clientes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setFixedHeight(40)
        
        self.tabla_clientes.verticalHeader().setDefaultSectionSize(35)
        self.tabla_clientes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout_tabla.addWidget(self.tabla_clientes)
        widget_tabla.setLayout(layout_tabla)
        parent_layout.addWidget(widget_tabla, 7)  # 70% del espacio

    def crear_panel_detalle(self, parent_layout):
        """Panel lateral con detalles completos del cliente seleccionado"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 200);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Título
        titulo = QLabel("📄 Detalles del Cliente")
        titulo.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00788E;
            padding: 8px;
            background: rgba(44, 213, 196, 0.2);
            border-radius: 5px;
        """)
        layout.addWidget(titulo)
        
        # Scroll area para detalles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenido = QWidget()
        layout_contenido = QVBoxLayout()
        layout_contenido.setSpacing(8)
        
        # Labels para información
        self.lbl_detalle_id = self.crear_label_detalle("🆔 ID:", "---")
        self.lbl_detalle_nombre = self.crear_label_detalle("👤 Nombre:", "---")
        self.lbl_detalle_tipo = self.crear_label_detalle("📌 Tipo:", "---")
        self.lbl_detalle_email = self.crear_label_detalle("📧 Email:", "---")
        self.lbl_detalle_telefono = self.crear_label_detalle("📞 Teléfono:", "---")
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background-color: rgba(0, 120, 142, 0.3); max-height: 2px;")
        
        self.lbl_detalle_direccion = self.crear_label_detalle("🏠 Dirección:", "---", multilinea=True)
        self.lbl_detalle_ciudad = self.crear_label_detalle("🏙️ Ciudad:", "---")
        self.lbl_detalle_estado = self.crear_label_detalle("📍 Estado:", "---")
        self.lbl_detalle_cp = self.crear_label_detalle("📮 CP:", "---")
        self.lbl_detalle_pais = self.crear_label_detalle("🌎 País:", "---")
        self.lbl_detalle_rfc = self.crear_label_detalle("📋 RFC:", "---")
        
        # Agregar todos los labels
        for lbl in [self.lbl_detalle_id, self.lbl_detalle_nombre, self.lbl_detalle_tipo, 
                    self.lbl_detalle_email, self.lbl_detalle_telefono]:
            layout_contenido.addWidget(lbl)
        
        layout_contenido.addWidget(separador)
        
        for lbl in [self.lbl_detalle_direccion, self.lbl_detalle_ciudad, 
                    self.lbl_detalle_estado, self.lbl_detalle_cp, 
                    self.lbl_detalle_pais, self.lbl_detalle_rfc]:
            layout_contenido.addWidget(lbl)
        
        layout_contenido.addStretch()
        contenido.setLayout(layout_contenido)
        scroll.setWidget(contenido)
        
        layout.addWidget(scroll)
        panel.setLayout(layout)
        parent_layout.addWidget(panel, 3)  # 30% del espacio

    def crear_label_detalle(self, titulo, valor, multilinea=False):
        """Crear label para panel de detalles"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(3)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-weight: bold; color: #666; font-size: 11px;")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("color: #333; font-size: 13px;")
        lbl_valor.setWordWrap(multilinea)
        lbl_valor.setObjectName("valor")  # Para identificarlo después
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        
        frame.setLayout(layout)
        return frame

    def crear_botones_principales(self, parent_layout):
        """Crear botones principales de la ventana"""
        layout_principales = QHBoxLayout()
        layout_principales.setSpacing(15)
        
        botones_info = [
            ("Nuevo", self.nuevo_cliente),
            ("Guardar", self.guardar_cliente),
            ("Editar", self.editar_cliente),
            ("Eliminar", self.eliminar_cliente),
            ("Buscar", self.buscar_cliente),
            ("Limpiar", self.limpiar_formulario),
            ("Exportar", self.exportar_clientes),
            ("Cerrar", self.close)
        ]
        
        for texto, funcion in botones_info:
            btn = QPushButton(texto)
            btn.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFixedHeight(50)
            btn.clicked.connect(funcion)
            layout_principales.addWidget(btn)
        
        parent_layout.addLayout(layout_principales)

    def conectar_senales(self):
        """Conectar señales de los controles"""
        self.tabla_clientes.doubleClicked.connect(self.editar_cliente)
        # Actualizar panel de detalles al seleccionar
        self.tabla_clientes.selectionModel().currentChanged.connect(self.actualizar_panel_detalle)

    def actualizar_panel_detalle(self, current, previous):
        """Actualizar panel de detalles con cliente seleccionado"""
        if not current.isValid():
            return
        
        fila = current.row()
        cliente_id = int(self.tabla_model.item(fila, 0).text())
        cliente = next((c for c in self.clientes_data if c['id'] == cliente_id), None)
        
        if cliente:
            self.actualizar_label_valor(self.lbl_detalle_id, str(cliente['id']))
            self.actualizar_label_valor(self.lbl_detalle_nombre, cliente['nombre'])
            self.actualizar_label_valor(self.lbl_detalle_tipo, cliente['tipo'])
            self.actualizar_label_valor(self.lbl_detalle_email, cliente['email'])
            self.actualizar_label_valor(self.lbl_detalle_telefono, cliente['telefono'])
            
            # Dirección completa
            direccion_partes = []
            if cliente.get('calle'):
                direccion_partes.append(cliente['calle'])
            if cliente.get('colonia'):
                direccion_partes.append(cliente['colonia'])
            direccion = '\n'.join(direccion_partes) if direccion_partes else '---'
            self.actualizar_label_valor(self.lbl_detalle_direccion, direccion)
            
            self.actualizar_label_valor(self.lbl_detalle_ciudad, cliente['ciudad'])
            self.actualizar_label_valor(self.lbl_detalle_estado, cliente['estado'])
            self.actualizar_label_valor(self.lbl_detalle_cp, cliente['cp'])
            self.actualizar_label_valor(self.lbl_detalle_pais, cliente.get('pais', 'México'))
            self.actualizar_label_valor(self.lbl_detalle_rfc, cliente['rfc'] if cliente['rfc'] else '---')

    def actualizar_label_valor(self, frame, valor):
        """Actualizar valor en label de detalle"""
        layout = frame.layout()
        # Buscar el label con objectName "valor"
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.objectName() == "valor":
                widget.setText(valor if valor else "---")
                break

    # OPERACIONES CRUD
    
    def guardar_cliente(self):
        """Guardar cliente nuevo o actualizar existente"""
        if self.modo_edicion:
            self.actualizar_cliente()
        else:
            self.agregar_cliente()
    
    def agregar_cliente(self):
        """Agregar nuevo cliente"""
        if not self.validar_formulario():
            return
        
        cliente = {
            'id': self.proximo_id,
            'nombre': self.txt_nombre.text().strip(),
            'tipo': self.cmb_tipo.currentText(),
            'email': self.txt_email.text().strip(),
            'telefono': self.txt_telefono.text().strip(),
            'calle': self.txt_calle.text().strip(),
            'colonia': self.txt_colonia.text().strip(),
            'cp': self.txt_cp.text().strip(),
            'ciudad': self.txt_ciudad.text().strip(),
            'estado': self.cmb_estado.currentText(),
            'pais': self.txt_pais.text().strip(),
            'rfc': self.txt_rfc.text().strip()
        }
        
        self.clientes_data.append(cliente)
        self.proximo_id += 1
        self.actualizar_tabla()
        self.limpiar_formulario()
        
        self.mostrar_mensaje("Éxito", "Cliente agregado correctamente.", QMessageBox.Information)

    def actualizar_cliente(self):
        """Actualizar cliente existente"""
        if not self.validar_formulario() or self.cliente_en_edicion is None:
            return
        
        for i, cliente in enumerate(self.clientes_data):
            if cliente['id'] == self.cliente_en_edicion['id']:
                self.clientes_data[i].update({
                    'nombre': self.txt_nombre.text().strip(),
                    'tipo': self.cmb_tipo.currentText(),
                    'email': self.txt_email.text().strip(),
                    'telefono': self.txt_telefono.text().strip(),
                    'calle': self.txt_calle.text().strip(),
                    'colonia': self.txt_colonia.text().strip(),
                    'cp': self.txt_cp.text().strip(),
                    'ciudad': self.txt_ciudad.text().strip(),
                    'estado': self.cmb_estado.currentText(),
                    'pais': self.txt_pais.text().strip(),
                    'rfc': self.txt_rfc.text().strip()
                })
                break
        
        self.actualizar_tabla()
        self.cancelar_edicion()
        self.mostrar_mensaje("Éxito", "Cliente actualizado correctamente.", QMessageBox.Information)

    def eliminar_cliente(self):
        """Eliminar cliente seleccionado"""
        fila = self.tabla_clientes.currentIndex().row()
        if fila < 0:
            self.mostrar_mensaje("Advertencia", "Seleccione un cliente para eliminar.", QMessageBox.Warning)
            return
        
        cliente_id = int(self.tabla_model.item(fila, 0).text())
        cliente = next((c for c in self.clientes_data if c['id'] == cliente_id), None)
        
        if cliente:
            respuesta = QMessageBox.question(
                self, "Confirmar eliminación",
                f"¿Está seguro de eliminar el cliente '{cliente['nombre']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                self.clientes_data.remove(cliente)
                self.actualizar_tabla()
                self.limpiar_formulario()
                self.limpiar_panel_detalle()
                self.mostrar_mensaje("Éxito", "Cliente eliminado correctamente.", QMessageBox.Information)

    # FUNCIONES AUXILIARES
    
    def nuevo_cliente(self):
        """Preparar formulario para nuevo cliente"""
        self.limpiar_formulario()
        self.txt_nombre.setFocus()

    def editar_cliente(self):
        """Cargar cliente seleccionado para edición"""
        fila = self.tabla_clientes.currentIndex().row()
        if fila < 0:
            self.mostrar_mensaje("Advertencia", "Seleccione un cliente para editar.", QMessageBox.Warning)
            return
        
        cliente_id = int(self.tabla_model.item(fila, 0).text())
        cliente = next((c for c in self.clientes_data if c['id'] == cliente_id), None)
        
        if cliente:
            self.cargar_cliente_en_formulario(cliente)
            self.modo_edicion = True
            self.cliente_en_edicion = cliente

    def cancelar_edicion(self):
        """Cancelar modo de edición"""
        self.modo_edicion = False
        self.cliente_en_edicion = None
        self.limpiar_formulario()

    def buscar_cliente(self):
        """Buscar cliente por nombre"""
        texto, ok = QInputDialog.getText(self, "Buscar Cliente", "Ingrese nombre a buscar:")
        if ok and texto:
            self.filtrar_tabla(texto)

    def exportar_clientes(self):
        """Exportar lista de clientes"""
        self.mostrar_mensaje("Info", "Función de exportación en desarrollo.", QMessageBox.Information)

    def validar_formulario(self):
        """Validar datos del formulario"""
        if not self.txt_nombre.text().strip():
            self.mostrar_mensaje("Error", "El nombre es obligatorio.", QMessageBox.Critical)
            self.txt_nombre.setFocus()
            return False
        
        if not self.txt_email.text().strip():
            self.mostrar_mensaje("Error", "El email es obligatorio.", QMessageBox.Critical)
            self.txt_email.setFocus()
            return False
        
        email = self.txt_email.text().strip()
        if "@" not in email or "." not in email:
            self.mostrar_mensaje("Error", "Formato de email inválido.", QMessageBox.Critical)
            self.txt_email.setFocus()
            return False
        
        return True

    def cargar_cliente_en_formulario(self, cliente):
        """Cargar datos del cliente en el formulario"""
        self.txt_id.setText(str(cliente['id']))
        self.txt_nombre.setText(cliente['nombre'])
        self.cmb_tipo.setCurrentText(cliente['tipo'])
        self.txt_email.setText(cliente['email'])
        self.txt_telefono.setText(cliente['telefono'])
        self.txt_calle.setText(cliente.get('calle', ''))
        self.txt_colonia.setText(cliente.get('colonia', ''))
        self.txt_cp.setText(cliente['cp'])
        self.txt_ciudad.setText(cliente['ciudad'])
        self.cmb_estado.setCurrentText(cliente['estado'])
        self.txt_pais.setText(cliente.get('pais', 'México'))
        self.txt_rfc.setText(cliente['rfc'])

    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        self.txt_id.setText("")
        self.txt_nombre.setText("")
        self.cmb_tipo.setCurrentIndex(0)
        self.txt_email.setText("")
        self.txt_telefono.setText("")
        self.txt_calle.setText("")
        self.txt_colonia.setText("")
        self.txt_cp.setText("")
        self.txt_ciudad.setText("")
        self.cmb_estado.setCurrentIndex(12)  # Jalisco por defecto
        self.txt_pais.setText("México")
        self.txt_rfc.setText("")
        self.modo_edicion = False
        self.cliente_en_edicion = None

    def limpiar_panel_detalle(self):
        """Limpiar el panel de detalles"""
        for lbl in [self.lbl_detalle_id, self.lbl_detalle_nombre, self.lbl_detalle_tipo,
                    self.lbl_detalle_email, self.lbl_detalle_telefono, self.lbl_detalle_direccion,
                    self.lbl_detalle_ciudad, self.lbl_detalle_estado, self.lbl_detalle_cp,
                    self.lbl_detalle_pais, self.lbl_detalle_rfc]:
            self.actualizar_label_valor(lbl, "---")

    def actualizar_tabla(self):
        """Actualizar datos mostrados en la tabla"""
        self.tabla_model.clear()
        self.tabla_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Email", "Teléfono"
        ])
        
        for cliente in self.clientes_data:
            fila = [
                QStandardItem(str(cliente['id'])),
                QStandardItem(cliente['nombre']),
                QStandardItem(cliente['tipo']),
                QStandardItem(cliente['email']),
                QStandardItem(cliente['telefono'])
            ]
            
            for item in fila:
                item.setTextAlignment(Qt.AlignCenter)
            
            fila[1].setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            fila[3].setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            self.tabla_model.appendRow(fila)

    def filtrar_tabla(self, texto_busqueda):
        """Filtrar tabla por texto de búsqueda"""
        texto = texto_busqueda.lower()
        clientes_filtrados = [
            c for c in self.clientes_data 
            if texto in c['nombre'].lower() or texto in c['email'].lower()
        ]
        
        datos_originales = self.clientes_data
        self.clientes_data = clientes_filtrados
        self.actualizar_tabla()
        self.clientes_data = datos_originales

    def cargar_datos_ejemplo(self):
        """Cargar datos de ejemplo"""
        ejemplos = [
            {
                'id': 1, 'nombre': 'Juan Pérez García', 'tipo': 'Particular',
                'email': 'juan.perez@email.com', 'telefono': '(33) 1234-5678',
                'calle': 'Av. Hidalgo 123', 'colonia': 'Centro',
                'ciudad': 'Guadalajara', 'estado': 'Jalisco', 'cp': '44100',
                'pais': 'México', 'rfc': ''
            },
            {
                'id': 2, 'nombre': 'María López Sánchez', 'tipo': 'Empresa',
                'email': 'maria.lopez@empresa.com', 'telefono': '(33) 9876-5432',
                'calle': 'Calle Morelos 456', 'colonia': 'Americana',
                'ciudad': 'Zapopan', 'estado': 'Jalisco', 'cp': '45100',
                'pais': 'México', 'rfc': 'LOSM850315ABC'
            },
            {
                'id': 3, 'nombre': 'Carlos Ramírez Torres', 'tipo': 'Particular',
                'email': 'carlos.ramirez@correo.com', 'telefono': '(33) 5555-1234',
                'calle': 'Av. Américas 789', 'colonia': 'Providencia',
                'ciudad': 'Guadalajara', 'estado': 'Jalisco', 'cp': '44630',
                'pais': 'México', 'rfc': ''
            }
        ]
        
        self.clientes_data.extend(ejemplos)
        self.proximo_id = 4
        self.actualizar_tabla()

    def mostrar_mensaje(self, titulo, mensaje, tipo):
        """Mostrar mensaje al usuario"""
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()

    def closeEvent(self, event):
        """Evento al cerrar la ventana"""
        event.accept()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ClientesWindow()
    window.show()
    sys.exit(app.exec_())