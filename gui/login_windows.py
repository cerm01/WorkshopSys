import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPainterPath, QFont, QFontMetrics
from gui.db_helper import DatabaseHelper

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.db_helper = DatabaseHelper()
        self.usuario_logueado = None
        
        self.setWindowTitle("Iniciar Sesión")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setMinimumSize(800, 600)
        self.showMaximized()
        
        self._setup_ui()
    
    def _crear_pixmap_circular(self, logo_bytes, tamanio=180):
        """Crear pixmap circular desde bytes"""
        if not logo_bytes:
            return QPixmap()
        
        qimage = QImage()
        qimage.loadFromData(logo_bytes)
        pixmap_original = QPixmap.fromImage(qimage)
        
        if pixmap_original.isNull():
            return QPixmap()
        
        pixmap_escalado = pixmap_original.scaled(
            tamanio - 20, tamanio - 20, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        pixmap_redondo = QPixmap(tamanio, tamanio)
        pixmap_redondo.fill(Qt.transparent)
        
        painter = QPainter(pixmap_redondo)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        path = QPainterPath()
        path.addEllipse(0, 0, tamanio, tamanio)
        painter.fillPath(path, Qt.white)
        painter.setClipPath(path)
        
        x = (tamanio - pixmap_escalado.width()) / 2
        y = (tamanio - pixmap_escalado.height()) / 2
        painter.drawPixmap(int(x), int(y), pixmap_escalado)
        painter.end()
        
        return pixmap_redondo
    
    def _cargar_logo_empresa(self):
        """Cargar logo desde la base de datos"""
        config = self.db_helper.get_config_empresa()
        
        if config and config.get('logo_data'):
            return self._crear_pixmap_circular(config['logo_data'], 180)
        
        return QPixmap()
    
    def _ajustar_texto_nombre(self, texto, ancho_maximo=450):
        """Ajustar nombre: divide en líneas o reduce fuente si es muy largo"""
        palabras = texto.split()
        
        # Probar con fuente normal (28px)
        font = QFont("Arial", 28, QFont.Bold)
        metrics = QFontMetrics(font)
        
        # Si cabe en una línea
        if metrics.horizontalAdvance(texto) <= ancho_maximo:
            return texto, 28
        
        # Intentar dividir en 2 líneas balanceadas
        if len(palabras) > 1:
            # Buscar punto medio
            mitad = len(palabras) // 2
            linea1 = " ".join(palabras[:mitad])
            linea2 = " ".join(palabras[mitad:])
            
            # Verificar que ambas líneas quepan
            if (metrics.horizontalAdvance(linea1) <= ancho_maximo and 
                metrics.horizontalAdvance(linea2) <= ancho_maximo):
                return f"{linea1}\n{linea2}", 28
        
        # Si no cabe dividido, reducir fuente
        for size in [24, 20, 18, 16]:
            font = QFont("Arial", size, QFont.Bold)
            metrics = QFontMetrics(font)
            
            # Intentar en una línea
            if metrics.horizontalAdvance(texto) <= ancho_maximo:
                return texto, size
            
            # Intentar dividido
            if len(palabras) > 1:
                mitad = len(palabras) // 2
                linea1 = " ".join(palabras[:mitad])
                linea2 = " ".join(palabras[mitad:])
                
                if (metrics.horizontalAdvance(linea1) <= ancho_maximo and 
                    metrics.horizontalAdvance(linea2) <= ancho_maximo):
                    return f"{linea1}\n{linea2}", size
        
        # Último recurso: forzar división con fuente pequeña
        mitad = len(palabras) // 2
        linea1 = " ".join(palabras[:mitad])
        linea2 = " ".join(palabras[mitad:])
        return f"{linea1}\n{linea2}", 14
    
    def _setup_ui(self):
        """Configurar interfaz"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addStretch()
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        
        # Frame contenedor
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 200);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        frame_layout = QVBoxLayout()
        frame_layout.setAlignment(Qt.AlignCenter)
        frame_layout.setSpacing(5)
        
        # Nombre comercial con ajuste automático
        config = self.db_helper.get_config_empresa()
        nombre_empresa = config.get('nombre_comercial', 'WORKSHOPSYS') if config else 'WORKSHOPSYS'
        
        # Ajustar texto y tamaño de fuente
        texto_ajustado, font_size = self._ajustar_texto_nombre(nombre_empresa)
        
        self.label_nombre_empresa = QLabel(texto_ajustado)
        self.label_nombre_empresa.setStyleSheet(f"""
            font-size: {font_size}px; 
            font-weight: bold;
            color: black;
            background: transparent;
        """)
        self.label_nombre_empresa.setAlignment(Qt.AlignCenter)
        self.label_nombre_empresa.setWordWrap(True)
        frame_layout.addWidget(self.label_nombre_empresa)
        
        frame_layout.addSpacing(5)
        
        # Logo de la empresa
        self.label_logo = QLabel()
        logo_pixmap = self._cargar_logo_empresa()
        
        if not logo_pixmap.isNull():
            self.label_logo.setPixmap(logo_pixmap)
            self.label_logo.setFixedSize(180, 180)
        else:
            self.label_logo.setText("SIN\nLOGO")
            self.label_logo.setFixedSize(180, 180)
            self.label_logo.setStyleSheet("""
                QLabel {
                    background: white;
                    border: 3px solid #2CD5C4;
                    border-radius: 90px;
                    color: #00788E;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
        
        self.label_logo.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(self.label_logo, alignment=Qt.AlignCenter)
        
        frame_layout.addSpacing(10)
        
        # Usuario
        self.label_username = QLabel("USUARIO")
        self.label_username.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold;
            color: #00788E;
            background: transparent;
        """)
        self.label_username.setAlignment(Qt.AlignCenter)
        
        self.input_username = QLineEdit()
        self.input_username.setStyleSheet("""
            QLineEdit {
                font-size: 15px; 
                padding: 10px; 
                border-radius: 5px;
                background-color: white;
                border: 2px solid #2CD5C4;
            }
            QLineEdit:focus {
                border: 2px solid #00788E;
            }
        """)
        self.input_username.setMaxLength(20)
        self.input_username.setPlaceholderText("Ingrese su usuario")
        
        # Contraseña
        self.label_password = QLabel("CONTRASEÑA")
        self.label_password.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold;
            color: #00788E;
            background: transparent;
        """)
        self.label_password.setAlignment(Qt.AlignCenter)
        
        self.input_password = QLineEdit()
        self.input_password.setStyleSheet("""
            QLineEdit {
                font-size: 15px;
                padding: 10px; 
                border-radius: 5px;
                background-color: white;
                border: 2px solid #2CD5C4;
            }
            QLineEdit:focus {
                border: 2px solid #00788E;
            }
        """)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setMaxLength(20)
        self.input_password.setPlaceholderText("Ingrese su contraseña")
        self.input_password.returnPressed.connect(self.login)
        
        # Botón
        self.btn_login = QPushButton("INICIAR SESIÓN")
        size_hint = self.btn_login.sizeHint()
        self.btn_login.setFixedSize(size_hint.width() + 120, size_hint.height() + 40)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #2CD5C4, stop:1 #00788E);
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #00788E, stop:1 #2CD5C4);
            }
            QPushButton:pressed {
                background: #00788E;
            }
        """)
        self.btn_login.clicked.connect(self.login)
        
        # Agregar widgets
        frame_layout.addWidget(self.label_username)
        frame_layout.addWidget(self.input_username)
        frame_layout.addSpacing(5)
        frame_layout.addWidget(self.label_password)
        frame_layout.addWidget(self.input_password)
        frame_layout.addSpacing(15)
        frame_layout.addWidget(self.btn_login, alignment=Qt.AlignCenter)
        
        self.frame.setLayout(frame_layout)
        center_layout.addWidget(self.frame)
        center_layout.addStretch()
        
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2CD5C4, stop:1 #00788E);")
        
        self.adjustFrameSize()
    
    def resizeEvent(self, event):
        """Ajustar frame al redimensionar"""
        self.adjustFrameSize()
        super().resizeEvent(event)
    
    def adjustFrameSize(self):
        """Ajustar tamaño del frame"""
        if hasattr(self, 'frame'):
            w = self.width() // 3
            h = (self.height() * 2) // 3
            self.frame.setFixedSize(w, h)
    
    def login(self):
        """Validar credenciales"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        
        if not username or not password:
            self._mostrar_error("Por favor ingrese usuario y contraseña")
            return
        
        # Validar contra BD
        usuario = self.db_helper.validar_login(username, password)
        
        if usuario:
            self.usuario_logueado = usuario
            self.accept()
        else:
            self._mostrar_error("Usuario o contraseña incorrectos")
            self.input_password.clear()
            self.input_password.setFocus()
    
    def _mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error de Autenticación", mensaje)
    
    def get_usuario_logueado(self):
        """Obtener datos del usuario autenticado"""
        return self.usuario_logueado

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    if window.exec_() == QDialog.Accepted:
        usuario = window.get_usuario_logueado()
        print(f"Usuario autenticado: {usuario['nombre_completo']} - Rol: {usuario['rol']}")
    sys.exit()