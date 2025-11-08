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

from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE, 
    LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, MESSAGE_BOX_STYLE
)

from gui.api_client import api_client as db_helper
from gui.websocket_client import ws_client

try:
    from gui.estado_cuenta_proveedor_dialog import EstadoCuentaProveedorDialog
except ImportError as e:
    print(f"Error al importar EstadoCuentaProveedorDialog: {e}")
    EstadoCuentaProveedorDialog = None

class ProveedoresWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Gestión de Proveedores")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.setMinimumSize(1200, 700)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        self.proveedor_en_edicion = None
        self.modo_edicion = False
        self._datos_cargados = False
        
        self.setup_ui()

        if ws_client:
            ws_client.proveedor_creado.connect(self.on_notificacion_remota)
            ws_client.proveedor_actualizado.connect(self.on_notificacion_remota)
            ws_client.proveedor_eliminado.connect(self.on_notificacion_remota)
        
        self.setWindowState(Qt.WindowMaximized)
        QTimer.singleShot(100, self._cargar_datos_inicial)

    def _cargar_datos_inicial(self):
        if not self._datos_cargados:
            self.cargar_datos_desde_bd()
            self._datos_cargados = True

    def on_notificacion_remota(self, data):
        self.cargar_datos_desde_bd()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        self.crear_formulario_proveedor(main_layout)
        
        contenedor_horizontal = QHBoxLayout()
        contenedor_horizontal.setSpacing(10)
        
        self.crear_tabla_proveedores(contenedor_horizontal)
        
        self.crear_panel_detalle(contenedor_horizontal)
        
        main_layout.addLayout(contenedor_horizontal, 10)
        
        self.crear_botones_principales(main_layout)
        
        self.setLayout(main_layout)

    def crear_formulario_proveedor(self, parent_layout):
        grupo_form = QGroupBox()
        grupo_form.setStyleSheet(GROUP_BOX_STYLE)
        grupo_form.setMaximumHeight(180) 

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 15)
        
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
        
        row = 0
        
        lbl_nombre = QLabel("Nombre:")
        lbl_nombre.setStyleSheet(label_style)
        lbl_nombre.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_nombre, row, 0)
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setStyleSheet(INPUT_STYLE)
        self.txt_nombre.setPlaceholderText("Nombre completo del proveedor")
        grid.addWidget(self.txt_nombre, row, 1)
        
        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setStyleSheet(label_style)
        lbl_tipo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_tipo, row, 2)
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.setStyleSheet(INPUT_STYLE)
        self.cmb_tipo.addItems(["Particular", "Empresa", "Gobierno"])
        grid.addWidget(self.cmb_tipo, row, 3)
        
        lbl_email = QLabel("Email:")
        lbl_email.setStyleSheet(label_style)
        lbl_email.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_email, row, 4)
        self.txt_email = QLineEdit()
        self.txt_email.setStyleSheet(INPUT_STYLE)
        self.txt_email.setPlaceholderText("correo@ejemplo.com")
        grid.addWidget(self.txt_email, row, 5)
        
        lbl_telefono = QLabel("Teléfono:")
        lbl_telefono.setStyleSheet(label_style)
        lbl_telefono.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_telefono, row, 6)
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setStyleSheet(INPUT_STYLE)
        self.txt_telefono.setPlaceholderText("(123) 456-7890")
        grid.addWidget(self.txt_telefono, row, 7)
        
        row = 1
        
        lbl_calle = QLabel("Calle:")
        lbl_calle.setStyleSheet(label_style)
        lbl_calle.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_calle, row, 0)
        self.txt_calle = QLineEdit()
        self.txt_calle.setStyleSheet(INPUT_STYLE)
        self.txt_calle.setPlaceholderText("Calle y número")
        grid.addWidget(self.txt_calle, row, 1)
        
        lbl_colonia = QLabel("Colonia:")
        lbl_colonia.setStyleSheet(label_style)
        lbl_colonia.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_colonia, row, 2)
        self.txt_colonia = QLineEdit()
        self.txt_colonia.setStyleSheet(INPUT_STYLE)
        self.txt_colonia.setPlaceholderText("Colonia o fraccionamiento")
        grid.addWidget(self.txt_colonia, row, 3)
        
        lbl_cp = QLabel("C.P.:")
        lbl_cp.setStyleSheet(label_style)
        lbl_cp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_cp, row, 4)
        self.txt_cp = QLineEdit()
        self.txt_cp.setStyleSheet(INPUT_STYLE)
        self.txt_cp.setPlaceholderText("00000")
        self.txt_cp.setMaxLength(5)
        grid.addWidget(self.txt_cp, row, 5)
        
        lbl_ciudad = QLabel("Ciudad:")
        lbl_ciudad.setStyleSheet(label_style)
        lbl_ciudad.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_ciudad, row, 6)
        self.txt_ciudad = QLineEdit()
        self.txt_ciudad.setStyleSheet(INPUT_STYLE)
        self.txt_ciudad.setPlaceholderText("Ciudad")
        grid.addWidget(self.txt_ciudad, row, 7)
        
        row = 2
        
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
        
        lbl_pais = QLabel("País:")
        lbl_pais.setStyleSheet(label_style)
        lbl_pais.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_pais, row, 2)
        self.txt_pais = QLineEdit()
        self.txt_pais.setStyleSheet(INPUT_STYLE)
        self.txt_pais.setText("México")
        self.txt_pais.setPlaceholderText("País")
        grid.addWidget(self.txt_pais, row, 3)
        
        lbl_rfc = QLabel("RFC:")
        lbl_rfc.setStyleSheet(label_style)
        lbl_rfc.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_rfc, row, 4)
        self.txt_rfc = QLineEdit()
        self.txt_rfc.setStyleSheet(INPUT_STYLE)
        self.txt_rfc.setPlaceholderText("RFC (opcional)")
        grid.addWidget(self.txt_rfc, row, 5)
        
        lbl_id = QLabel("ID:")
        lbl_id.setStyleSheet(label_style)
        lbl_id.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl_id, row, 6)
        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        self.txt_id.setStyleSheet(INPUT_STYLE + "background-color: #E8E8E8; color: #666;")
        self.txt_id.setPlaceholderText("Auto")
        grid.addWidget(self.txt_id, row, 7)
        
        for col in range(0, 8, 2):  
            grid.setColumnStretch(col, 0)  
            grid.setColumnMinimumWidth(col, 70)  
        
        for col in range(1, 8, 2):  
            grid.setColumnStretch(col, 1)  
        
        grupo_form.setLayout(grid)
        parent_layout.addWidget(grupo_form)

    def crear_tabla_proveedores(self, parent_layout):
        widget_tabla = QWidget()
        layout_tabla = QVBoxLayout()
        layout_tabla.setContentsMargins(0, 0, 0, 0)
        layout_tabla.setSpacing(5)
        
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
        
        self.tabla_proveedores.selectionModel().selectionChanged.connect(self.actualizar_panel_detalle)
        
        header = self.tabla_proveedores.horizontalHeader()
        header.setFixedHeight(40)
        
        layout_tabla.addWidget(self.tabla_proveedores)
        widget_tabla.setLayout(layout_tabla)
        parent_layout.addWidget(widget_tabla, 7) 

    def forzar_resize_completo(self):
        self.updateGeometry()

        if self.layout():
            self.layout().invalidate()
            self.layout().activate()

        self.update()
        self.ajustar_columnas_tabla()

    def ajustar_columnas_tabla(self):
        header = self.tabla_proveedores.horizontalHeader()
        ancho_total = self.tabla_proveedores.viewport().width()
        
        if ancho_total <= 0:
            return

        anchos = [
            int(ancho_total * 0.10),  
            int(ancho_total * 0.35),  
            int(ancho_total * 0.10),  
            int(ancho_total * 0.35),  
            int(ancho_total * 0.10)   
        ]
        
        for i, ancho in enumerate(anchos):
            header.resizeSection(i, ancho)
            header.setSectionResizeMode(i, QHeaderView.Fixed)

    def crear_panel_detalle(self, parent_layout):
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
        
        self.detalle_widget = QWidget()
        detalle_layout = QVBoxLayout()
        detalle_layout.setSpacing(5)
        
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
            
            if key == 'telefono':
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("background-color: rgba(0, 120, 142, 0.3); max-height: 2px;")
                detalle_layout.addWidget(sep)
        
        detalle_layout.addStretch()
        self.detalle_widget.setLayout(detalle_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setWidget(self.detalle_widget)
        
        layout.addWidget(scroll)
        self.btn_estado_cuenta_prov = QPushButton("Ver Estado de Cuenta")
        self.btn_estado_cuenta_prov.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        self.btn_estado_cuenta_prov.setCursor(Qt.PointingHandCursor)
        self.btn_estado_cuenta_prov.clicked.connect(self.abrir_estado_cuenta_proveedor)
        
        layout.addWidget(self.btn_estado_cuenta_prov) 
        panel.setLayout(layout)
        parent_layout.addWidget(panel, 3)  

    def crear_label_detalle(self, titulo, valor):
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

            setattr(self, nombre_attr, btn)
            layout.addWidget(btn)

        parent_layout.addLayout(layout)

    def abrir_estado_cuenta_proveedor(self):
        if EstadoCuentaProveedorDialog is None:
            self.mostrar_error("No se pudo cargar el módulo de Estado de Cuenta de Proveedor.")
            return

        indice = self.tabla_proveedores.currentIndex()
        if not indice.isValid():
            self.mostrar_advertencia("Seleccione un proveedor para ver su estado de cuenta.")
            return
        
        fila = indice.row()
        try:
            proveedor_id = int(self.tabla_model.item(fila, 0).text())
            nombre_proveedor = self.tabla_model.item(fila, 1).text()
        except Exception as e:
            self.mostrar_error(f"No se pudo obtener la información del proveedor: {e}")
            return

        dialog = EstadoCuentaProveedorDialog(proveedor_id, nombre_proveedor, self)
        dialog.exec_()
    
    def actualizar_panel_detalle(self):
        indice = self.tabla_proveedores.currentIndex()
        if not indice.isValid():
            return
        
        fila = indice.row()
        proveedor_id = int(self.tabla_model.item(fila, 0).text())

        try: 
            proveedores = db_helper.get_proveedores()
            proveedor = next((p for p in proveedores if p['id'] == proveedor_id), None)
        
            if proveedor:
                self.actualizar_label_valor(self.labels_detalle['id'], str(proveedor.get('id', 'N/A')))
                self.actualizar_label_valor(self.labels_detalle['nombre'], proveedor.get('nombre', '---'))
                self.actualizar_label_valor(self.labels_detalle['tipo'], proveedor.get('tipo', '---'))
                self.actualizar_label_valor(self.labels_detalle['email'], proveedor.get('email', '---'))
                self.actualizar_label_valor(self.labels_detalle['telefono'], proveedor.get('telefono', '---'))
                
                direccion = f"{proveedor.get('calle', '')}\n{proveedor.get('colonia', '')}"
                self.actualizar_label_valor(self.labels_detalle['direccion'], direccion.strip() or '---') 
                self.actualizar_label_valor(self.labels_detalle['ciudad'], proveedor.get('ciudad', '---'))
                self.actualizar_label_valor(self.labels_detalle['estado'], proveedor.get('estado', '---'))
                self.actualizar_label_valor(self.labels_detalle['cp'], proveedor.get('cp', '---'))
                self.actualizar_label_valor(self.labels_detalle['pais'], proveedor.get('pais', 'México'))
                self.actualizar_label_valor(self.labels_detalle['rfc'], proveedor.get('rfc', '---') or '---')
        except Exception as e:
            print(f"Error al actualizar panel de detalles: {e}")

    def actualizar_label_valor(self, frame, valor):
        for widget in frame.findChildren(QLabel):
            if widget.objectName() == "valor":
                widget.setText(valor if valor else "---")
                break

    def nuevo_proveedor(self):
        self.limpiar_formulario()
        self.txt_nombre.setFocus()

    def guardar_proveedor(self):
        if not self.validar_formulario():
            return
        
        datos = self.obtener_datos_formulario()

        try:
            if self.modo_edicion and self.proveedor_en_edicion:
                if db_helper.actualizar_proveedor(self.proveedor_en_edicion['id'], datos):
                    self.mostrar_exito("Proveedor actualizado correctamente.")
                    self.cargar_datos_desde_bd()
                    self.cancelar_edicion()
                else:
                    self.mostrar_error("No se pudo actualizar el proveedor.")
            else:
                if db_helper.crear_proveedor(datos):
                    self.mostrar_exito("Proveedor agregado correctamente.")
                    self.cargar_datos_desde_bd()
                    self.limpiar_formulario()
                else:
                    self.mostrar_error("No se pudo agregar el proveedor.")
        except Exception as e:
            self.mostrar_error(f"Ocurrió un error: {e}")

    def editar_proveedor(self):
        indice = self.tabla_proveedores.currentIndex()
        if not indice.isValid():
            self.mostrar_advertencia("Seleccione un proveedor para editar.")
            return
        
        fila = indice.row()
        proveedor_id = int(self.tabla_model.item(fila, 0).text())

        proveedores = db_helper.get_proveedores()
        proveedor = next((p for p in proveedores if p['id'] == proveedor_id), None)

        if proveedor:
            self.proveedor_en_edicion = proveedor
            self.modo_edicion = True
            self.cargar_datos_formulario(proveedor)
            self.btn_guardar.setText("Actualizar")

    def eliminar_proveedor(self):
        indice = self.tabla_proveedores.currentIndex()
        if not indice.isValid():
            self.mostrar_advertencia("Seleccione un proveedor para eliminar.")
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
                self.mostrar_exito("Proveedor eliminado")
                self.cargar_datos_desde_bd()
                self.limpiar_formulario()
            else:
                self.mostrar_error("No se pudo eliminar")

    def buscar_proveedor(self):
        texto, ok = QInputDialog.getText(self, "Buscar", "Nombre a buscar:")
        if ok and texto: 
            try:
                resultados = db_helper.buscar_proveedores(texto)
                self.actualizar_tabla_con_datos(resultados)
            except Exception as e:
                self.mostrar_error(f"No se pudo buscar: {e}")

    def obtener_datos_formulario(self):
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
        self.txt_id.setText(str(proveedor.get('id', '')))
        self.txt_nombre.setText(proveedor.get('nombre', ''))
        self.cmb_tipo.setCurrentText(proveedor.get('tipo', 'Particular'))
        self.txt_email.setText(proveedor.get('email', ''))
        self.txt_telefono.setText(proveedor.get('telefono', ''))
        self.txt_calle.setText(proveedor.get('calle', ''))
        self.txt_colonia.setText(proveedor.get('colonia', ''))
        self.txt_cp.setText(proveedor.get('cp', ''))
        self.txt_ciudad.setText(proveedor.get('ciudad', ''))
        self.cmb_estado.setCurrentText(proveedor.get('estado', 'Jalisco'))
        self.txt_pais.setText(proveedor.get('pais', 'México'))
        self.txt_rfc.setText(proveedor.get('rfc', ''))

    def validar_formulario(self):
        if not self.txt_nombre.text().strip():
            self.mostrar_error("El nombre es obligatorio.")
            self.txt_nombre.setFocus()
            return False
        
        email = self.txt_email.text().strip()
        if email:  
            patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(patron_email, email):
                self.mostrar_error("Formato de email inválido.")
                self.txt_email.setFocus()
                return False
        
        telefono = self.txt_telefono.text().strip()
        if telefono:
            patron_telefono = r'^[\d\s\(\)\-\+]+$'
            if not re.match(patron_telefono, telefono) or len(re.sub(r'\D', '', telefono)) < 10:
                self.mostrar_error("Formato de teléfono inválido. Debe contener al menos 10 dígitos.")
                self.txt_telefono.setFocus()
                return False
        
        rfc = self.txt_rfc.text().strip()
        if rfc:
            patron_rfc = r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$'
            if not re.match(patron_rfc, rfc.upper()):
                self.mostrar_error("Formato de RFC inválido.")
                self.txt_rfc.setFocus()
                return False
        
        cp = self.txt_cp.text().strip()
        if cp:
            patron_cp = r'^\d{5}$'
            if not re.match(patron_cp, cp):
                self.mostrar_error("El código postal debe contener exactamente 5 dígitos.")
                self.txt_cp.setFocus()
                return False
        
        return True

    def limpiar_formulario(self):
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
        self.cargar_datos_desde_bd()

    def cancelar_edicion(self):
        self.modo_edicion = False
        self.proveedor_en_edicion = None
        self.btn_guardar.setText("Guardar")

    def cargar_datos_desde_bd(self):
        try:
            proveedores = db_helper.get_proveedores()
            self.actualizar_tabla_con_datos(proveedores)
        except Exception as e:
            self.mostrar_error(f"No se pudieron cargar los datos: {e}")

    def _crear_item(self, texto, alineacion):
        item = QStandardItem(str(texto)) 
        item.setTextAlignment(alineacion)
        return item

    def actualizar_tabla_con_datos(self, proveedores):
        self.tabla_model.setRowCount(0)
        
        for proveedor in proveedores:
            fila = [
                self._crear_item(proveedor.get('id', 'N/A'), Qt.AlignCenter),
                self._crear_item(proveedor.get('nombre', 'Sin Nombre'), Qt.AlignCenter),
                self._crear_item(proveedor.get('tipo', 'Sin Tipo'), Qt.AlignCenter),
                self._crear_item(proveedor.get('email', ''), Qt.AlignCenter),
                self._crear_item(proveedor.get('telefono', ''), Qt.AlignCenter)
            ]
            self.tabla_model.appendRow(fila)

    def _mostrar_mensaje(self, icono, titulo, mensaje):
        msg_box = QMessageBox(icono, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()

    def mostrar_advertencia(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Warning, "Advertencia", mensaje)
    
    def mostrar_error(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Critical, "Error", mensaje)
    
    def mostrar_exito(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Information, "Éxito", mensaje)

    def closeEvent(self, event):
        self.limpiar_formulario()
        event.accept()

    def cerrar_ventana(self):
        self.limpiar_formulario()
        self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'tabla_proveedores'):
            QTimer.singleShot(50, self.ajustar_columnas_tabla)

    def showEvent(self, event):
        super().showEvent(event)
        
        if not self._datos_cargados:
            self.cargar_datos_desde_bd()
            self._datos_cargados = True
            
        self.layout().invalidate()
        self.layout().activate()

        QTimer.singleShot(50, self.ajustar_columnas_tabla)
        QTimer.singleShot(100, self.forzar_resize_completo)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    try:
        from gui.api_client import api_client as db_helper
    except ImportError:
        print("Error: No se pudo importar api_client. Asegúrate de que el servidor esté corriendo.")
        sys.exit(1)
        
    window = ProveedoresWindow()
    window.show()
    sys.exit(app.exec_())