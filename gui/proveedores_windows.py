import sys
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QGridLayout, QGroupBox, QMessageBox, 
    QTableView, QHeaderView, QFrame, QWidget, 
    QComboBox, QInputDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# Importar estilos
from styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE, 
    LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, MESSAGE_BOX_STYLE
)

from db_helper import db_helper

class ProveedoresWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Gestión de Proveedores")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Configuración inicial

        self.setMinimumSize(1200, 700)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        # Variables de control
        self.proveedor_en_edicion = None
        self.modo_edicion = False
        
        # Configurar interfaz
        self.setup_ui()
        self.cargar_datos_desde_bd()

        #Forzar maximización
        QTimer.singleShot(100, self.maximizar_ventana)

    def maximizar_ventana(self):
        """Maximizar la ventana forzando actualización completa"""
        self.setWindowState(Qt.WindowMaximized)
        # Forzar actualización del layout
        QTimer.singleShot(50, self.forzar_resize_completo)

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Formulario de proveedor con labels al lado
        self.crear_formulario_proveedor(main_layout)
        
        # Layout horizontal: Tabla + Panel de detalles
        contenedor_horizontal = QHBoxLayout()
        contenedor_horizontal.setSpacing(10)
        
        # Tabla (70% del espacio)
        self.crear_tabla_proveedores(contenedor_horizontal)
        
        # Panel de detalles (30% del espacio)
        self.crear_panel_detalle(contenedor_horizontal)
        
        main_layout.addLayout(contenedor_horizontal, 10)
        
        # Botones principales
        self.crear_botones_principales(main_layout)
        
        self.setLayout(main_layout)

    def crear_formulario_proveedor(self, parent_layout):
        """Crear formulario con labels al lado de cada campo - Todos alineados"""
        grupo_form = QGroupBox()
        grupo_form.setStyleSheet(GROUP_BOX_STYLE)
        grupo_form.setMaximumHeight(180)  # Altura más compacta

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 15)
        
        # Estilo para labels
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background: transparent;
                min-width: 70px;
                max-width: 70px;
            }
        """
        
        # === FILA 1: Nombre | Tipo | Email | Teléfono ===
        row = 0
        
        # Nombre
        lbl_nombre = QLabel("Nombre:")
        lbl_nombre.setStyleSheet(label_style)
        lbl_nombre.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_nombre, row, 0)
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setStyleSheet(INPUT_STYLE)
        self.txt_nombre.setPlaceholderText("Nombre completo del proveedor")
        grid.addWidget(self.txt_nombre, row, 1)
        
        # Tipo
        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setStyleSheet(label_style)
        lbl_tipo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_tipo, row, 2)
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.setStyleSheet(INPUT_STYLE)
        self.cmb_tipo.addItems(["Particular", "Empresa", "Gobierno"])
        grid.addWidget(self.cmb_tipo, row, 3)
        
        # Email
        lbl_email = QLabel("Email:")
        lbl_email.setStyleSheet(label_style)
        lbl_email.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_email, row, 4)
        self.txt_email = QLineEdit()
        self.txt_email.setStyleSheet(INPUT_STYLE)
        self.txt_email.setPlaceholderText("correo@ejemplo.com")
        grid.addWidget(self.txt_email, row, 5)
        
        # Teléfono
        lbl_telefono = QLabel("Teléfono:")
        lbl_telefono.setStyleSheet(label_style)
        lbl_telefono.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_telefono, row, 6)
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setStyleSheet(INPUT_STYLE)
        self.txt_telefono.setPlaceholderText("(123) 456-7890")
        grid.addWidget(self.txt_telefono, row, 7)
        
        # === FILA 2: Calle | Colonia | CP | Ciudad ===
        row = 1
        
        # Calle
        lbl_calle = QLabel("Calle:")
        lbl_calle.setStyleSheet(label_style)
        lbl_calle.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_calle, row, 0)
        self.txt_calle = QLineEdit()
        self.txt_calle.setStyleSheet(INPUT_STYLE)
        self.txt_calle.setPlaceholderText("Calle y número")
        grid.addWidget(self.txt_calle, row, 1)
        
        # Colonia
        lbl_colonia = QLabel("Colonia:")
        lbl_colonia.setStyleSheet(label_style)
        lbl_colonia.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_colonia, row, 2)
        self.txt_colonia = QLineEdit()
        self.txt_colonia.setStyleSheet(INPUT_STYLE)
        self.txt_colonia.setPlaceholderText("Colonia o fraccionamiento")
        grid.addWidget(self.txt_colonia, row, 3)
        
        # CP
        lbl_cp = QLabel("C.P.:")
        lbl_cp.setStyleSheet(label_style)
        lbl_cp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_cp, row, 4)
        self.txt_cp = QLineEdit()
        self.txt_cp.setStyleSheet(INPUT_STYLE)
        self.txt_cp.setPlaceholderText("00000")
        self.txt_cp.setMaxLength(5)
        grid.addWidget(self.txt_cp, row, 5)
        
        # Ciudad
        lbl_ciudad = QLabel("Ciudad:")
        lbl_ciudad.setStyleSheet(label_style)
        lbl_ciudad.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_ciudad, row, 6)
        self.txt_ciudad = QLineEdit()
        self.txt_ciudad.setStyleSheet(INPUT_STYLE)
        self.txt_ciudad.setPlaceholderText("Ciudad")
        grid.addWidget(self.txt_ciudad, row, 7)
        
        # === FILA 3: Estado | País | RFC | ID ===
        row = 2
        
        # Estado
        lbl_estado = QLabel("Estado:")
        lbl_estado.setStyleSheet(label_style)
        lbl_estado.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_estado, row, 0)
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
        grid.addWidget(self.cmb_estado, row, 1)
        
        # País
        lbl_pais = QLabel("País:")
        lbl_pais.setStyleSheet(label_style)
        lbl_pais.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_pais, row, 2)
        self.txt_pais = QLineEdit()
        self.txt_pais.setStyleSheet(INPUT_STYLE)
        self.txt_pais.setText("México")
        self.txt_pais.setPlaceholderText("País")
        grid.addWidget(self.txt_pais, row, 3)
        
        # RFC
        lbl_rfc = QLabel("RFC:")
        lbl_rfc.setStyleSheet(label_style)
        lbl_rfc.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_rfc, row, 4)
        self.txt_rfc = QLineEdit()
        self.txt_rfc.setStyleSheet(INPUT_STYLE)
        self.txt_rfc.setPlaceholderText("RFC (opcional)")
        grid.addWidget(self.txt_rfc, row, 5)
        
        # ID (solo lectura)
        lbl_id = QLabel("ID:")
        lbl_id.setStyleSheet(label_style)
        lbl_id.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_id, row, 6)
        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        self.txt_id.setStyleSheet(INPUT_STYLE + "background-color: #E8E8E8; color: #666;")
        self.txt_id.setPlaceholderText("Auto")
        grid.addWidget(self.txt_id, row, 7)
        
        # Configurar columnas: labels estrechas, campos anchos
        for col in range(0, 8, 2):  # Columnas de labels (0, 2, 4, 6)
            grid.setColumnStretch(col, 0)  # Sin stretch para labels
            grid.setColumnMinimumWidth(col, 70)  # Ancho fijo para labels
        
        for col in range(1, 8, 2):  # Columnas de campos (1, 3, 5, 7)
            grid.setColumnStretch(col, 1)  # Stretch igual para todos los campos
        
        grupo_form.setLayout(grid)
        parent_layout.addWidget(grupo_form)

    def crear_tabla_proveedores(self, parent_layout):
        """Tabla con campos principales que ocupa todo el ancho"""
        widget_tabla = QWidget()
        layout_tabla = QVBoxLayout()
        layout_tabla.setContentsMargins(0, 0, 0, 0)
        layout_tabla.setSpacing(5)
        
        # Título de la tabla
        lbl_titulo = QLabel("📋 Lista de Proveedores")
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
            }
        """)
        layout_tabla.addWidget(lbl_titulo)
        
        # Modelo de tabla
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Email", "Teléfono"
        ])
        
        self.tabla_proveedores = QTableView()
        self.tabla_proveedores.setModel(self.tabla_model)
        self.tabla_proveedores.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_proveedores.setSelectionMode(QTableView.SingleSelection)
        self.tabla_proveedores.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_proveedores.setStyleSheet(TABLE_STYLE)
        self.tabla_proveedores.horizontalHeader().setStretchLastSection(True)
        self.tabla_proveedores.verticalHeader().setDefaultSectionSize(35)
        
        # Configurar header
        self.tabla_proveedores.selectionModel().selectionChanged.connect(self.actualizar_panel_detalle)
        
        header = self.tabla_proveedores.horizontalHeader()
        header.setFixedHeight(40)
        
        layout_tabla.addWidget(self.tabla_proveedores)
        widget_tabla.setLayout(layout_tabla)
        parent_layout.addWidget(widget_tabla, 7)  # 70% del espacio

    def showEvent(self, event):
        """Evento que se ejecuta cuando la ventana se muestra"""
        super().showEvent(event)
        
        # Esperar a que la ventana esté completamente renderizada
        self.layout().invalidate()
        self.layout().activate()

        # Ajustar columnas de la tabla
        QTimer.singleShot(50, self.ajustar_columnas_tabla)

        # Forzar actualización completa después de un breve retraso
        QTimer.singleShot(100, self.forzar_resize_completo)

    def forzar_resize_completo(self):
        """Forzar un resize completo para ajustar layouts y widgets"""
        # Actualizar geometria
        self.updateGeometry()

        # Invalidar y activar el layout
        if self.layout():
            self.layout().invalidate()
            self.layout().activate()

        #Forzar actualizacion visual
        self.update()

        # Ajustar columnas nuevamente
        self.ajustar_columnas_tabla()

    def ajustar_columnas_tabla(self):
        """Ajustar anchos de columnas con proporciones exactas"""
        header = self.tabla_proveedores.horizontalHeader()
        ancho_total = self.tabla_proveedores.viewport().width()
        
        # Proporciones: 10%, 35%, 10%, 35%, 10%
        anchos = [
            int(ancho_total * 0.10),  # ID
            int(ancho_total * 0.35),  # Nombre
            int(ancho_total * 0.10),  # Tipo
            int(ancho_total * 0.35),  # Email
            int(ancho_total * 0.10)   # Teléfono
        ]
        
        for i, ancho in enumerate(anchos):
            header.resizeSection(i, ancho)
            header.setSectionResizeMode(i, QHeaderView.Fixed)

    def crear_panel_detalle(self, parent_layout):
        """Panel lateral con detalles del proveedor seleccionado"""
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
        
        # Título
        titulo = QLabel("📄 Detalles del Proveedor")
        titulo.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00788E;
            padding: 8px;
            background: rgba(44, 213, 196, 0.2);
            border-radius: 5px;
        """)
        layout.addWidget(titulo)
        
        # Contenedor de detalles
        self.detalle_widget = QWidget()
        detalle_layout = QVBoxLayout()
        detalle_layout.setSpacing(5)
        
        # Crear labels de detalle
        self.labels_detalle = {}
        campos = [
            ('id', '🆔 ID:', '---'),
            ('nombre', '👤 Nombre:', '---'),
            ('tipo', '📌 Tipo:', '---'),
            ('email', '📧 Email:', '---'),
            ('telefono', '📞 Teléfono:', '---'),
            ('direccion', '🏠 Dirección:', '---'),
            ('ciudad', '🏙️ Ciudad:', '---'),
            ('estado', '📍 Estado:', '---'),
            ('cp', '📮 CP:', '---'),
            ('pais', '🌎 País:', '---'),
            ('rfc', '📋 RFC:', '---')
        ]
        
        for key, titulo, valor in campos:
            frame = self.crear_label_detalle(titulo, valor)
            self.labels_detalle[key] = frame
            detalle_layout.addWidget(frame)
            
            # Separador después del teléfono
            if key == 'telefono':
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("background-color: rgba(0, 120, 142, 0.3); max-height: 2px;")
                detalle_layout.addWidget(sep)
        
        detalle_layout.addStretch()
        self.detalle_widget.setLayout(detalle_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setWidget(self.detalle_widget)
        
        layout.addWidget(scroll)
        panel.setLayout(layout)
        parent_layout.addWidget(panel, 3)  # 30% del espacio

    def crear_label_detalle(self, titulo, valor):
        """Crear label individual para el panel de detalles"""
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
        layout.setSpacing(2)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-weight: bold; color: #666; font-size: 14px;")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("color: #333; font-size: 16px;")
        lbl_valor.setWordWrap(True)
        lbl_valor.setObjectName("valor")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        
        frame.setLayout(layout)
        return frame

    def crear_botones_principales(self, parent_layout):
        """Crear botones principales"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        

        botones_config = [
            ("btn_nuevo", "Nuevo", self.nuevo_proveedor),
            ("btn_guardar", "Guardar", self.guardar_proveedor),
            ("btn_editar", "Editar", self.editar_proveedor),
            ("btn_eliminar", "Eliminar", self.eliminar_proveedor),
            ("btn_buscar", "Buscar", self.buscar_proveedor),
            ("btn_limpiar", "Limpiar", self.limpiar_formulario),
            ("btn_cerrar", "Cerrar", self.cerrar_ventana) 
        ]
        

        for nombre_attr, texto, funcion in botones_config:
            btn = QPushButton(texto)
            btn.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)
            btn.clicked.connect(funcion)

            # Guardar referencia al botón como atributo de instancia
            setattr(self, nombre_attr, btn)
            layout.addWidget(btn)

        parent_layout.addLayout(layout)

    
    def actualizar_panel_detalle(self):
        """Actualizar panel de detalles cuando se selecciona un proveedor"""
        indice = self.tabla_proveedores.currentIndex()
        if not indice.isValid():
            return
        
        fila = indice.row()
        proveedor_id = int(self.tabla_model.item(fila, 0).text())

        try: 
            proveedores = db_helper.get_proveedores()
            proveedor = next((p for p in proveedores if p['id'] == proveedor_id), None)
        
            if proveedor:
                # Actualizar cada campo del detalle
                self.actualizar_label_valor(self.labels_detalle['id'], str(proveedor['id']))
                self.actualizar_label_valor(self.labels_detalle['nombre'], proveedor['nombre'])
                self.actualizar_label_valor(self.labels_detalle['tipo'], proveedor['tipo'])
                self.actualizar_label_valor(self.labels_detalle['email'], proveedor['email'])
                self.actualizar_label_valor(self.labels_detalle['telefono'], proveedor['telefono'])
                
                # Dirección completa
                direccion = f"{proveedor.get('calle', '')}\n{proveedor.get('colonia', '')}"
                self.actualizar_label_valor(self.labels_detalle['direccion'], direccion.strip()) 
                self.actualizar_label_valor(self.labels_detalle['ciudad'], proveedor['ciudad'])
                self.actualizar_label_valor(self.labels_detalle['estado'], proveedor['estado'])
                self.actualizar_label_valor(self.labels_detalle['cp'], proveedor['cp'])
                self.actualizar_label_valor(self.labels_detalle['pais'], proveedor.get('pais', 'México'))
                self.actualizar_label_valor(self.labels_detalle['rfc'], proveedor['rfc'] or '---')
        except Exception as e:
            print(f"Error al actualizar panel de detalles: {e}")

    def actualizar_label_valor(self, frame, valor):
        """Actualizar el valor en un label del panel de detalles"""
        for widget in frame.findChildren(QLabel):
            if widget.objectName() == "valor":
                widget.setText(valor if valor else "---")
                break

    # === OPERACIONES CRUD ===

    def nuevo_proveedor(self):
        """Preparar formulario para nuevo proveedor"""
        self.limpiar_formulario()
        self.txt_nombre.setFocus()

    def guardar_proveedor(self):
        """Guardar proveedor (nuevo o actualización)"""
        if not self.validar_formulario():
            return
        
        datos = self.obtener_datos_formulario()

        try:
            if self.modo_edicion and self.proveedor_en_edicion:
                if db_helper.actualizar_proveedor(self.proveedor_en_edicion['id'], datos):
                    self.mostrar_mensaje("Éxito", "Proveedor actualizado correctamente.", QMessageBox.Information)
                    self.cargar_datos_desde_bd()
                    self.cancelar_edicion()
                else:
                    self.mostrar_mensaje("Error", "No se pudo actualizar el proveedor.", QMessageBox.Critical)
            else:
                if db_helper.crear_proveedor(datos):
                    self.mostrar_mensaje("Éxito", "Proveedor agregado correctamente.", QMessageBox.Information)
                    self.cargar_datos_desde_bd()
                    self.limpiar_formulario()
                else:
                    self.mostrar_mensaje("Error", "No se pudo agregar el proveedor.", QMessageBox.Critical)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Ocurrió un error: {e}", QMessageBox.Critical)

    def editar_proveedor(self):
        """Cargar proveedor seleccionado para edición"""
        indice = self.tabla_proveedores.currentIndex()
        if not indice.isValid():
            self.mostrar_mensaje("Advertencia", "Seleccione un proveedor para editar.", QMessageBox.Warning)
            return
        
        fila = indice.row()
        proveedor_id = int(self.tabla_model.item(fila, 0).text())

        proveedor = db_helper.get_proveedores()
        proveedor = next((p for p in proveedor if p['id'] == proveedor_id), None)

        if proveedor:
            self.proveedor_en_edicion = proveedor
            self.modo_edicion = True
            self.cargar_datos_formulario(proveedor)
            self.btn_guardar.setText("Actualizar")

    def eliminar_proveedor(self):
        """Eliminar proveedor seleccionado"""
        indice = self.tabla_proveedores.currentIndex()
        if not indice.isValid():
            self.mostrar_mensaje("Advertencia", "Seleccione un proveedor para eliminar.", QMessageBox.Warning)
            return
        
        fila = indice.row()
        proveedor_id = int(self.tabla_model.item(fila, 0).text())
        nombre = self.tabla_model.item(fila, 1).text()

        respuesta = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar proveedor '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
    
            if db_helper.eliminar_proveedor(proveedor_id):
                self.mostrar_mensaje("Éxito", "Proveedor eliminado", QMessageBox.Information)
                self.cargar_datos_desde_bd()
                self.limpiar_formulario()
            else:
                self.mostrar_mensaje("Error", "No se pudo eliminar", QMessageBox.Critical)

    def buscar_proveedor(self):
        """Buscar proveedor por nombre"""
        texto, ok = QInputDialog.getText(self, "Buscar", "Nombre a buscar:")
        if ok and texto: 
            try:
                resultados = db_helper.buscar_proveedores(texto)
                self.actualizar_tabla(resultados)
            except Exception as e:
                self.mostrar_mensaje("Error", f"No se pudo buscar: {e}", QMessageBox.Critical)

    # === FUNCIONES AUXILIARES ===

    def obtener_datos_formulario(self):
        """Obtener datos del formulario como diccionario"""
        return {
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

    def cargar_datos_formulario(self, proveedor):
        """Cargar datos del proveedor en el formulario"""
        self.txt_id.setText(str(proveedor['id']))
        self.txt_nombre.setText(proveedor['nombre'])
        self.cmb_tipo.setCurrentText(proveedor['tipo'])
        self.txt_email.setText(proveedor['email'])
        self.txt_telefono.setText(proveedor['telefono'])
        self.txt_calle.setText(proveedor.get('calle', ''))
        self.txt_colonia.setText(proveedor.get('colonia', ''))
        self.txt_cp.setText(proveedor['cp'])
        self.txt_ciudad.setText(proveedor['ciudad'])
        self.cmb_estado.setCurrentText(proveedor['estado'])
        self.txt_pais.setText(proveedor.get('pais', 'México'))
        self.txt_rfc.setText(proveedor['rfc'])

    def validar_formulario(self):
        """Validar datos del formulario"""
        # Validación del nombre (obligatorio)
        if not self.txt_nombre.text().strip():
            self.mostrar_mensaje("Error", "El nombre es obligatorio.", QMessageBox.Critical)
            self.txt_nombre.setFocus()
            return False
        
        # Validación del email (opcional pero si existe debe ser válido)
        email = self.txt_email.text().strip()
        if email:  # Solo validar si se ingresó un email
            # Patrón de expresión regular para email
            patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(patron_email, email):
                self.mostrar_mensaje("Error", "Formato de email inválido.", QMessageBox.Critical)
                self.txt_email.setFocus()
                return False
        
        # Validación del teléfono (opcional pero si existe debe ser válido)
        telefono = self.txt_telefono.text().strip()
        if telefono:
            # Patrón para teléfono mexicano (acepta varios formatos)
            patron_telefono = r'^[\d\s\(\)\-\+]+$'
            if not re.match(patron_telefono, telefono) or len(re.sub(r'\D', '', telefono)) < 10:
                self.mostrar_mensaje("Error", "Formato de teléfono inválido. Debe contener al menos 10 dígitos.", QMessageBox.Critical)
                self.txt_telefono.setFocus()
                return False
        
        # Validación del RFC (opcional pero si existe debe ser válido)
        rfc = self.txt_rfc.text().strip()
        if rfc:
            # Patrón para RFC mexicano (persona física o moral)
            patron_rfc = r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$'
            if not re.match(patron_rfc, rfc.upper()):
                self.mostrar_mensaje("Error", "Formato de RFC inválido.", QMessageBox.Critical)
                self.txt_rfc.setFocus()
                return False
        
        # Validación del código postal (opcional pero si existe debe ser válido)
        cp = self.txt_cp.text().strip()
        if cp:
            # Patrón para código postal de 5 dígitos
            patron_cp = r'^\d{5}$'
            if not re.match(patron_cp, cp):
                self.mostrar_mensaje("Error", "El código postal debe contener exactamente 5 dígitos.", QMessageBox.Critical)
                self.txt_cp.setFocus()
                return False
        
        return True

    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        self.txt_id.clear()
        self.txt_nombre.clear()
        self.cmb_tipo.setCurrentIndex(0)
        self.txt_email.clear()
        self.txt_telefono.clear()
        self.txt_calle.clear()
        self.txt_colonia.clear()
        self.txt_cp.clear()
        self.txt_ciudad.clear()
        self.cmb_estado.setCurrentText("Jalisco")
        self.txt_pais.setText("México")
        self.txt_rfc.clear()
        self.cancelar_edicion()

    def cancelar_edicion(self):
        """Cancelar modo de edición"""
        self.modo_edicion = False
        self.proveedor_en_edicion = None
        self.btn_guardar.setText("Guardar")

    def cargar_datos_desde_bd(self):
        """Cargar datos de proveedores desde la base de datos"""
        try:
            proveedores = db_helper.get_proveedores()
            self.actualizar_tabla(proveedores)
        except Exception as e:
            self.mostrar_mensaje("Error", f"No se pudieron cargar los datos: {e}", QMessageBox.Critical)

    def actualizar_tabla(self, proveedores):
        """Actualizar datos de la tabla"""
        self.tabla_model.setRowCount(0)
        
        for proveedor in proveedores:
            fila = [
                QStandardItem(str(proveedor['id'])),
                QStandardItem(proveedor['nombre']),
                QStandardItem(proveedor['tipo']),
                QStandardItem(proveedor['email']),
                QStandardItem(proveedor['telefono'])
            ]
            
            for item in fila:
                item.setTextAlignment(Qt.AlignCenter)
            
            self.tabla_model.appendRow(fila)

    def mostrar_mensaje(self, titulo, mensaje, tipo):
        """Mostrar mensaje al usuario"""
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()

    def closeEvent(self, event):
        """Evento al cerrar la ventana"""
        self.limpiar_formulario()

        self.setGeometry(100, 100, 1400, 800)
        event.accept()

    def cerrar_ventana(self):
        """Cerrar la ventana"""
        
        self.setGeometry(100, 100, 1400, 800)

        self.limpiar_formulario()

        self.close()

    def resizeEvent(self, event):
        """Evento de resize para ajustar columnas de la tabla"""
        super().resizeEvent(event)
        if hasattr(self, 'tabla_proveedores'):
            QTimer.singleShot(50, self.ajustar_columnas_tabla)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ProveedoresWindow()
    window.show()
    sys.exit(app.exec_())