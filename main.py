import sys
from PyQt5.QtWidgets import QApplication, QDialog
from gui.login_windows import LoginWindow
from gui.main_windows import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Mostrar ventana de login
    login = LoginWindow()
    
    if login.exec_() == QDialog.Accepted:
        # Usuario autenticado correctamente
        usuario = login.get_usuario_logueado()
        
        # Crear y mostrar ventana principal
        window = MainWindow(usuario)
        window.show()
        
        sys.exit(app.exec_())
    else:
        # Usuario canceló o cerró el login
        sys.exit(0)