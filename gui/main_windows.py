from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

# Importar la ventana de login
from login_windows import LoginWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WORKSHOPSYS")
        self.setGeometry(100, 100, 800, 600)

        # Crear botones
        self.btn_orden_trabajo = QPushButton("Órdenes de Trabajo")
        self.btn_nota_venta = QPushButton("Notas de Venta")

        layout = QVBoxLayout()
        layout.addWidget(self.btn_orden_trabajo)
        layout.addWidget(self.btn_nota_venta)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication([])

    # Validar si el usuario está autenticado
    """
    login_window = LoginWindow()
    if login_window.exec_() == LoginWindow.Accepted:
        window = MainWindow()
        window.show()
    """
    window = MainWindow()
    window.show()

    app.exec_()
