import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(800, 600)
        self.showMaximized()  # Mostrar maximizada

        # Layout principal (vertical)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addStretch()  # Espacio superior

        # Layout horizontal para centrar el frame
        center_layout = QHBoxLayout()
        center_layout.addStretch()

        # Contenedor (frame) con fondo y bordes redondeados
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            background: rgba(255, 255, 255, 200);
            border-radius: 10px;
            padding: 20px;
        """)

        # Layout interno del frame
        frame_layout = QVBoxLayout()
        frame_layout.setAlignment(Qt.AlignCenter)
        
        #----------------------------------------------------
        self.label_username = QLabel("USUARIO")
        self.label_username.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold;
            text-align: center;
            background: transparent;
            padding-bottom: 10px;
        """)
        self.label_username.setAlignment(Qt.AlignCenter)
        #----------------------------------------------------
        self.input_username = QLineEdit(self)
        self.input_username.setStyleSheet("""
            font-size: 15px;
            padding: 10px;
            border-radius: 5px;
        """)
        self.input_username.setMaxLength(20)
        #----------------------------------------------------
        self.label_password = QLabel("CONTRASEÑA")
        self.label_password.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold;
            text-align: center;
            background: transparent;
            padding-bottom: 10px;               
        """)
        self.label_password.setAlignment(Qt.AlignCenter)
        #----------------------------------------------------
        self.input_password = QLineEdit(self)
        self.input_password.setStyleSheet("""
            padding: 10px;
            border-radius: 5px;
        """)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setMaxLength(20)
        #----------------------------------------------------
        self.btn_login = QPushButton("INICIAR SESIÓN")
        size_hint = self.btn_login.sizeHint()
        self.btn_login.setFixedSize(size_hint.width() + 120, size_hint.height() + 40)
        self.btn_login.setStyleSheet("""
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #2CD5C4, stop: 1 #00788E
            );
            color: white;
            font-size: 20px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
        """)
        self.btn_login.clicked.connect(self.login)
        #----------------------------------------------------

        frame_layout.addWidget(self.label_username)
        frame_layout.addWidget(self.input_username)
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

        # Fondo degradado
        self.setStyleSheet("""
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #2CD5C4, stop: 1 #00788E
            );
        """)

        # Ajustar el tamaño del frame después de la inicialización
        self.adjustFrameSize()

    def resizeEvent(self, event):
        """ Redimensiona el frame de forma proporcional al tamaño de la ventana. """
        self.adjustFrameSize()
        super().resizeEvent(event)

    def adjustFrameSize(self):
        """ Ajusta el tamaño del frame basado en la ventana. """
        if hasattr(self, 'frame') and self.frame:
            w = self.width() // 3
            h = (self.height() * 2) // 3
            self.frame.setFixedSize(w, h)

    def login(self):
        username = self.input_username.text()
        password = self.input_password.text()

        if username == "admin" and password == "admin":
            self.accept()
        else:
             # Crear una ventana emergente de error
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)  # Icono de error
            error_msg.setWindowTitle("Error")
            error_msg.setText("Usuario o contraseña no son correctos.")
            error_msg.setStandardButtons(QMessageBox.Ok)  # Botón de aceptar
            error_msg.exec_()  # Mostrar la ventana emergente

            self.input_username.clear()
            self.input_password.clear()
            self.input_username.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
