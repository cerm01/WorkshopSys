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
    
    # Código de reinicio (debe coincidir con gui/main_windows.py)
    RESTART_CODE = 1001
    exit_code = 0

    # Bucle principal para manejar el reinicio de sesión
    while True:
        # 1. Mostrar Login
        login = LoginWindow()
        
        # Si el login NO es aceptado (ej. cerró la ventana), salimos
        if login.exec_() != LoginWindow.Accepted:
            exit_code = 0 # Salida limpia
            break # Salir del bucle while
        
        # 2. Si el login es exitoso, mostrar MainWindow
        main_window = MainWindow(usuario=login.usuario_logueado)
        
        # 3. Ejecutar el bucle de eventos de MainWindow (esto es bloqueante)
        # Esperará a que main_window llame a self.done(codigo)
        exit_code = main_window.exec_()
        
        # 4. Analizar el código de salida
        print(f"DEBUG (main.py): Bucle de aplicación terminado. Código recibido: {exit_code}")
        if exit_code != RESTART_CODE:
            # Si NO es el código de reinicio (ej. se cerró con la 'X'),
            # salimos del bucle while
            break
        
        # Si el código ES RESTART_CODE, el bucle se repite
        # y volverá a mostrar el LoginWindow
    
    # Limpiar WebSocket al cerrar
    ws_client.stop()
    
    sys.exit(exit_code)