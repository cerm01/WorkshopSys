import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QWidget
from PyQt5.QtCore import Qt
# Importar los estilos
from styles import WINDOW_GRADIENT, ROUNDED_FRAME

class NotasWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Notas")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)  # Mostrar maximizada

        # Aplicar estilos
        self.apply_styles()
        
        # Crear la interfaz
        self.setup_ui()
    
    def apply_styles(self):
        """Método para aplicar los estilos importados del archivo styles.py"""
        self.setStyleSheet(WINDOW_GRADIENT)
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Contenedor (frame) con fondo y bordes redondeados
        self.frame = QFrame()
        self.frame.setStyleSheet(ROUNDED_FRAME)

        # Layout interno del frame
        frame_layout = QVBoxLayout()
        frame_layout.setAlignment(Qt.AlignCenter)

        # Establecer el Layout del frame
        self.frame.setLayout(frame_layout)

        # Layout principal del diálogo
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.frame)

        # Establecer márgenes del layout 
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Asignar el layout al diálogo
        self.setLayout(main_layout)
    
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = NotasWindow()
    window.show()
    sys.exit(app.exec_())