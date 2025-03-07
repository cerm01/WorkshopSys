from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WORKSHOPSYS")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(800, 600)
        self.showMaximized()  # Mostrar maximizada

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

        # Crear botones 
        button_Administracion = QPushButton("Administración")
        button_Administracion.

        # Layout para los botones de la fila superior
        top_layout = QHBoxLayout()
        top_layout.addWidget(button_Administracion)

        # Agregar los layouts de arriba y abajo al layout principal
        frame_layout.addLayout(top_layout)

        # Agregar el layout al QFrame
        self.frame.setLayout(frame_layout)

        # Crear un widget central y agregar el frame
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.frame)

        # Establecer márgenes del layout para aumentar el espacio entre el frame y la ventana
        central_layout.setContentsMargins(150, 150, 150, 150)  # Márgenes en el orden: (izquierda, arriba, derecha, abajo)

        # Asignar el layout al widget central
        central_widget.setLayout(central_layout)

        # Establecer el widget central
        self.setCentralWidget(central_widget)

        # Fondo degradado
        self.setStyleSheet("""
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #2CD5C4, stop: 1 #00788E
            );
        """)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()

    app.exec_()
