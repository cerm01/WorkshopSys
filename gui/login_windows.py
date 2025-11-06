import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
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
        
        # Usuario
        self.label_username = QLabel("USUARIO")
        self.label_username.setStyleSheet("font-size: 20px; font-weight: bold; background: transparent;")
        self.label_username.setAlignment(Qt.AlignCenter)
        
        self.input_username = QLineEdit()
        self.input_username.setStyleSheet("font-size: 15px; padding: 10px; border-radius: 5px;")
        self.input_username.setMaxLength(20)
        self.input_username.setPlaceholderText("Ingrese su usuario")
        
        # Contraseña
        self.label_password = QLabel("CONTRASEÑA")
        self.label_password.setStyleSheet("font-size: 20px; font-weight: bold; background: transparent;")
        self.label_password.setAlignment(Qt.AlignCenter)
        
        self.input_password = QLineEdit()
        self.input_password.setStyleSheet("padding: 10px; border-radius: 5px;")
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
        """)
        self.btn_login.clicked.connect(self.login)
        
        # Agregar widgets
        frame_layout.addWidget(self.label_username)
        frame_layout.addWidget(self.input_username)
        frame_layout.addSpacing(10)
        frame_layout.addWidget(self.label_password)
        frame_layout.addWidget(self.input_password)
        frame_layout.addSpacing(25)
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