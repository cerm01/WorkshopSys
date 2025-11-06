"""
MAIN.PY - Punto de entrada con sistema distribuido
"""
import sys
from PyQt5.QtWidgets import QApplication
from gui.login_windows import LoginWindow
from gui.main_windows import MainWindow
from gui.websocket_client import init_websocket

# ==================== CONFIGURACIÓN ====================
SERVER_URL = "localhost:8000"  # Cambiar por IP del servidor si está en otra PC

# ==================== INICIAR APLICACIÓN ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Inicializar WebSocket para notificaciones en tiempo real
    print("🔌 Conectando a servidor...")
    ws_client = init_websocket(SERVER_URL)
    
    # Mostrar login o ventana principal
    # Si tienes login:
    # login = LoginWindow()
    # if login.exec_() == LoginWindow.Accepted:
    #     main_window = MainWindow(usuario=login.usuario_logueado)
    #     main_window.show()
    
    # Sin login (temporal):
    main_window = MainWindow()
    main_window.show()
    
    # Ejecutar aplicación
    exit_code = app.exec_()
    
    # Limpiar WebSocket al cerrar
    ws_client.stop()
    
    sys.exit(exit_code)