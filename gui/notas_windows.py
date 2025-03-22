import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, 
    QPushButton, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt
# Importar los estilos
from styles import WINDOW_GRADIENT, ROUNDED_FRAME, BUTTON_STYLE_2

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
        
        # Añadir espacio flexible para empujar los botones hacia abajo
        frame_layout.addStretch(1)
        
        # Crear layout para los botones (fila horizontal)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)  # Espacio entre botones
        botones_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes adicionales
        botones_layout.setStretch(0, 1)  # Hacer que se estire horizontalmente
        
        # Usamos el estilo BUTTON_STYLE_2 importado de styles.py
        # Modificamos para usar QPushButton en lugar de QToolButton
        estilo_boton = BUTTON_STYLE_2.replace("QToolButton", "QPushButton")
        
        # Textos de los botones
        textos_botones = ["Nuevo", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir"]
        
        # Crear los botones y añadirlos al layout
        self.botones = []
        for texto in textos_botones:
            boton = QPushButton(texto)
            boton.setStyleSheet(estilo_boton)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Expandir horizontalmente
            botones_layout.addWidget(boton)
            self.botones.append(boton)
        
        # Añadir el layout de botones al layout del frame
        frame_layout.addLayout(botones_layout)
        
        # Establecer el Layout del frame
        self.frame.setLayout(frame_layout)

        # Layout principal del diálogo
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.frame)

        # Establecer márgenes del layout 
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Asignar el layout al diálogo
        self.setLayout(main_layout)
    
    def closeEvent(self, event):
        """Evento que se dispara al cerrar la ventana"""
        event.accept()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotasWindow()
    window.show()
    sys.exit(app.exec_())