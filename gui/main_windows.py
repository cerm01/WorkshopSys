import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QPushButton, QHBoxLayout, QToolButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor

from administracion_windows import AdministracionWindow
from clientes_windows import ClientesWindow
from proveedores_windows import ProveedoresWindow
from inventario_windows import InventarioWindow
from reportes_windows import ReportesWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WORKSHOPSYS")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(1200, 600)
        self.showMaximized()  # Mostrar maximizada

        # Fondo degradado
        self.setStyleSheet("""
            background: qradialgradient(
            cx: 0.5, cy: 0.5, radius: 0.9,
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

        # Estilo para QToolButton
        button_style = """
            QToolButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2CD5C4, stop: 1 #00788E
                );
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 15px;
                padding: 15px, 10px, 20px, 10px;
            }
            QToolButton::menu-indicator {  /* Oculta el indicador de menú si no se usa */
                image: none;
            }
        """

        def recolor_icon(icon_path, color):
            pixmap = QPixmap(icon_path)  # Cargar la imagen original
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)  # Modo para cambiar el color
            painter.fillRect(pixmap.rect(), QColor(color))  # Aplicar color
            painter.end()
            return QIcon(pixmap)

        # Layout interno del frame
        frame_layout = QVBoxLayout()
        frame_layout.setAlignment(Qt.AlignCenter)

        # Crear botones Inicio -------------------------------------------
        button_Administracion = QToolButton()  # Usamos QToolButton en lugar de QPushButton
        button_Administracion.setText("Administración")
        button_Administracion.setStyleSheet(button_style)
        button_Administracion.setMinimumHeight(200)  # Ajustar tamaño para acomodar el icono y texto
        button_Administracion.setMinimumWidth(200)
        button_Administracion.setCursor(Qt.PointingHandCursor)
        icon_path = "assets/icons/administracion.png"
        button_Administracion.setIcon(recolor_icon(icon_path, "#FFFFFF"))  # Cambiar color del icono
        button_Administracion.setIconSize(QSize(120,120))  # Ajusta el tamaño del icono
        button_Administracion.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # Texto debajo del icono
        button_Administracion.clicked.connect(lambda: self.open_window("administracion"))
        #----------------------------------------------------------------
        button_Clientes = QToolButton()
        button_Clientes.setText("Clientes")
        button_Clientes.setStyleSheet(button_style)
        button_Clientes.setMinimumHeight(200)
        button_Clientes.setMinimumWidth(200)
        button_Clientes.setCursor(Qt.PointingHandCursor)
        icon_path = "assets/icons/clientes.png"
        button_Clientes.setIcon(recolor_icon(icon_path, "#FFFFFF"))
        button_Clientes.setIconSize(QSize(120,120))
        button_Clientes.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button_Clientes.clicked.connect(lambda: self.open_window("clientes"))
        #----------------------------------------------------------------
        button_Proveedores = QToolButton()
        button_Proveedores.setText("Proveedores")
        button_Proveedores.setStyleSheet(button_style)
        button_Proveedores.setMinimumHeight(200)
        button_Proveedores.setMinimumWidth(200)
        button_Proveedores.setCursor(Qt.PointingHandCursor)
        icon_path = "assets/icons/proveedores.png"
        button_Proveedores.setIcon(recolor_icon(icon_path, "#FFFFFF"))
        button_Proveedores.setIconSize(QSize(120,120))
        button_Proveedores.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button_Proveedores.clicked.connect(lambda: self.open_window("proveedores"))
        #----------------------------------------------------------------
        button_Inventario = QToolButton()
        button_Inventario.setText("Inventario")
        button_Inventario.setStyleSheet(button_style)
        button_Inventario.setMinimumHeight(200)
        button_Inventario.setMinimumWidth(200)
        button_Inventario.setCursor(Qt.PointingHandCursor)
        icon_path = "assets/icons/inventario.png"
        button_Inventario.setIcon(recolor_icon(icon_path, "#FFFFFF"))
        button_Inventario.setIconSize(QSize(120,120))
        button_Inventario.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button_Inventario.clicked.connect(lambda: self.open_window("inventario"))
        #----------------------------------------------------------------
        button_Reportes = QToolButton()
        button_Reportes.setText("Reportes")
        button_Reportes.setStyleSheet(button_style)
        button_Reportes.setMinimumHeight(200)
        button_Reportes.setMinimumWidth(200)
        button_Reportes.setCursor(Qt.PointingHandCursor)
        icon_path = "assets/icons/reportes.png"
        button_Reportes.setIcon(recolor_icon(icon_path, "#FFFFFF"))
        button_Reportes.setIconSize(QSize(120,120))
        button_Reportes.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button_Reportes.clicked.connect(lambda: self.open_window("reportes"))
        #----------------------------------------------------------------
        button_Configuracion = QToolButton()
        button_Configuracion.setStyleSheet(button_style)
        button_Configuracion.setMinimumHeight(80)
        button_Configuracion.setMinimumWidth(80)
        button_Configuracion.setCursor(Qt.PointingHandCursor)
        icon_path = "assets/icons/configuracion.png"
        button_Configuracion.setIcon(recolor_icon(icon_path, "#FFFFFF"))
        button_Configuracion.setIconSize(QSize(50,50))
        button_Configuracion.clicked.connect(lambda: self.open_window("configuracion"))
        
        
        # Layout para los botones de la fila superior 
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Espaciador antes del primer botón
        top_layout.addWidget(button_Administracion)
        top_layout.addStretch()  # Espaciador entre los botones
        top_layout.addWidget(button_Clientes)
        top_layout.addStretch()  # Espaciador entre los botones
        top_layout.addWidget(button_Proveedores)
        top_layout.addStretch()  # Espaciador entre los botones
        top_layout.addWidget(button_Inventario)
        top_layout.addStretch()  # Espaciador entre los botones
        top_layout.addWidget(button_Reportes)
        top_layout.addStretch()  # Espaciador después del último botón
        top_layout.setAlignment(Qt.AlignCenter)

        config_layout = QHBoxLayout()
        config_layout.addStretch(1)
        config_layout.addWidget(button_Configuracion)
        config_layout.setContentsMargins(5, 5, 5, 5)  # Añade margen a la derecha e inferior
        
        # Crear un layout vertical principal para el frame
        main_content_layout = QVBoxLayout()
        main_content_layout.addStretch(1)  # Espacio superior
        main_content_layout.addLayout(top_layout)  # Botones principales
        main_content_layout.addStretch(1)  # Espacio inferior
        
        # Crear un layout para posicionar el contenido principal y el botón de configuración
        frame_layout = QVBoxLayout()
        frame_layout.addLayout(main_content_layout)  # Contenido principal (centrado)
        frame_layout.addLayout(config_layout)  # Botón de configuración (abajo a la derecha)

        # Establecer el layout del frame
        self.frame.setLayout(frame_layout)

        # Crear un widget central y agregar el frame
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.frame)

        # Establecer márgenes del layout para aumentar el espacio entre el frame y la ventana
        central_layout.setContentsMargins(30, 30, 30, 30)  # Márgenes en el orden: (izquierda, arriba, derecha, abajo)

        # Asignar el layout al widget central
        central_widget.setLayout(central_layout)

        # Establecer el widget central
        self.setCentralWidget(central_widget)

        # Almacenar referencias a ventanas secundarias
        self.windows = {
            "administracion": None,
            "clientes": None,
            "proveedores": None,
            "inventario": None,
            "reportes": None,
        }

    
    def open_window(self, window_name):
        
        if window_name == "administracion":
            self.windows[window_name] = AdministracionWindow(self)
            self.windows[window_name].exec_()
        elif window_name == "clientes":
            self.windows[window_name] = ClientesWindow(self)
            self.windows[window_name].exec_()
        elif window_name == "proveedores":
            self.windows[window_name] = ProveedoresWindow(self)
            self.windows[window_name].exec_()
        elif window_name == "inventario":
            self.windows[window_name] = InventarioWindow(self)
            self.windows[window_name].exec_()
        elif window_name == "reportes":
            self.windows[window_name] = ReportesWindow(self)
            self.windows[window_name].exec_()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
