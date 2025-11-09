import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QHBoxLayout, QApplication, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor

from gui.utils import recolor_icon

from gui.notas_windows import NotasWindow
from gui.cotizaciones_windows import CotizacionesWindow
from gui.ordenes_windows import OrdenesWindow
from gui.notas_proveedores_windows import NotasProveedoresWindow
# Importar los estilos
from gui.styles import WINDOW_GRADIENT, ROUNDED_FRAME, BUTTON_STYLE_2

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
        },
        "notas_proveedores": {
            "class": NotasProveedoresWindow,
            "display_name": "Notas de Proveedores",
            "icon": "assets/icons/proveedores.png",
            "size": (250, 250),
            "icon_size": (120, 120)
        }
    }
        
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario_actual = usuario
        # Corregir rol de "Usuario" a "Capturista" si viene de la BD antigua
        if self.usuario_actual and self.usuario_actual.get('rol') == 'Usuario':
            self.usuario_actual['rol'] = 'Capturista'
            
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
        button_order = ["notas", "cotizaciones", "ordenes",  "notas_proveedores"]
        for identifier in button_order:
            if identifier in self.WINDOW_CONFIG:
                config = self.WINDOW_CONFIG[identifier]
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

    def precalentar_sub_ventanas(self):
        """Crea instancias de las sub-ventanas de admin."""
        try:
            if self.window_instances["notas"] is None:
                self.window_instances["notas"] = NotasWindow(self)
            if self.window_instances["cotizaciones"] is None:
                self.window_instances["cotizaciones"] = CotizacionesWindow(self)
            if self.window_instances["ordenes"] is None:
                self.window_instances["ordenes"] = OrdenesWindow(self)
            if self.window_instances["notas_proveedores"] is None:
                self.window_instances["notas_proveedores"] = NotasProveedoresWindow(self)
        except Exception as e:
            print(f"Error pre-calentando sub-ventanas: {e}")
    
    def create_button(self, config, identifier):
        """
        Método para crear botones con estilo consistente
        
        Args:
            config (dict): Configuración del botón
            identifier (str): Identificador del botón
        """
        # Obtener rol
        rol = self.usuario_actual.get('rol', 'Capturista') if self.usuario_actual else None

        # Definir permisos internos
        permisos = {
            "notas": (["Admin", "Vendedor"], "Gestión de notas de venta"),
            "cotizaciones": (["Admin", "Vendedor"], "Gestión de cotizaciones"),
            "ordenes": (["Admin", "Vendedor", "Mecanico"], "Gestión de órdenes de trabajo"),
            "notas_proveedores": (["Admin", "Vendedor"], "Gestión de notas de proveedor")
        }

        button = QToolButton()
        button.setText(config["display_name"])
        button.setProperty("identifier", identifier)
        button.setStyleSheet(BUTTON_STYLE_2)
        button.setMinimumSize(*config["size"])
        button.setCursor(Qt.PointingHandCursor)
        button.setIcon(recolor_icon(config["icon"], "#FFFFFF"))
        button.setIconSize(QSize(*config["icon_size"]))
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        tiene_permiso = False
        razon = "Rol no reconocido"

        if identifier in permisos:
            roles_permitidos, razon_permiso = permisos[identifier]
            if rol in roles_permitidos:
                tiene_permiso = True
            else:
                razon = f"Acceso restringido.\nSolo para roles: {', '.join(roles_permitidos)}."
        
        if tiene_permiso:
            button.clicked.connect(lambda checked=False, id=identifier: self.open_window(id))
        else:
            button.setEnabled(False)
            button.setToolTip(razon)
            # Aplicar estilo deshabilitado
            button.setStyleSheet(BUTTON_STYLE_2 + """
                QToolButton {
                    background: #999999;
                    color: #CCCCCC;
                }
            """)
        
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
                if window_class is None:
                    print(f"Error: La clase para '{window_id}' no está definida.")
                    return
                self.window_instances[window_id] = window_class(self)
            
            # Mostrar la ventana
            self.window_instances[window_id].exec_()
        else:
            print(f"Error: No se encontró una ventana con el identificador '{window_id}'")