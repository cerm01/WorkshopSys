import sys
import os
import shutil
import re
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QTableView, QHeaderView, QMessageBox,
    QFileDialog, QComboBox, QCheckBox, QGroupBox, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import (
    QStandardItemModel, QStandardItem, QPixmap,
    QPainter, QPainterPath, QImage
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.api_client import api_client as db_helper
from gui.websocket_client import ws_client

from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, GROUP_BOX_STYLE, LABEL_STYLE, INPUT_STYLE,
    BUTTON_STYLE_2, TABLE_STYLE, MESSAGE_BOX_STYLE
)

def generar_hash_password(password: str) -> str:
    """Generar hash SHA256 de contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

class ConfiguracionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Sistema")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setMinimumSize(1000, 700)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)
        
        self.usuario_en_edicion_id = None
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logo_data = None  # Guardamos bytes en lugar de path
        
        self.setup_ui()
        
        if ws_client:
            pass
        
        # Cargar datos iniciales
        self.cargar_datos_empresa()
        self.cargar_usuarios()

    def on_notificacion_remota(self, data):
        self.cargar_usuarios()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 150);
                color: #333;
                padding: 15px 30px;
                margin-right: 2px;
                border-radius: 5px 5px 0 0;
                font-weight: bold;
                font-size: 16px;
                min-width: 280px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(
                   x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2CD5C4, stop: 1 #00788E
                );
                color: white;
            }
            QTabBar::tab:hover {
                background: rgba(44, 213, 196, 0.3);
            }
        """)
        
        # Crear pestañas
        self.tabs.addTab(self.crear_tab_empresa(), "DATOS DE LA EMPRESA")
        self.tabs.addTab(self.crear_tab_usuarios(), "USUARIOS")
        self.tabs.addTab(self.crear_tab_respaldo(), "RESPALDO")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
    
    # ==================== TAB EMPRESA (MODIFICADO) ====================
    
    def crear_tab_empresa(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Grupo: Datos Generales
        grupo_general = QGroupBox()
        grupo_general.setStyleSheet(GROUP_BOX_STYLE)
        grid_general = QGridLayout()
        grid_general.setSpacing(10)
        
        lbl_nombre = QLabel("Nombre Comercial *")
        lbl_nombre.setStyleSheet(LABEL_STYLE)
        self.txt_nombre_comercial = QLineEdit()
        self.txt_nombre_comercial.setStyleSheet(INPUT_STYLE)
        
        lbl_razon = QLabel("Razón Social")
        lbl_razon.setStyleSheet(LABEL_STYLE)
        self.txt_razon_social = QLineEdit()
        self.txt_razon_social.setStyleSheet(INPUT_STYLE)
        
        lbl_rfc = QLabel("RFC")
        lbl_rfc.setStyleSheet(LABEL_STYLE)
        self.txt_rfc_empresa = QLineEdit()
        self.txt_rfc_empresa.setStyleSheet(INPUT_STYLE)
        self.txt_rfc_empresa.setMaxLength(13)
        
        grid_general.addWidget(lbl_nombre, 0, 0)
        grid_general.addWidget(self.txt_nombre_comercial, 0, 1)
        grid_general.addWidget(lbl_razon, 1, 0)
        grid_general.addWidget(self.txt_razon_social, 1, 1)
        grid_general.addWidget(lbl_rfc, 2, 0)
        grid_general.addWidget(self.txt_rfc_empresa, 2, 1)
        
        grupo_general.setLayout(grid_general)
        layout.addWidget(grupo_general) # <-- Directo a 'layout'
        
        # Grupo: Dirección
        grupo_direccion = QGroupBox()
        grupo_direccion.setStyleSheet(GROUP_BOX_STYLE)
        grid_dir = QGridLayout()
        grid_dir.setSpacing(10)
        
        lbl_calle = QLabel("Calle")
        lbl_calle.setStyleSheet(LABEL_STYLE)
        self.txt_calle_empresa = QLineEdit()
        self.txt_calle_empresa.setStyleSheet(INPUT_STYLE)
        
        lbl_colonia = QLabel("Colonia")
        lbl_colonia.setStyleSheet(LABEL_STYLE)
        self.txt_colonia_empresa = QLineEdit()
        self.txt_colonia_empresa.setStyleSheet(INPUT_STYLE)
        
        lbl_ciudad = QLabel("Ciudad")
        lbl_ciudad.setStyleSheet(LABEL_STYLE)
        self.txt_ciudad_empresa = QLineEdit()
        self.txt_ciudad_empresa.setStyleSheet(INPUT_STYLE)
        
        lbl_estado = QLabel("Estado")
        lbl_estado.setStyleSheet(LABEL_STYLE)
        self.txt_estado_empresa = QLineEdit()
        self.txt_estado_empresa.setStyleSheet(INPUT_STYLE)
        
        lbl_cp = QLabel("Código Postal")
        lbl_cp.setStyleSheet(LABEL_STYLE)
        self.txt_cp_empresa = QLineEdit()
        self.txt_cp_empresa.setStyleSheet(INPUT_STYLE)
        self.txt_cp_empresa.setMaxLength(5)
        
        grid_dir.addWidget(lbl_calle, 0, 0)
        grid_dir.addWidget(self.txt_calle_empresa, 0, 1)
        grid_dir.addWidget(lbl_colonia, 0, 2)
        grid_dir.addWidget(self.txt_colonia_empresa, 0, 3)
        grid_dir.addWidget(lbl_ciudad, 1, 0)
        grid_dir.addWidget(self.txt_ciudad_empresa, 1, 1)
        grid_dir.addWidget(lbl_estado, 1, 2)
        grid_dir.addWidget(self.txt_estado_empresa, 1, 3)
        grid_dir.addWidget(lbl_cp, 2, 0)
        grid_dir.addWidget(self.txt_cp_empresa, 2, 1)
        
        grupo_direccion.setLayout(grid_dir)
        layout.addWidget(grupo_direccion) # <-- Directo a 'layout'
        
        # Grupo: Contacto
        grupo_contacto = QGroupBox()
        grupo_contacto.setStyleSheet(GROUP_BOX_STYLE)
        grid_contacto = QGridLayout()
        grid_contacto.setSpacing(10)
        
        lbl_tel1 = QLabel("Teléfono 1")
        lbl_tel1.setStyleSheet(LABEL_STYLE)
        self.txt_tel1_empresa = QLineEdit()
        self.txt_tel1_empresa.setStyleSheet(INPUT_STYLE)
        
        lbl_tel2 = QLabel("Teléfono 2")
        lbl_tel2.setStyleSheet(LABEL_STYLE)
        self.txt_tel2_empresa = QLineEdit()
        self.txt_tel2_empresa.setStyleSheet(INPUT_STYLE)
        
        lbl_email = QLabel("Email")
        lbl_email.setStyleSheet(LABEL_STYLE)
        self.txt_email_empresa = QLineEdit()
        self.txt_email_empresa.setStyleSheet(INPUT_STYLE)
        
        lbl_web = QLabel("Sitio Web")
        lbl_web.setStyleSheet(LABEL_STYLE)
        self.txt_web_empresa = QLineEdit()
        self.txt_web_empresa.setStyleSheet(INPUT_STYLE)
        
        grid_contacto.addWidget(lbl_tel1, 0, 0)
        grid_contacto.addWidget(self.txt_tel1_empresa, 0, 1)
        grid_contacto.addWidget(lbl_tel2, 0, 2)
        grid_contacto.addWidget(self.txt_tel2_empresa, 0, 3)
        grid_contacto.addWidget(lbl_email, 1, 0)
        grid_contacto.addWidget(self.txt_email_empresa, 1, 1)
        grid_contacto.addWidget(lbl_web, 1, 2)
        grid_contacto.addWidget(self.txt_web_empresa, 1, 3)
        
        grupo_contacto.setLayout(grid_contacto)
        layout.addWidget(grupo_contacto) # <-- Directo a 'layout'
        
        # Sección Logo
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(10, 15, 10, 15)
        
        self.lbl_logo_preview = QLabel("Sin logo")
        self.lbl_logo_preview.setFixedSize(150, 150)
        self.lbl_logo_preview.setStyleSheet("""
            QLabel {
                background: white;
                border-radius: 75px;
                border: 2px solid #00788E;
            }
        """)
        self.lbl_logo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_logo_preview.setScaledContents(False)
        
        btn_cargar_logo = QPushButton("Cargar Logo")
        btn_cargar_logo.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_cargar_logo.clicked.connect(self.cargar_logo)
        btn_cargar_logo.setFixedHeight(60)
        
        btn_quitar_logo = QPushButton("Quitar Logo")
        btn_quitar_logo.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_quitar_logo.clicked.connect(self.quitar_logo)
        btn_quitar_logo.setFixedHeight(60)
        
        logo_btns = QVBoxLayout()
        logo_btns.addWidget(btn_cargar_logo)
        logo_btns.addWidget(btn_quitar_logo)
        logo_btns.addStretch()
        
        logo_layout.addWidget(self.lbl_logo_preview)
        logo_layout.addLayout(logo_btns)
        logo_layout.addStretch()
        
        layout.addLayout(logo_layout)
        
        # Botón Guardar
        layout.addStretch()
        btn_guardar_empresa = QPushButton("Guardar Configuración")
        btn_guardar_empresa.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_guardar_empresa.setFixedHeight(60)
        btn_guardar_empresa.clicked.connect(self.guardar_empresa)
        layout.addWidget(btn_guardar_empresa)
        
        tab.setLayout(layout)
        return tab

    def _crear_pixmap_circular(self, pixmap_o_bytes, tamanio=150):
        """Crear pixmap circular desde QPixmap o bytes"""
        if isinstance(pixmap_o_bytes, bytes):
            # Convertir bytes a QPixmap
            qimage = QImage()
            qimage.loadFromData(pixmap_o_bytes)
            pixmap_original = QPixmap.fromImage(qimage)
        else:
            pixmap_original = pixmap_o_bytes
            
        if pixmap_original.isNull():
            return QPixmap()

        pixmap_escalado = pixmap_original.scaled(
            tamanio, tamanio, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )

        pixmap_redondo = QPixmap(tamanio, tamanio)
        pixmap_redondo.fill(Qt.transparent)

        painter = QPainter(pixmap_redondo)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        path = QPainterPath()
        path.addEllipse(0, 0, tamanio, tamanio)
        painter.setClipPath(path)

        x = (tamanio - pixmap_escalado.width()) / 2
        y = (tamanio - pixmap_escalado.height()) / 2
        painter.drawPixmap(int(x), int(y), pixmap_escalado)
        painter.end()
        
        return pixmap_redondo

    def cargar_logo(self):
        """Cargar logo y convertir a bytes"""
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Logo", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if archivo:
            try:
                # Leer archivo como bytes
                with open(archivo, 'rb') as f:
                    self.logo_data = f.read()
                
                # Mostrar preview
                pixmap_circular = self._crear_pixmap_circular(self.logo_data)
                if not pixmap_circular.isNull():
                    self.lbl_logo_preview.setPixmap(pixmap_circular)
                else:
                    self.mostrar_mensaje("Error", "No se pudo cargar la imagen", QMessageBox.Critical)
                    self.logo_data = None
                    
            except Exception as e:
                self.mostrar_mensaje("Error", f"Error al cargar logo: {e}", QMessageBox.Critical)
                self.logo_data = None
    
    def quitar_logo(self):
        """Quitar logo"""
        self.logo_data = None
        self.lbl_logo_preview.clear()
        self.lbl_logo_preview.setText("Sin logo")
    
    def cargar_datos_empresa(self):
        """Cargar datos de la empresa desde BD"""
        # Esta llamada ahora usa api_client (renombrado como db_helper)
        datos = db_helper.get_config_empresa()
        if datos:
            self.txt_nombre_comercial.setText(datos.get('nombre_comercial', ''))
            self.txt_razon_social.setText(datos.get('razon_social', ''))
            self.txt_rfc_empresa.setText(datos.get('rfc', ''))
            self.txt_calle_empresa.setText(datos.get('calle', ''))
            self.txt_colonia_empresa.setText(datos.get('colonia', ''))
            self.txt_ciudad_empresa.setText(datos.get('ciudad', ''))
            self.txt_estado_empresa.setText(datos.get('estado', ''))
            self.txt_cp_empresa.setText(datos.get('cp', ''))
            self.txt_tel1_empresa.setText(datos.get('telefono1', ''))
            self.txt_tel2_empresa.setText(datos.get('telefono2', ''))
            self.txt_email_empresa.setText(datos.get('email', ''))
            self.txt_web_empresa.setText(datos.get('sitio_web', ''))
            
            # Cargar logo desde bytes
            self.logo_data = datos.get('logo_data')
            if self.logo_data:
                pixmap_circular = self._crear_pixmap_circular(self.logo_data)
                if not pixmap_circular.isNull():
                    self.lbl_logo_preview.setPixmap(pixmap_circular)
                else:
                    self.quitar_logo()
    
    def guardar_empresa(self):
        """Guardar configuración de la empresa"""
        nombre = self.txt_nombre_comercial.text().strip()
        if not nombre:
            self.mostrar_mensaje("Error", "El nombre comercial es obligatorio", QMessageBox.Critical)
            return
        
        rfc = self.txt_rfc_empresa.text().strip().upper()
        if rfc:
            patron_rfc = r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$'
            if not re.match(patron_rfc, rfc):
                self.mostrar_mensaje("Error", "El formato del RFC es inválido", QMessageBox.Critical)
                return
        
        cp = self.txt_cp_empresa.text().strip()
        if cp and not re.match(r'^\d{5}$', cp):
            self.mostrar_mensaje("Error", "El CP debe tener 5 dígitos", QMessageBox.Critical)
            return
        
        tel1 = self.txt_tel1_empresa.text().strip()
        if tel1:
            patron_tel = r'^[\d\s\(\)\-\+]+$'
            if not re.match(patron_tel, tel1) or len(re.sub(r'\D', '', tel1)) < 10:
                self.mostrar_mensaje("Error", "Formato de teléfono 1 inválido", QMessageBox.Critical)
                return
        
        tel2 = self.txt_tel2_empresa.text().strip()
        if tel2:
            patron_tel = r'^[\d\s\(\)\-\+]+$'
            if not re.match(patron_tel, tel2) or len(re.sub(r'\D', '', tel2)) < 10:
                self.mostrar_mensaje("Error", "Formato de teléfono 2 inválido", QMessageBox.Critical)
                return

        email = self.txt_email_empresa.text().strip()
        if email:
            patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(patron_email, email):
                self.mostrar_mensaje("Error", "Formato de email inválido", QMessageBox.Critical)
                return
        
        datos = {
            'nombre_comercial': nombre,
            'razon_social': self.txt_razon_social.text().strip(),
            'rfc': rfc,
            'calle': self.txt_calle_empresa.text().strip(),
            'colonia': self.txt_colonia_empresa.text().strip(),
            'ciudad': self.txt_ciudad_empresa.text().strip(),
            'estado': self.txt_estado_empresa.text().strip(),
            'cp': cp,
            'telefono1': tel1,
            'telefono2': tel2,
            'email': email,
            'sitio_web': self.txt_web_empresa.text().strip(),
            'logo_data': self.logo_data  # Guardamos bytes
        }
        
        # Esta llamada ahora usa api_client (renombrado como db_helper)
        if db_helper.guardar_config_empresa(datos):
            self.mostrar_mensaje("Éxito", "Configuración guardada correctamente", QMessageBox.Information)
        else:
            self.mostrar_mensaje("Error", "No se pudo guardar la configuración", QMessageBox.Critical)
    
    # ==================== TAB USUARIOS ====================
    
    def crear_tab_usuarios(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formulario
        grupo_form = QGroupBox()
        grupo_form.setStyleSheet(GROUP_BOX_STYLE)
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.txt_id_usuario = QLineEdit()
        self.txt_id_usuario.setVisible(False)
        
        lbl_username = QLabel("Usuario *")
        lbl_username.setStyleSheet(LABEL_STYLE)
        self.txt_username = QLineEdit()
        self.txt_username.setStyleSheet(INPUT_STYLE)
        
        lbl_password = QLabel("Contraseña *")
        lbl_password.setStyleSheet(LABEL_STYLE)
        self.txt_password = QLineEdit()
        self.txt_password.setStyleSheet(INPUT_STYLE)
        self.txt_password.setEchoMode(QLineEdit.Password)
        
        lbl_nombre = QLabel("Nombre Completo *")
        lbl_nombre.setStyleSheet(LABEL_STYLE)
        self.txt_nombre_usuario = QLineEdit()
        self.txt_nombre_usuario.setStyleSheet(INPUT_STYLE)
        
        lbl_email = QLabel("Email")
        lbl_email.setStyleSheet(LABEL_STYLE)
        self.txt_email_usuario = QLineEdit()
        self.txt_email_usuario.setStyleSheet(INPUT_STYLE)
        
        lbl_rol = QLabel("Rol *")
        lbl_rol.setStyleSheet(LABEL_STYLE)
        self.cmb_rol = QComboBox()
        self.cmb_rol.setStyleSheet(INPUT_STYLE)
        self.cmb_rol.addItems(["Usuario", "Vendedor", "Mecánico", "Admin"])
        
        lbl_activo = QLabel("Activo")
        lbl_activo.setStyleSheet(LABEL_STYLE)
        self.chk_activo = QCheckBox()
        self.chk_activo.setChecked(True)
        
        grid.addWidget(lbl_username, 0, 0)
        grid.addWidget(self.txt_username, 0, 1)
        grid.addWidget(lbl_password, 0, 2)
        grid.addWidget(self.txt_password, 0, 3)
        grid.addWidget(lbl_nombre, 1, 0)
        grid.addWidget(self.txt_nombre_usuario, 1, 1)
        grid.addWidget(lbl_email, 1, 2)
        grid.addWidget(self.txt_email_usuario, 1, 3)
        grid.addWidget(lbl_rol, 2, 0)
        grid.addWidget(self.cmb_rol, 2, 1)
        grid.addWidget(lbl_activo, 2, 2)
        grid.addWidget(self.chk_activo, 2, 3)
        
        grupo_form.setLayout(grid)
        layout.addWidget(grupo_form)
        
        # Botones
        btns_layout = QHBoxLayout()
        btn_nuevo = QPushButton("Nuevo")
        btn_guardar = QPushButton("Guardar")
        btn_editar = QPushButton("Editar")
        btn_eliminar = QPushButton("Eliminar")
        btn_limpiar = QPushButton("Limpiar")
        
        for btn in [btn_nuevo, btn_guardar, btn_editar, btn_eliminar, btn_limpiar]:
            btn.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            btn.setFixedHeight(60)
            btns_layout.addWidget(btn)
        
        btn_nuevo.clicked.connect(self.nuevo_usuario)
        btn_guardar.clicked.connect(self.guardar_usuario)
        btn_editar.clicked.connect(self.editar_usuario)
        btn_eliminar.clicked.connect(self.eliminar_usuario)
        btn_limpiar.clicked.connect(self.limpiar_form_usuario)
        
        layout.addLayout(btns_layout)
        
        # Tabla
        self.tabla_usuarios = QTableView()
        self.tabla_usuarios.setStyleSheet(TABLE_STYLE)
        self.tabla_usuarios.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_usuarios.doubleClicked.connect(self.editar_usuario)
        
        self.tabla_usuarios_model = QStandardItemModel()
        self.tabla_usuarios_model.setHorizontalHeaderLabels(
            ["ID", "Usuario", "Nombre", "Email", "Rol", "Estado", "Último AccGceso"]
        )
        self.tabla_usuarios.setModel(self.tabla_usuarios_model)
        
        header = self.tabla_usuarios.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_usuarios.setColumnHidden(0, True)
        
        layout.addWidget(self.tabla_usuarios)
        
        tab.setLayout(layout)
        return tab
    
    def cargar_usuarios(self):
        self.tabla_usuarios_model.setRowCount(0)
        # Esta llamada ahora usa api_client (renombrado como db_helper)
        usuarios = db_helper.get_usuarios()
        
        for usuario in usuarios:
            fila = [
                QStandardItem(str(usuario['id'])),
                QStandardItem(usuario['username']),
                QStandardItem(usuario['nombre_completo']),
                QStandardItem(usuario.get('email', '')),
                QStandardItem(usuario['rol']),
                QStandardItem("Activo" if usuario['activo'] else "Inactivo"),
                QStandardItem(usuario.get('ultimo_acceso', ''))
            ]
            
            for item in fila:
                item.setTextAlignment(Qt.AlignCenter)
            
            if not usuario['activo']:
                for item in fila:
                    item.setForeground(Qt.gray)
            
            self.tabla_usuarios_model.appendRow(fila)
    
    def nuevo_usuario(self):
        self.limpiar_form_usuario()
        self.txt_password.setPlaceholderText("Ingrese contraseña")
    
    def guardar_usuario(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        nombre = self.txt_nombre_usuario.text().strip()
        
        if not username or not nombre:
            self.mostrar_mensaje("Error", "Usuario y Nombre son obligatorios", QMessageBox.Critical)
            return
        
        if not self.usuario_en_edicion_id and not password:
            self.mostrar_mensaje("Error", "La contraseña es obligatoria para usuarios nuevos", QMessageBox.Critical)
            return
        
        datos = {
            'username': username,
            'nombre_completo': nombre,
            'email': self.txt_email_usuario.text().strip(),
            'rol': self.cmb_rol.currentText(),
            'activo': self.chk_activo.isChecked()
        }
        
        # Validar candado de admin
        if self.usuario_en_edicion_id:
            # Esta llamada ahora usa api_client
            usuario_original = db_helper.get_usuario(self.usuario_en_edicion_id)
            
            if (usuario_original and
                usuario_original['rol'] == 'Admin' and 
                datos['activo'] is False):
                
                # Esta llamada ahora usa api_client
                usuarios = db_helper.get_usuarios()
                conteo_admins_activos = sum(1 for u in usuarios if u['rol'] == 'Admin' and u['activo'])
                
                if conteo_admins_activos <= 1:
                    self.mostrar_mensaje(
                        "Acción Denegada",
                        "No se puede desactivar al último administrador activo.",
                        QMessageBox.Critical
                    )
                    self.chk_activo.setChecked(True)
                    return
        
        if password:
            datos['password_hash'] = generar_hash_password(password)
        
        if self.usuario_en_edicion_id:
            # Esta llamada ahora usa api_client
            if db_helper.actualizar_usuario(self.usuario_en_edicion_id, datos):
                self.mostrar_mensaje("Éxito", "Usuario actualizado", QMessageBox.Information)
                self.cargar_usuarios()
                self.limpiar_form_usuario()
            else:
                self.mostrar_mensaje("Error", "No se pudo actualizar", QMessageBox.Critical)
        else:
            if password:
                datos['password_hash'] = generar_hash_password(password)
            # Esta llamada ahora usa api_client
            if db_helper.crear_usuario(datos):
                self.mostrar_mensaje("Éxito", "Usuario creado", QMessageBox.Information)
                self.cargar_usuarios()
                self.limpiar_form_usuario()
            else:
                self.mostrar_mensaje("Error", "No se pudo crear (usuario duplicado?)", QMessageBox.Critical)
    
    def editar_usuario(self):
        indice = self.tabla_usuarios.currentIndex()
        if not indice.isValid():
            self.mostrar_mensaje("Advertencia", "Seleccione un usuario", QMessageBox.Warning)
            return
        
        fila = indice.row()
        usuario_id = int(self.tabla_usuarios_model.item(fila, 0).text())
        
        # Esta llamada ahora usa api_client
        usuario = db_helper.get_usuario(usuario_id)
        if usuario:
            self.usuario_en_edicion_id = usuario_id
            self.txt_id_usuario.setText(str(usuario['id']))
            self.txt_username.setText(usuario['username'])
            self.txt_password.clear()
            self.txt_password.setPlaceholderText("Dejar vacío para no cambiar")
            self.txt_nombre_usuario.setText(usuario['nombre_completo'])
            self.txt_email_usuario.setText(usuario.get('email', ''))
            self.cmb_rol.setCurrentText(usuario['rol'])
            self.chk_activo.setChecked(usuario['activo'])
    
    def eliminar_usuario(self):
        indice = self.tabla_usuarios.currentIndex()
        if not indice.isValid():
            self.mostrar_mensaje("Advertencia", "Seleccione un usuario", QMessageBox.Warning)
            return
        
        fila = indice.row()
        usuario_id = int(self.tabla_usuarios_model.item(fila, 0).text())
        username = self.tabla_usuarios_model.item(fila, 1).text()
        rol = self.tabla_usuarios_model.item(fila, 4).text()

        # Validación: Admin activo
        # Esta llamada ahora usa api_client
        admins_activos = db_helper.contar_admins_activos()
            
        if rol == "Admin" and admins_activos <= 1:
            self.mostrar_mensaje(
                "Acción Denegada",
                "No se puede eliminar el único administrador activo del sistema.",
                QMessageBox.Critical
            )
            return

        respuesta = QMessageBox.question(
            self, 
            "Confirmar Eliminación", 
            f"¿Eliminar usuario '{username}' permanentemente?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            # Esta llamada ahora usa api_client
            if db_helper.eliminar_usuario(usuario_id):
                self.mostrar_mensaje("Éxito", "Usuario eliminado", QMessageBox.Information)
                self.cargar_usuarios()
            else:
                self.mostrar_mensaje("Error", "No se pudo eliminar el usuario", QMessageBox.Critical)
    
    def limpiar_form_usuario(self):
        self.usuario_en_edicion_id = None
        self.txt_id_usuario.clear()
        self.txt_username.clear()
        self.txt_password.clear()
        self.txt_nombre_usuario.clear()
        self.txt_email_usuario.clear()
        self.cmb_rol.setCurrentIndex(0)
        self.chk_activo.setChecked(True)
    
    # ==================== TAB RESPALDO ====================
    
    def crear_tab_respaldo(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(70, 70, 70, 70)
        layout.setSpacing(80)
        
        lbl_titulo = QLabel("Sistema de Respaldo de Base de Datos")
        lbl_titulo.setStyleSheet("font-size: 44px; font-weight: bold; color: #333;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        lbl_info = QLabel(
            "Crea respaldos de tu base de datos para proteger tu información.\n"
            "Se recomienda hacer respaldos diarios."
        )
        lbl_info.setStyleSheet("font-size: 32px; color: #666;")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)
        
        layout.addStretch()
        
        btn_crear_respaldo = QPushButton("Crear Respaldo Ahora")
        btn_crear_respaldo.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_crear_respaldo.setFixedHeight(60)
        btn_crear_respaldo.clicked.connect(self.crear_respaldo)
        layout.addWidget(btn_crear_respaldo)
        
        btn_restaurar = QPushButton("Restaurar desde Respaldo")
        btn_restaurar.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_restaurar.setFixedHeight(60)
        btn_restaurar.clicked.connect(self.restaurar_respaldo)
        layout.addWidget(btn_restaurar)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def crear_respaldo(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_origen = os.path.join(self.base_dir, "taller.db")
            
            archivo_destino, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Respaldo",
                f"respaldo_taller_{timestamp}.db",
                "Base de Datos (*.db)"
            )
            
            if archivo_destino:
                if os.path.exists(archivo_origen):
                    shutil.copy2(archivo_origen, archivo_destino)
                    self.mostrar_mensaje(
                        "Éxito",
                        f"Respaldo creado exitosamente en:\n{archivo_destino}",
                        QMessageBox.Information
                    )
                else:
                    self.mostrar_mensaje("Error", f"No se encontró la base de datos en: {archivo_origen}", QMessageBox.Critical)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al crear respaldo: {str(e)}", QMessageBox.Critical)
    
    def restaurar_respaldo(self):
        respuesta = QMessageBox.warning(
            self,
            "⚠️ Advertencia",
            "Esta acción reemplazará TODA la base de datos actual.\n"
            "La aplicación debe reiniciarse después de la restauración.\n"
            "¿Está seguro de continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.No:
            return
        
        try:
            archivo_origen, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar Respaldo",
                "",
                "Base de Datos (*.db)"
            )
            
            if archivo_origen:
                archivo_destino = os.path.join(self.base_dir, "taller.db")
                # Esta llamada ahora usa api_client (renombrado como db_helper)
                db_helper.close()
                shutil.copy2(archivo_origen, archivo_destino)
                
                self.mostrar_mensaje(
                    "Éxito",
                    "Base de datos restaurada exitosamente.\n"
                    "Por favor, REINICIE la aplicación ahora.",
                    QMessageBox.Information
                )
                self.close()
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al restaurar: {str(e)}.\nDebe reiniciar la aplicación.", QMessageBox.Critical)
    
    # ==================== UTILIDADES ====================
    
    def mostrar_mensaje(self, titulo, mensaje, tipo):
        msg = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg.setStyleSheet(MESSAGE_BOX_STYLE)
        msg.exec_()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ConfiguracionWindow()
    window.show()
    sys.exit(app.exec_())