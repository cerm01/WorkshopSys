import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QToolButton, QDialog
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
class MainWindow(QDialog):

    # Definición de las ventanas y sus configuraciones como constante de clase
    WINDOW_CONFIG = {
        "administracion": {
            "class": AdministracionWindow,
            "display_name": "Administración",
            "icon": "assets/icons/administracion.png",
            "size": (200, 200),
            "icon_size": (120, 120),
            "position": "main"
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
            "position": "bottom_corner"
        },
        "cerrar": {
            "class": None,  # Clase None para acción especial (cerrar)
            "display_name": "",
            "icon": "assets/icons/cerrar.png", # El icono que mencionaste
            "size": (80, 80),
            "icon_size": (50, 50),
            "position": "top_corner"
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
        self.showMaximized()
        # Fondo degradado
        self.setStyleSheet(MAIN_WINDOW_GRADIENT.replace("QMainWindow", "QDialog"))
        
        # Inicializar diccionario para las instancias de ventanas
        self.window_instances = {key: None for key in self.WINDOW_CONFIG.keys()}
        # Crear la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Contenedor (frame) con fondo y bordes redondeados
        self.frame = QFrame()
        self.frame.setStyleSheet(ROUNDED_FRAME)

        # Crear un layout para posicionar el contenido
        frame_layout = QVBoxLayout()
        
        # Añadir botón de cerrar (esquina superior)
        frame_layout.addLayout(self.create_top_corner_button_layout())

        # Añadir contenido principal
        frame_layout.addLayout(self.create_main_content_layout())
        
        # Añadir botón de configuración (esquina inferior)
        frame_layout.addLayout(self.create_bottom_corner_button_layout())

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
        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.addWidget(central_widget)
        self.setLayout(main_dialog_layout)
    
    def create_main_content_layout(self):
        """Crea el layout para los botones principales"""
        layout = QVBoxLayout()
        layout.addStretch(1)
        
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)
        
        main_buttons = [k for k, v in self.WINDOW_CONFIG.items() if v["position"] == "main"]
        
        top_layout.addStretch()
        for identifier in main_buttons:
            config = self.WINDOW_CONFIG[identifier]
            button = self.create_button(config, identifier)
            top_layout.addWidget(button)
            top_layout.addStretch()
        
        layout.addLayout(top_layout)
        layout.addStretch(1)
        return layout
    
    def create_top_corner_button_layout(self):
        """Crea el layout para el botón de la esquina superior (cerrar)"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        corner_buttons = [k for k, v in self.WINDOW_CONFIG.items() if v["position"] == "top_corner"]
        
        layout.addStretch(1)
        for identifier in corner_buttons:
            config = self.WINDOW_CONFIG[identifier]
            button = self.create_button(config, identifier)
            layout.addWidget(button)
        
        return layout

    def create_bottom_corner_button_layout(self):
        """Crea el layout para el botón de la esquina inferior (config)"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        corner_buttons = [k for k, v in self.WINDOW_CONFIG.items() if v["position"] == "bottom_corner"]
        
        layout.addStretch(1)
        for identifier in corner_buttons:
            config = self.WINDOW_CONFIG[identifier]
            button = self.create_button(config, identifier)
            layout.addWidget(button)
        
        return layout

    def logout(self):
        """Cierra la ventana principal y emite un código de reinicio."""
        # Código de resultado personalizado para "Cerrar Sesión"
        RESTART_CODE = 1001
        self.done(RESTART_CODE)

    def create_button(self, config, identifier):
        """
        Método para crear botones con estilo consistente
        """
        button = QToolButton()
        button.setText(config["display_name"])
        button.setProperty("identifier", identifier)
        button.setStyleSheet(BUTTON_STYLE_2)
        button.setMinimumSize(*config["size"])
        button.setCursor(Qt.PointingHandCursor)
        button.setIcon(recolor_icon(config["icon"], self.WINDOW_SETTINGS["icon_color"]))
        button.setIconSize(QSize(*config["icon_size"]))
        
        if config["display_name"]:
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        if config["class"] is None:
            if identifier == "cerrar":
                button.clicked.connect(self.logout) # Conectar a self.logout
            # else:
                # button.clicked.connect(self.close) # Acción por defecto si no es 'cerrar'
        else:
            # Acción normal: abrir ventana
            button.clicked.connect(lambda checked=False, id=identifier: self.open_window(id))
        
        return button
    
    def open_window(self, window_id):
        """
        Abre la ventana correspondiente al identificador
        """
        if window_id in self.WINDOW_CONFIG:
            window_class = self.WINDOW_CONFIG[window_id]["class"]
            if window_class is None:
                print(f"Acción '{window_id}' no abre una ventana.")
                return

            if self.window_instances[window_id] is None:
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