import requests
from typing import List, Dict, Optional, Any
import json

class TallerAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _get(self, endpoint: str, params: dict = None):
        """GET request"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error GET {endpoint}: {e}")
            return None
    
    def _post(self, endpoint: str, data: dict):
        """POST request"""
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error POST {endpoint}: {e}")
            return None
    
    def _put(self, endpoint: str, data: dict):
        """PUT request"""
        try:
            response = self.session.put(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error PUT {endpoint}: {e}")
            return None
    
    def _delete(self, endpoint: str):
        """DELETE request"""
        try:
            response = self.session.delete(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error DELETE {endpoint}: {e}")
            return None
    
    # ==================== CLIENTES ====================
    
    def get_clientes(self) -> List[Dict]:
        return self._get("/clientes") or []
    
    def buscar_clientes(self, texto: str) -> List[Dict]:
        return self._get(f"/clientes/buscar/{texto}") or []
    
    def crear_cliente(self, datos: Dict) -> Optional[Dict]:
        return self._post("/clientes", datos)
    
    def actualizar_cliente(self, cliente_id: int, datos: Dict) -> Optional[Dict]:
        return self._put(f"/clientes/{cliente_id}", datos)
    
    def eliminar_cliente(self, cliente_id: int) -> bool:
        result = self._delete(f"/clientes/{cliente_id}")
        return result and result.get('success', False)
    
    # ==================== PROVEEDORES ====================
    
    def get_proveedores(self) -> List[Dict]:
        return self._get("/proveedores") or []
    
    def buscar_proveedores(self, texto: str) -> List[Dict]:
        proveedores = self.get_proveedores()
        texto = texto.lower()
        return [p for p in proveedores if texto in p['nombre'].lower()]
    
    def crear_proveedor(self, datos: Dict) -> Optional[Dict]:
        return self._post("/proveedores", datos)
    
    def actualizar_proveedor(self, proveedor_id: int, datos: Dict) -> Optional[Dict]:
        return self._put(f"/proveedores/{proveedor_id}", datos)
    
    def eliminar_proveedor(self, proveedor_id: int) -> bool:
        result = self._delete(f"/proveedores/{proveedor_id}")
        return result and result.get('success', False)
    
    # ==================== PRODUCTOS ====================
    
    def get_productos(self) -> List[Dict]:
        return self._get("/productos") or []
    
    def buscar_productos(self, texto: str) -> List[Dict]:
        return self._get(f"/productos/buscar/{texto}") or []
    
    def get_productos_bajo_stock(self) -> List[Dict]:
        productos = self.get_productos()
        return [p for p in productos if p['stock_actual'] <= p['stock_min']]
    
    def crear_producto(self, datos: Dict) -> Optional[Dict]:
        return self._post("/productos", datos)
    
    def actualizar_producto(self, producto_id: int, datos: Dict) -> Optional[Dict]:
        return self._put(f"/productos/{producto_id}", datos)
    
    def eliminar_producto(self, producto_id: int) -> bool:
        result = self._delete(f"/productos/{producto_id}")
        return result and result.get('success', False)
    
    # ==================== ORDENES ====================
    
    def get_all_ordenes(self, estado: str = None) -> List[Dict]:
        params = {"estado": estado} if estado else {}
        return self._get("/ordenes", params=params) or []
    
    def crear_orden(self, datos: Dict, items: List[Dict]) -> Optional[int]:
        datos['items'] = items
        result = self._post("/ordenes", datos)
        return result['id'] if result else None
    
    def get_orden(self, orden_id: int) -> Optional[Dict]:
        ordenes = self.get_all_ordenes()
        for orden in ordenes:
            if orden['id'] == orden_id:
                return orden
        return None
    
    def actualizar_orden(self, orden_id: int, datos: Dict) -> bool:
        result = self._put(f"/ordenes/{orden_id}", datos)
        return result is not None
    
    def cancelar_orden(self, orden_id: int) -> bool:
        return self.actualizar_orden(orden_id, {"estado": "Cancelada"})
    
    # ==================== COTIZACIONES ====================
    
    def get_all_cotizaciones(self, estado: str = None) -> List[Dict]:
        params = {"estado": estado} if estado else {}
        return self._get("/cotizaciones", params=params) or []
    
    def crear_cotizacion(self, datos: Dict, items: List[Dict]) -> Optional[int]:
        datos['items'] = items
        result = self._post("/cotizaciones", datos)
        return result['id'] if result else None
    
    def get_cotizacion(self, cotizacion_id: int) -> Optional[Dict]:
        cotizaciones = self.get_all_cotizaciones()
        for cot in cotizaciones:
            if cot['id'] == cotizacion_id:
                return cot
        return None
    
    # ==================== NOTAS DE VENTA ====================
    
    def get_all_notas_venta(self) -> List[Dict]:
        return self._get("/notas") or []
    
    def crear_nota(self, datos: Dict) -> Optional[int]:
        result = self._post("/notas", datos)
        return result['id'] if result else None
    
    def buscar_notas(self, **filtros) -> List[Dict]:
        notas = self.get_all_notas_venta()
        # Filtrado básico
        if 'folio' in filtros and filtros['folio']:
            notas = [n for n in notas if filtros['folio'].lower() in n.get('folio', '').lower()]
        return notas
    
    # ==================== INVENTARIO ====================
    
    def registrar_movimiento_inventario(self, producto_id: int, tipo: str, 
                                       cantidad: int, motivo: str, usuario: str = "Sistema"):
        datos = {
            'producto_id': producto_id,
            'tipo': tipo,
            'cantidad': cantidad,
            'motivo': motivo,
            'usuario': usuario
        }
        return self._post("/inventario/movimiento", datos)
    
    def get_movimientos_inventario(self, producto_id: int = None, 
                                   tipo: str = None, limit: int = 100) -> List[Dict]:
        # Por ahora retorna lista vacía, implementar endpoint en servidor si necesario
        return []
    
    # ==================== MÉTODOS DE COMPATIBILIDAD ====================
    
    def close(self):
        """Cerrar sesión (compatibilidad con db_helper)"""
        self.session.close()
    
    def get_config_empresa(self) -> Optional[Dict]:
        """Configuración empresa (retorna None por ahora)"""
        return None
    
    def guardar_config_empresa(self, datos: Dict) -> bool:
        """Guardar config empresa"""
        return False
    
    def get_usuarios(self) -> List[Dict]:
        """Lista de usuarios"""
        return []
    
    def verificar_credenciales(self, username: str, password: str) -> Optional[Dict]:
        """Verificar login"""
        return None

# Crear instancia global
api_client = TallerAPIClient()
