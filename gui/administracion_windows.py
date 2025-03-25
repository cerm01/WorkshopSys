import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor

from utils import recolor_icon

from notas_windows import NotasWindow
from cotizaciones_windows import CotizacionesWindow
from ordenes_windows import OrdenesWindow
# Importar los estilos
from styles import WINDOW_GRADIENT, ROUNDED_FRAME, BUTTON_STYLE_2

class AdministracionWindow(QDialog):
    # Definición de las ventanas y sus configuraciones como constante de clase
    WINDOW_CONFIG = {
        "notas": {
            "class": NotasWindow,
            "display_name": "Notas",
            "icon": "assets/icons/notas.png",
            "size": (250, 250),
            "icon_size": (120, 120)
        },
        "cotizaciones": {
            "class": CotizacionesWindow,
            "display_name": "Cotizaciones",
            "icon": "assets/icons/cotizaciones.png",
            "size": (250, 250),
            "icon_size": (120, 120)
        },
        "ordenes": {
            "class": OrdenesWindow,
            "display_name": "Órdenes de Trabajo",
            "icon": "assets/icons/ordenes.png",
            "size": (250, 250),
            "icon_size": (120, 120)
        }
    }
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administración")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)  # Mostrar maximizada

        # Inicializar diccionario para las instancias de ventanas
        self.window_instances = {key: None for key in self.WINDOW_CONFIG.keys()}
        
        # Aplicar estilos
        self.setStyleSheet(WINDOW_GRADIENT)
        
        # Crear la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Contenedor (frame) con fondo y bordes redondeados
        self.frame = QFrame()
        self.frame.setStyleSheet(ROUNDED_FRAME)

        # Layout para los botones 
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Crear los botones dinámicamente basados en la configuración
        for identifier, config in self.WINDOW_CONFIG.items():
            button = self.create_button(
                config=config,
                identifier=identifier
            )
            buttons_layout.addWidget(button)
            buttons_layout.addStretch()
        
        # Layout interno del frame
        frame_layout = QVBoxLayout()
        frame_layout.setAlignment(Qt.AlignCenter)
        frame_layout.addLayout(buttons_layout)
        
        # Establecer el Layout del frame
        self.frame.setLayout(frame_layout)

        # Layout principal del diálogo con márgenes
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.addWidget(self.frame)

        # Asignar el layout al diálogo
        self.setLayout(main_layout)
    
    def create_button(self, config, identifier):
        """
        Método para crear botones con estilo consistente
        
        Args:
            config (dict): Configuración del botón
            identifier (str): Identificador del botón
        """
        button = QToolButton()
        button.setText(config["display_name"])
        button.setProperty("identifier", identifier)
        button.setStyleSheet(BUTTON_STYLE_2)
        button.setMinimumSize(*config["size"])
        button.setCursor(Qt.PointingHandCursor)
        button.setIcon(recolor_icon(config["icon"], "#FFFFFF"))
        button.setIconSize(QSize(*config["icon_size"]))
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.clicked.connect(lambda checked=False, id=identifier: self.open_window(id))
        return button
    
    def open_window(self, window_id):
        """
        Abre la ventana correspondiente al identificador
        
        Args:
            window_id (str): Identificador de la ventana a abrir
        """
        if window_id in self.WINDOW_CONFIG:
            # Crear nueva instancia si no existe
            if self.window_instances[window_id] is None:
                window_class = self.WINDOW_CONFIG[window_id]["class"]
                self.window_instances[window_id] = window_class(self)
            
            # Mostrar la ventana
            self.window_instances[window_id].exec_()
        else:
            print(f"Error: No se encontró una ventana con el identificador '{window_id}'")