from PyQt5.QtCore import QThread, pyqtSignal
import websocket
import json
import time

class WebSocketClient(QThread):
    # Señales para diferentes eventos
    cliente_creado = pyqtSignal(dict)
    cliente_actualizado = pyqtSignal(dict)
    cliente_eliminado = pyqtSignal(dict)
    
    proveedor_creado = pyqtSignal(dict)
    proveedor_actualizado = pyqtSignal(dict)
    proveedor_eliminado = pyqtSignal(dict)
    
    producto_creado = pyqtSignal(dict)
    producto_actualizado = pyqtSignal(dict)
    stock_actualizado = pyqtSignal(dict)
    
    orden_creada = pyqtSignal(dict)
    orden_actualizada = pyqtSignal(dict)
    
    cotizacion_creada = pyqtSignal(dict)
    cotizacion_actualizada = pyqtSignal(dict)
    
    nota_creada = pyqtSignal(dict)
    nota_actualizada = pyqtSignal(dict)
    
    nota_proveedor_creada = pyqtSignal(dict)
    nota_proveedor_actualizada = pyqtSignal(dict)

    usuario_creado = pyqtSignal(dict)
    usuario_actualizado = pyqtSignal(dict)
    usuario_eliminado = pyqtSignal(dict)
    config_actualizada = pyqtSignal(dict)

    connection_status = pyqtSignal(bool)  # True=conectado, False=desconectado
    
    def __init__(self, server_url: str = "localhost:8000"):
        super().__init__()
        self.server_url = server_url
        self.ws = None
        self.running = True
        self.connected = False
    
    def run(self):
        """Thread principal del WebSocket"""
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    f"ws://{self.server_url}/ws",
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open
                )
                
                # Correr WebSocket (bloquea hasta cerrar conexión)
                self.ws.run_forever()
                
            except Exception as e:
                print(f"WebSocket error: {e}")
                self.connected = False
                self.connection_status.emit(False)
            
            # Reintentar conexión cada 5 segundos
            if self.running:
                time.sleep(5)
    
    def on_open(self, ws):
        """Conexión establecida"""
        print("✅ WebSocket conectado")
        self.connected = True
        self.connection_status.emit(True)
    
    def on_message(self, ws, message):
        """Mensaje recibido del servidor"""
        try:
            data = json.loads(message)
            event_type = data.get('type')
            event_data = data.get('data', {})
            
            # Emitir señal según tipo de evento
            if event_type == 'cliente_creado':
                self.cliente_creado.emit(event_data)
            elif event_type == 'cliente_actualizado':
                self.cliente_actualizado.emit(event_data)
            elif event_type == 'cliente_eliminado':
                self.cliente_eliminado.emit(event_data)
            elif event_type == 'proveedor_creado':
                self.proveedor_creado.emit(event_data)
            elif event_type == 'proveedor_actualizado':
                self.proveedor_actualizado.emit(event_data)
            elif event_type == 'proveedor_eliminado':
                self.proveedor_eliminado.emit(event_data)   
            elif event_type == 'producto_creado':
                self.producto_creado.emit(event_data)
            elif event_type == 'producto_actualizado':
                self.producto_actualizado.emit(event_data)
            elif event_type == 'stock_actualizado':
                self.stock_actualizado.emit(event_data)
            elif event_type == 'orden_creada':
                self.orden_creada.emit(event_data)
            elif event_type == 'orden_actualizada':
                self.orden_actualizada.emit(event_data)
            elif event_type == 'cotizacion_creada':
                self.cotizacion_creada.emit(event_data)
            elif event_type == 'cotizacion_actualizada':
                self.cotizacion_actualizada.emit(event_data)    
            elif event_type == 'nota_creada':
                self.nota_creada.emit(event_data)
            elif event_type == 'nota_actualizada':
                self.nota_actualizada.emit(event_data)
            elif event_type == 'nota_proveedor_creada':
                self.nota_proveedor_creada.emit(event_data)
            elif event_type == 'nota_proveedor_actualizada':
                self.nota_proveedor_actualizada.emit(event_data)
            elif event_type == 'usuario_creado':
                self.usuario_creado.emit(event_data)
            elif event_type == 'usuario_actualizado':
                self.usuario_actualizado.emit(event_data)
            elif event_type == 'usuario_eliminado':
                self.usuario_eliminado.emit(event_data)
            elif event_type == 'config_actualizada':
                self.config_actualizada.emit(event_data)
                
        except Exception as e:
            print(f"Error procesando mensaje: {e}")
    
    def on_error(self, ws, error):
        """Error en WebSocket"""
        print(f"❌ WebSocket error: {error}")
        self.connected = False
        self.connection_status.emit(False)
    
    def on_close(self, ws, close_status_code, close_msg):
        """Conexión cerrada"""
        print("🔌 WebSocket desconectado")
        self.connected = False
        self.connection_status.emit(False)
    
    def stop(self):
        """Detener thread"""
        self.running = False
        if self.ws:
            self.ws.close()
        self.quit()
        self.wait()

# Instancia global (se inicializa en main)
ws_client = None

def init_websocket(server_url: str = "localhost:8000"):
    """Inicializar WebSocket global"""
    global ws_client
    if ws_client is None:
        ws_client = WebSocketClient(server_url)
        ws_client.start()
    return ws_client