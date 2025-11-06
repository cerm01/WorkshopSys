import sys
from PyQt5.QtWidgets import QApplication, QDialog
from gui.login_windows import LoginWindow
from gui.main_windows import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    RESTART_CODE = 1001 
    result = RESTART_CODE
    usuario = None
    
    while result == RESTART_CODE:
        login = LoginWindow()
        
        if login.exec_() == QDialog.Accepted:
            usuario = login.get_usuario_logueado()
            window = MainWindow(usuario)
            result = window.exec_() 
        else:
            result = 0 
    sys.exit(0)