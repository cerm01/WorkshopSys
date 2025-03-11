import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

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

        # Estilo de los botones
        button_style = """
            QPushButton {
                background: #00788E;
                color: white;
                font-size: 20px;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background: #005F6B;
            }
        """

        # Layout interno del frame
        frame_layout = QVBoxLayout()
        frame_layout.setAlignment(Qt.AlignCenter)

        # Crear botones Inicio -------------------------------------------
        button_Administracion = QPushButton("Administración")
        button_Administracion.setStyleSheet(button_style)
        button_Administracion.setMinimumHeight(50)
        button_Administracion.setMinimumWidth(200)
        button_Administracion.setCursor(Qt.PointingHandCursor)

        button_Administracion.clicked.connect(lambda: self.open_window("administracion"))
        #----------------------------------------------------------------
        button_Clientes = QPushButton("Clientes")
        button_Clientes.setStyleSheet(button_style)
        button_Clientes.setMinimumHeight(50)
        button_Clientes.setMinimumWidth(200)
        button_Clientes.setCursor(Qt.PointingHandCursor)
        button_Clientes.clicked.connect(lambda: self.open_window("clientes"))
        #----------------------------------------------------------------
        button_Proveedores = QPushButton("Proveedores")
        button_Proveedores.setStyleSheet(button_style)
        button_Proveedores.setMinimumHeight(50)
        button_Proveedores.setMinimumWidth(200)
        button_Proveedores.setCursor(Qt.PointingHandCursor)
        button_Proveedores.clicked.connect(lambda: self.open_window("proveedores"))
        #----------------------------------------------------------------
        button_Inventario = QPushButton("Inventario")
        button_Inventario.setStyleSheet(button_style)
        button_Inventario.setMinimumHeight(50)
        button_Inventario.setMinimumWidth(200)
        button_Inventario.setCursor(Qt.PointingHandCursor)
        button_Inventario.clicked.connect(lambda: self.open_window("inventario"))
        #----------------------------------------------------------------
        button_Reportes = QPushButton("Reportes")
        button_Reportes.setStyleSheet(button_style)
        button_Reportes.setMinimumHeight(50)
        button_Reportes.setMinimumWidth(200)
        button_Reportes.setCursor(Qt.PointingHandCursor)
        button_Reportes.clicked.connect(lambda: self.open_window("reportes"))
        
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

        # Agregar el layout de los botones a la ventana
        frame_layout.addLayout(top_layout)

        # Establecer el layout del frame
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
