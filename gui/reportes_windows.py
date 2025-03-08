import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFrame, QWidget
from PyQt5.QtCore import Qt

class ReportesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reportes")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(800, 600)
        self.showMaximized()  # Mostrar maximizada

        # Fondo degradado
        self.setStyleSheet("""
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #2CD5C4, stop: 1 #00788E
            );
        """)

        # Contenedor (frame) con fondo y bordes redondeados
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            background: rgba(245, 245, 245, 200);
            border-radius: 10px;
            padding: 20px;
        """)

        # Layout interno del frame
        frame_layout = QVBoxLayout()
        frame_layout.setAlignment(Qt.AlignCenter)

        # Establecer el Layout del frame
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportesWindow()
    window.show()
    sys.exit(app.exec_())
