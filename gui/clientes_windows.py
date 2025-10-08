import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, 
    QLabel, QLineEdit, QGridLayout, QGroupBox, QMessageBox, 
    QTableView, QHeaderView, QFrame, QWidget, QDateEdit, 
    QComboBox, QSpacerItem, QInputDialog
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
        self.setMinimumSize(1000, 700)
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
        
        # Tabla de clientes (sin etiqueta, ocupa todo el espacio)
        self.crear_tabla_clientes(main_layout)
        
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
        
        # Sistema de 4 columnas: cada celda tiene label arriba y campo abajo
        
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
        
        # FILA 3: Estado | País | RFC | (ID - oculto para mostrar)
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
        
        # ID (solo lectura, informativo)
        grid.addWidget(QLabel("ID Cliente"), 4, 3)
        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        self.txt_id.setStyleSheet(INPUT_STYLE + "background-color: #E8E8E8; color: #666;")
        self.txt_id.setPlaceholderText("Autogenerado")
        grid.addWidget(self.txt_id, 5, 3)
        
        # Configurar todas las columnas con el mismo ancho
        for col in range(4):
            grid.setColumnStretch(col, 1)
        
        # Configurar estilos de labels
        for i in range(grid.rowCount()):
            for j in range(grid.columnCount()):
                item = grid.itemAtPosition(i, j)
                if item and isinstance(item.widget(), QLabel):
                    item.widget().setStyleSheet(LABEL_STYLE)
        
        grupo_form.setLayout(grid)
        parent_layout.addWidget(grupo_form)

    def crear_botones_accion(self, parent_layout):
        """Botones de acción del formulario (solo para control interno)"""
        # Crear botones ocultos para funcionalidad interna
        self.btn_agregar = QPushButton()
        self.btn_actualizar = QPushButton()
        self.btn_cancelar = QPushButton()
        self.btn_limpiar = QPushButton()
        
        # No agregar al layout - se controlarán desde botones principales

    def crear_tabla_clientes(self, parent_layout):
        """Crear tabla para mostrar clientes - ocupa todo el espacio disponible"""
        # Modelo de tabla
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Email", "Teléfono", "Ciudad", "Estado"
        ])
        
        # Vista de tabla
        self.tabla_clientes = QTableView()
        self.tabla_clientes.setModel(self.tabla_model)
        self.tabla_clientes.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_clientes.setSelectionMode(QTableView.SingleSelection)
        self.tabla_clientes.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_clientes.setStyleSheet(TABLE_STYLE)
        
        # Configurar columnas para ocupar todo el espacio
        header = self.tabla_clientes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Teléfono
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Ciudad
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Estado
        header.setStretchLastSection(True)
        
        header.setFixedHeight(40)
        self.tabla_clientes.verticalHeader().setDefaultSectionSize(35)
        
        # La tabla crece para ocupar todo el espacio disponible
        self.tabla_clientes.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        parent_layout.addWidget(self.tabla_clientes, 1)

    def crear_botones_principales(self, parent_layout):
        """Crear botones principales de la ventana"""
        layout_principales = QHBoxLayout()
        layout_principales.setSpacing(15)
        
        botones_info = [
            ("Nuevo", self.nuevo_cliente),
            ("Guardar", self.guardar_cliente),  # Nuevo botón unificado
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
        # Ya no hay botones internos de formulario
        self.tabla_clientes.doubleClicked.connect(self.editar_cliente)

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
            self.mostrar_mensaje("Modo Edición", "Cliente cargado. Modifique los datos y presione 'Guardar'.", QMessageBox.Information)

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
        self.cmb_estado.setCurrentIndex(0)
        self.txt_pais.setText("México")
        self.txt_rfc.setText("")

    def actualizar_tabla(self):
        """Actualizar datos mostrados en la tabla"""
        self.tabla_model.clear()
        self.tabla_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Email", "Teléfono", "Ciudad", "Estado"
        ])
        
        for cliente in self.clientes_data:
            fila = [
                QStandardItem(str(cliente['id'])),
                QStandardItem(cliente['nombre']),
                QStandardItem(cliente['tipo']),
                QStandardItem(cliente['email']),
                QStandardItem(cliente['telefono']),
                QStandardItem(cliente['ciudad']),
                QStandardItem(cliente['estado'])
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
            }
        ]
        
        self.clientes_data.extend(ejemplos)
        self.proximo_id = 3
        self.actualizar_tabla()

    def mostrar_mensaje(self, titulo, mensaje, tipo):
        """Mostrar mensaje al usuario"""
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()