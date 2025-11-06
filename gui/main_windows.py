import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QToolButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor

from gui.administracion_windows import AdministracionWindow
from gui.clientes_windows import ClientesWindow
from gui.proveedores_windows import ProveedoresWindow
from gui.inventario_windows import InventarioWindow
from gui.reportes_windows import ReportesWindow
from gui.configuracion_windows import ConfiguracionWindow

from gui.utils import recolor_icon

# Importar los estilos desde styles.py
from gui.styles import MAIN_WINDOW_GRADIENT, ROUNDED_FRAME, BUTTON_STYLE_2

class MainWindow(QMainWindow):
    # Definición de las ventanas y sus configuraciones como constante de clase
    WINDOW_CONFIG = {
        "administracion": {
            "class": AdministracionWindow,
            "display_name": "Administración",
            "icon": "assets/icons/administracion.png",
            "size": (200, 200),
            "icon_size": (120, 120),
            "position": "main"  # Propiedad para identificar ubicación
        },
        "clientes": {
            "class": ClientesWindow,
            "display_name": "Clientes",
            "icon": "assets/icons/clientes.png",
            "size": (200, 200),
            "icon_size": (120, 120),
            "position": "main"
        },
        "proveedores": {
            "class": ProveedoresWindow,
            "display_name": "Proveedores",
            "icon": "assets/icons/proveedores.png",
            "size": (200, 200),
            "icon_size": (120, 120),
            "position": "main"
        },
        "inventario": {
            "class": InventarioWindow,
            "display_name": "Inventario",
            "icon": "assets/icons/inventario.png",
            "size": (200, 200),
            "icon_size": (120, 120),
            "position": "main"
        },
        "reportes": {
            "class": ReportesWindow,
            "display_name": "Reportes",
            "icon": "assets/icons/reportes.png",
            "size": (200, 200),
            "icon_size": (120, 120),
            "position": "main"
        },
        "configuracion": {
            "class": ConfiguracionWindow,
            "display_name": "",  # Sin texto, solo icono
            "icon": "assets/icons/configuracion.png",
            "size": (80, 80),
            "icon_size": (50, 50),
            "position": "corner"  # Ubicación especial
        }
    }
    
    # Configuración general de la ventana
    WINDOW_SETTINGS = {
        "title": "WORKSHOPSYS",
        "min_size": (1200, 600),
        "icon_color": "#FFFFFF",
        "margins": (30, 30, 30, 30)
    }
    
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario_actual = usuario
        # Actualizar título con usuario
        titulo = self.WINDOW_SETTINGS["title"]
        if usuario:
            nombre = usuario.get('nombre_completo', 'Usuario')
            rol = usuario.get('rol', '')
            titulo = f"{titulo} - {nombre} ({rol})"
        self.setWindowTitle(titulo)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        # Dimensiones iniciales
        self.setMinimumSize(*self.WINDOW_SETTINGS["min_size"])
        self.showMaximized()  # Mostrar maximizada
        # Fondo degradado - Usamos el estilo importado
        self.setStyleSheet(MAIN_WINDOW_GRADIENT)
        # Inicializar diccionario para las instancias de ventanas
        self.window_instances = {key: None for key in self.WINDOW_CONFIG.keys()}
        # Crear la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Contenedor (frame) con fondo y bordes redondeados - Usamos el estilo importado
        self.frame = QFrame()
        self.frame.setStyleSheet(ROUNDED_FRAME)

        # Crear un layout para posicionar el contenido principal y el botón de configuración
        frame_layout = QVBoxLayout()
        
        # Añadir contenido principal
        frame_layout.addLayout(self.create_main_content_layout())
        
        # Añadir botón de configuración
        frame_layout.addLayout(self.create_config_button_layout())

        # Establecer el layout del frame
        self.frame.setLayout(frame_layout)

        # Crear un widget central y agregar el frame
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.frame)

        # Establecer márgenes del layout
        central_layout.setContentsMargins(*self.WINDOW_SETTINGS["margins"])

        # Asignar el layout al widget central
        central_widget.setLayout(central_layout)

        # Establecer el widget central
        self.setCentralWidget(central_widget)
    
    def create_main_content_layout(self):
        """Crea el layout para los botones principales"""
        layout = QVBoxLayout()
        layout.addStretch(1)  # Espacio superior
        
        # Layout para los botones principales
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)
        
        # Filtrar botones principales
        main_buttons = [k for k, v in self.WINDOW_CONFIG.items() if v["position"] == "main"]
        
        top_layout.addStretch()  # Espaciador inicial
        for identifier in main_buttons:
            config = self.WINDOW_CONFIG[identifier]
            button = self.create_button(config, identifier)
            top_layout.addWidget(button)
            top_layout.addStretch()  # Espaciador entre botones
        
        layout.addLayout(top_layout)
        layout.addStretch(1)  # Espacio inferior
        return layout
    
    def create_config_button_layout(self):
        """Crea el layout para el botón de configuración"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Filtrar botones de esquina
        corner_buttons = [k for k, v in self.WINDOW_CONFIG.items() if v["position"] == "corner"]
        
        layout.addStretch(1)
        for identifier in corner_buttons:
            config = self.WINDOW_CONFIG[identifier]
            button = self.create_button(config, identifier)
            layout.addWidget(button)
        
        return layout
    
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
        button.setIcon(recolor_icon(config["icon"], self.WINDOW_SETTINGS["icon_color"]))
        button.setIconSize(QSize(*config["icon_size"]))
        
        # Solo establecer el estilo si hay texto para mostrar
        if config["display_name"]:
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
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())