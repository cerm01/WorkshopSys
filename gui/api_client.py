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
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error {e.response.status_code} POST {endpoint}: {e.response.text}")
            return None
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
    
    def buscar_ordenes(self, **filtros) -> List[Dict]:
        return self._get("/ordenes/buscar", params=filtros) or []
    
    def crear_orden(self, datos: Dict, items: List[Dict]) -> Optional[Dict]:
        datos_completos = datos.copy()
        datos_completos['items'] = items
        result = self._post("/ordenes", datos_completos)
        return result if result else None
    
    def get_orden(self, orden_id: int) -> Optional[Dict]:
        ordenes = self.get_all_ordenes()
        for orden in ordenes:
            if orden['id'] == orden_id:
                return orden
        return None
    
    def actualizar_orden(self, orden_id: int, datos: Dict, items: Optional[List[Dict]] = None) -> Optional[Dict]:
        datos_completos = datos.copy()
        if items is not None:
            datos_completos['items'] = items
            
        return self._put(f"/ordenes/{orden_id}", datos_completos)
    
    def actualizar_orden_campos_simples(self, orden_id: int, datos: Dict) -> Optional[Dict]:
        return self.actualizar_orden(orden_id, datos, items=None)
    
    def cancelar_orden(self, orden_id: int) -> Optional[Dict]:
        return self._post(f"/ordenes/{orden_id}/cancelar", data={})
    
    # ==================== COTIZACIONES ====================
    
    def get_all_cotizaciones(self, estado: str = None) -> List[Dict]:
        params = {"estado": estado} if estado else {}
        return self._get("/cotizaciones", params=params) or []
    
    def buscar_cotizaciones(self, **filtros) -> List[Dict]:
        """Busca cotizaciones usando filtros como 'folio' o 'cliente_id'."""
        # Pasa los filtros como query parameters (ej: ?folio=COT-123)
        return self._get("/cotizaciones/buscar", params=filtros) or []
    
    def crear_cotizacion(self, datos: Dict, items: List[Dict]) -> Optional[Dict]:
        datos['items'] = items
        result = self._post("/cotizaciones", datos)
        return result if result else None
    
    def get_cotizacion(self, cotizacion_id: int) -> Optional[Dict]:
        """Obtiene una cotización específica por su ID."""
        return self._get(f"/cotizaciones/{cotizacion_id}")
    
    def buscar_cotizaciones(self, folio: str) -> List[Dict]:
        """Busca cotizaciones por folio."""
        return self._get(f"/cotizaciones/buscar", params={"folio": folio}) or []

    def actualizar_cotizacion(self, cotizacion_id: int, cotizacion_data: Dict, items: List[Dict], nota_folio: Optional[str] = None) -> Optional[Dict]:
        """Actualiza una cotización existente."""
        datos_completos = cotizacion_data.copy()
        datos_completos['items'] = items
        
        if nota_folio:
            datos_completos['nota_folio'] = nota_folio
        
        # La fecha de vigencia ya viene como string "dd/MM/yyyy" desde cotizaciones_windows
        return self._put(f"/cotizaciones/{cotizacion_id}", datos_completos)
    
    def actualizar_cotizacion(self, cotizacion_id: int, nota_data: Dict, items: List[Dict], nota_folio: Optional[str] = None) -> Optional[Dict]:
        """Actualiza una cotización existente."""
        datos_completos = nota_data.copy()
        datos_completos['items'] = items
        if nota_folio:
            datos_completos['nota_folio'] = nota_folio
        
        # No tiene sentido enviar la fecha de creación en una actualización
        datos_completos.pop('fecha', None) 
        
        return self._put(f"/cotizaciones/{cotizacion_id}", datos_completos)
    
    def cancelar_cotizacion(self, cotizacion_id: int) -> Optional[Dict]:
        """Marca una cotización como 'Cancelada'."""
        # Usamos _post a la nueva ruta. No requiere enviar datos (data={}).
        return self._post(f"/cotizaciones/{cotizacion_id}/cancelar", data={})
    
    # ==================== NOTAS DE VENTA ====================
    
    def get_all_notas_venta(self) -> List[Dict]:
        return self._get("/notas") or []
    
    def crear_nota(self, datos: Dict, items: List[Dict], **kwargs) -> Optional[Dict]:
        datos_completos = datos.copy()
        datos_completos['items'] = items
        datos_completos.update(kwargs)
        
        return self._post("/notas", datos_completos)
    
    def buscar_notas(self, **filtros) -> List[Dict]:
        notas = self.get_all_notas_venta()
        notas_filtradas = notas
        
        if 'folio' in filtros and filtros['folio']:
            folio_buscar = filtros['folio'].lower()
            notas_filtradas = [
                n for n in notas_filtradas 
                if folio_buscar in n.get('folio', '').lower()
            ]
        
        if 'orden_folio' in filtros and filtros['orden_folio']:
            orden_folio_buscar = filtros['orden_folio'].lower()
            notas_filtradas = [
                n for n in notas_filtradas 
                if n.get('orden_folio', '').lower() == orden_folio_buscar
            ]
            
        return notas_filtradas
    
    def get_nota(self, nota_id: int) -> Optional[Dict]:
        """Obtiene una nota de venta específica por su ID."""
        return self._get(f"/notas/{nota_id}")
    
    def registrar_pago(self, nota_id: int, monto: float, fecha_pago: Any, metodo_pago: str, memo: str) -> Optional[Dict]:
        """Registrar un pago a una nota de venta. fecha_pago debe ser un objeto date."""
        datos_pago = {
            "monto": monto,
            "fecha_pago": fecha_pago.isoformat(), # Convertir date a string ISO
            "metodo_pago": metodo_pago,
            "memo": memo
        }
        return self._post(f"/notas/{nota_id}/pagar", datos_pago)

    def eliminar_pago(self, pago_id: int) -> Optional[Dict]:
        """Elimina un pago de nota de venta y devuelve la nota actualizada"""
        return self._delete(f"/pagos/{pago_id}")
    
    def actualizar_nota(self, nota_id: int, nota_data: Dict, items: List[Dict]) -> Optional[Dict]:
        """Actualiza una nota de venta existente."""
        datos_completos = nota_data.copy()
        datos_completos['items'] = items
        # La fecha ya viene como string 'yyyy-MM-dd' desde notas_windows.py
        return self._put(f"/notas/{nota_id}", datos_completos)
    
    def cancelar_nota(self, nota_id: int) -> Optional[Dict]:
        """Marca una nota de venta como 'Cancelada'."""
        # Usamos _post a la nueva ruta. No requiere enviar datos (data={}).
        return self._post(f"/notas/{nota_id}/cancelar", data={})
    
    # ==================== NOTAS DE PROVEEDOR ====================

    def crear_nota_proveedor(self, datos: Dict, items: List[Dict]) -> Optional[Dict]:
        """Crea una nueva nota de proveedor."""
        datos_completos = datos.copy()
        datos_completos['items'] = items
        return self._post("/notas_proveedor", datos_completos)
    
    def actualizar_nota_proveedor(self, nota_id: int, datos: Dict, items: List[Dict]) -> Optional[Dict]:
        """Actualiza una nota de proveedor existente."""
        datos_completos = datos.copy()
        datos_completos['items'] = items
        return self._put(f"/notas_proveedor/{nota_id}", datos_completos)

    def get_all_notas_proveedor(self) -> List[Dict]:
        return self._get("/notas_proveedor") or []

    def get_nota_proveedor(self, nota_id: int) -> Optional[Dict]:
        return self._get(f"/notas_proveedor/{nota_id}")
    
    def buscar_notas_proveedor(self, folio: Optional[str] = None, proveedor_id: Optional[int] = None) -> List[Dict]:
        """Busca notas de proveedor usando filtros (llamada al servidor)."""
        params = {}
        if folio:
            params['folio'] = folio
        if proveedor_id:
            params['proveedor_id'] = proveedor_id
        return self._get("/notas_proveedor/buscar", params=params) or []

    def registrar_pago_proveedor(self, nota_id: int, monto: float, fecha_pago: Any, metodo_pago: str, memo: str) -> Optional[Dict]:
        """Registrar un pago a proveedor. fecha_pago debe ser un objeto date."""
        datos_pago = {
            "monto": monto,
            "fecha_pago": fecha_pago.isoformat(), # Convertir date a string ISO
            "metodo_pago": metodo_pago,
            "memo": memo
        }
        return self._post(f"/notas_proveedor/{nota_id}/pagar", datos_pago)

    def eliminar_pago_proveedor(self, pago_id: int) -> Optional[Dict]:
        """Elimina un pago a proveedor y devuelve la nota actualizada"""
        return self._delete(f"/pagos_proveedor/{pago_id}")
    
    def cancelar_nota_proveedor(self, nota_id: int) -> Optional[Dict]:
        """Marca una nota de proveedor como 'Cancelada'."""
        # Usamos _post a la nueva ruta. No requiere enviar datos (data={}).
        return self._post(f"/notas_proveedor/{nota_id}/cancelar", data={})
    
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
