import requests
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
import base64 # Requerido para manejar el logo

class TallerAPIClient:
    def __init__(self, base_url: str = "https://web-production-96c8.up.railway.app"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _get(self, endpoint: str, params: dict = None):
        """GET request"""
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error GET {endpoint}: {e}")
            return None
    
    def _post(self, endpoint: str, data: dict):
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=data, timeout=10)
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
            response = self.session.put(f"{self.base_url}{endpoint}", json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error PUT {endpoint}: {e}")
            return None
    
    def _delete(self, endpoint: str):
        """DELETE request"""
        try:
            response = self.session.delete(f"{self.base_url}{endpoint}", timeout=10)
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
        return self._get(f"/proveedores/buscar/{texto}") or []
    
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
        return self._get("/reportes/inventario_bajo") or []
    
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
        return self._get(f"/ordenes/{orden_id}")
    
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
        return self._get("/cotizaciones/buscar", params=filtros) or []
    
    def crear_cotizacion(self, datos: Dict, items: List[Dict]) -> Optional[Dict]:
        datos['items'] = items
        result = self._post("/cotizaciones", datos)
        return result if result else None
    
    def get_cotizacion(self, cotizacion_id: int) -> Optional[Dict]:
        """Obtiene una cotización específica por su ID."""
        return self._get(f"/cotizaciones/{cotizacion_id}")
    
    def actualizar_cotizacion(self, cotizacion_id: int, cotizacion_data: Dict, items: List[Dict], nota_folio: Optional[str] = None) -> Optional[Dict]:
        """Actualiza una cotización existente."""
        datos_completos = cotizacion_data.copy()
        datos_completos['items'] = items
        
        if nota_folio:
            datos_completos['nota_folio'] = nota_folio
        
        return self._put(f"/cotizaciones/{cotizacion_id}", datos_completos)
    
    def cancelar_cotizacion(self, cotizacion_id: int) -> Optional[Dict]:
        """Marca una cotización como 'Cancelada'."""
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
        """Busca notas de venta usando filtros."""
        return self._get("/notas/buscar", params=filtros) or []
    
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
        return self._put(f"/notas/{nota_id}", datos_completos)
    
    def cancelar_nota(self, nota_id: int) -> Optional[Dict]:
        """Marca una nota de venta como 'Cancelada'."""
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
    
    def buscar_notas_proveedor(self, **filtros) -> List[Dict]:
        """Busca notas de proveedor usando filtros (llamada al servidor)."""
        return self._get("/notas_proveedor/buscar", params=filtros) or []

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
    
    def get_movimientos_inventario(self, producto_id: int = None, tipo: str = None, limit: int = 100) -> List[Dict]:
        params = {}
        if producto_id:
            params['producto_id'] = producto_id
        if tipo:
            params['tipo'] = tipo
        if limit:
            params['limit'] = limit
        return self._get("/inventario/movimientos", params=params) or []
    
    # ==================== REPORTES ====================
    
    def get_reporte_ventas(self, fecha_ini: datetime, fecha_fin: datetime) -> List[Dict]:
        """Obtiene el reporte de ventas por período."""
        params = {
            "fecha_ini": fecha_ini.isoformat(),
            "fecha_fin": fecha_fin.isoformat()
        }
        return self._get("/reportes/ventas", params=params) or []

    def get_reporte_servicios(self, fecha_ini: datetime, fecha_fin: datetime) -> List[Dict]:
        """Obtiene el reporte de servicios más solicitados."""
        params = {
            "fecha_ini": fecha_ini.isoformat(),
            "fecha_fin": fecha_fin.isoformat()
        }
        return self._get("/reportes/servicios", params=params) or []
    
    def get_reporte_clientes(self, fecha_ini: datetime, fecha_fin: datetime) -> List[Dict]:
        """Obtiene el reporte de clientes frecuentes."""
        params = {
            "fecha_ini": fecha_ini.isoformat(),
            "fecha_fin": fecha_fin.isoformat()
        }
        return self._get("/reportes/clientes", params=params) or []
    
    def get_reporte_inventario_bajo_stock(self) -> List[Dict]:
        """Obtiene el reporte de inventario bajo stock (no usa fechas)."""
        return self._get("/reportes/inventario_bajo") or []

    def get_reporte_cuentas_por_cobrar(self) -> List[Dict]:
        """Obtiene el reporte de cuentas por cobrar (no usa fechas)."""
        return self._get("/reportes/cxc") or []
    
    # ==================== LOGIN / USUARIOS / CONFIG (¡ACTUALIZADO!) ====================
    
    def close(self):
        """Cerrar sesión (compatibilidad con db_helper)"""
        self.session.close()
    
    def get_config_empresa(self) -> Optional[Dict]:
        """Obtener configuración de empresa desde API"""
        config = self._get("/configuracion")
        if config and 'logo_data' in config and config['logo_data']:
            try:
                # Decodificar Base64 a bytes
                config['logo_data'] = base64.b64decode(config['logo_data'].encode('utf-8'))
            except Exception as e:
                print(f"Error al decodificar logo: {e}")
                config['logo_data'] = None
        return config

    def guardar_config_empresa(self, datos: Dict) -> bool:
        """Guardar config empresa vía API"""
        datos_serializados = datos.copy()
        # Codificar logo (bytes) a Base64 (string) para JSON
        if 'logo_data' in datos_serializados and datos_serializados['logo_data']:
            try:
                datos_serializados['logo_data'] = base64.b64encode(datos_serializados['logo_data']).decode('utf-8')
            except Exception as e:
                print(f"Error al codificar logo: {e}")
                datos_serializados['logo_data'] = None
                
        result = self._post("/configuracion", datos_serializados)
        return result and result.get('success', False)
    
    def get_usuarios(self) -> List[Dict]:
        """Lista de usuarios desde API"""
        return self._get("/usuarios") or []

    def get_usuario(self, usuario_id: int) -> Optional[Dict]:
        """Obtener un usuario por ID desde API"""
        return self._get(f"/usuarios/{usuario_id}")

    def crear_usuario(self, datos: Dict) -> Optional[Dict]:
        """Crear nuevo usuario vía API"""
        return self._post("/usuarios", datos)

    def actualizar_usuario(self, usuario_id: int, datos: Dict) -> Optional[Dict]:
        """Actualizar usuario existente vía API"""
        return self._put(f"/usuarios/{usuario_id}", datos)

    def contar_admins_activos(self) -> int:
        """Contar admins activos en el sistema vía API"""
        result = self._get("/usuarios/contar_admins")
        if result and 'admins_activos' in result:
            return result['admins_activos']
        return 0

    def eliminar_usuario(self, usuario_id: int) -> bool:
        """Eliminar usuario (soft delete) vía API"""
        result = self._delete(f"/usuarios/{usuario_id}")
        return result and result.get('success', False)

    def validar_login(self, username: str, password: str) -> Optional[Dict]:
        """Verificar login contra el servidor API."""
        data = {"username": username, "password": password}
        # _post maneja los errores HTTP (como 401) y devuelve None si falla
        return self._post("/login", data)

# Crear instancia global
api_client = TallerAPIClient()