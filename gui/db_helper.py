"""
Helper para integrar base de datos con GUI PyQt5
Simplifica el uso del CRUD en las ventanas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_sync
from server import crud
from typing import List, Optional, Dict, Any


class DatabaseHelper:
    """
    Clase helper para operaciones de base de datos en GUI
    Maneja automáticamente la apertura/cierre de sesiones
    """
    
    def __init__(self):
        self.db = None
    
    def _get_session(self):
        """Obtener sesión (reutiliza si existe)"""
        if self.db is None:
            self.db = get_db_sync()
        return self.db
    
    def close(self):
        """Cerrar sesión"""
        if self.db:
            self.db.close()
            self.db = None
    
    # ==================== CLIENTES ====================
    
    def get_clientes(self) -> List[Dict]:
        """Obtener todos los clientes como diccionarios"""
        db = self._get_session()
        clientes = crud.get_all_clientes(db)
        return [self._cliente_to_dict(c) for c in clientes]
    
    def buscar_clientes(self, texto: str) -> List[Dict]:
        """Buscar clientes por texto"""
        db = self._get_session()
        clientes = crud.search_clientes(db, texto)
        return [self._cliente_to_dict(c) for c in clientes]
    
    def crear_cliente(self, datos: Dict) -> Optional[Dict]:
        """Crear nuevo cliente"""
        try:
            db = self._get_session()
            cliente = crud.create_cliente(db, datos)
            return self._cliente_to_dict(cliente)
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            return None
    
    def actualizar_cliente(self, cliente_id: int, datos: Dict) -> Optional[Dict]:
        """Actualizar cliente existente"""
        try:
            db = self._get_session()
            cliente = crud.update_cliente(db, cliente_id, datos)
            return self._cliente_to_dict(cliente) if cliente else None
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            return None
    
    def eliminar_cliente(self, cliente_id: int) -> bool:
        """Eliminar cliente (soft delete)"""
        try:
            db = self._get_session()
            return crud.delete_cliente(db, cliente_id, soft_delete=True)
        except Exception as e:
            print(f"Error al eliminar cliente: {e}")
            return False
    
    # ==================== PROVEEDORES ====================
    
    def get_proveedores(self) -> List[Dict]:
        """Obtener todos los proveedores"""
        db = self._get_session()
        proveedores = crud.get_all_proveedores(db)
        return [self._proveedor_to_dict(p) for p in proveedores]
    
    def crear_proveedor(self, datos: Dict) -> Optional[Dict]:
        """Crear nuevo proveedor"""
        try:
            db = self._get_session()
            proveedor = crud.create_proveedor(db, datos)
            return self._proveedor_to_dict(proveedor)
        except Exception as e:
            print(f"Error al crear proveedor: {e}")
            return None
    
    def actualizar_proveedor(self, proveedor_id: int, datos: Dict) -> Optional[Dict]:
        """Actualizar proveedor"""
        try:
            db = self._get_session()
            proveedor = crud.update_proveedor(db, proveedor_id, datos)
            return self._proveedor_to_dict(proveedor) if proveedor else None
        except Exception as e:
            print(f"Error al actualizar proveedor: {e}")
            return None
    
    def eliminar_proveedor(self, proveedor_id: int) -> bool:
        """Eliminar proveedor"""
        try:
            db = self._get_session()
            return crud.delete_proveedor(db, proveedor_id, soft_delete=True)
        except Exception as e:
            print(f"Error al eliminar proveedor: {e}")
            return False
        
    def buscar_proveedores(self, texto: str) -> List[Dict]:
        """Buscar proveedores"""
        db = self._get_session()
        proveedores = crud.search_proveedores(db, texto)
        return [self._proveedor_to_dict(p) for p in proveedores]
    
    # ==================== INVENTARIO ====================
    
    def get_productos(self) -> List[Dict]:
        """Obtener todos los productos"""
        db = self._get_session()
        productos = crud.get_all_productos(db)
        return [self._producto_to_dict(p) for p in productos]
    
    def get_productos_bajo_stock(self) -> List[Dict]:
        """Obtener productos con stock bajo"""
        db = self._get_session()
        productos = crud.get_productos_bajo_stock(db)
        return [self._producto_to_dict(p) for p in productos]
    
    def buscar_productos(self, texto: str) -> List[Dict]:
        """Buscar productos"""
        db = self._get_session()
        productos = crud.search_productos(db, texto)
        return [self._producto_to_dict(p) for p in productos]
    
    def crear_producto(self, datos: Dict) -> Optional[Dict]:
        """Crear nuevo producto"""
        try:
            db = self._get_session()
            producto = crud.create_producto(db, datos)
            return self._producto_to_dict(producto)
        except Exception as e:
            print(f"Error al crear producto: {e}")
            return None
    
    def registrar_movimiento(self, producto_id: int, tipo: str, cantidad: int, 
                            motivo: str, usuario: str) -> bool:
        """Registrar movimiento de inventario"""
        try:
            db = self._get_session()
            crud.registrar_movimiento_inventario(
                db, producto_id, tipo, cantidad, motivo, usuario
            )
            return True
        except Exception as e:
            print(f"Error al registrar movimiento: {e}")
            return False
    
    def get_movimientos(self, producto_id: Optional[int] = None) -> List[Dict]:
        """Obtener historial de movimientos"""
        db = self._get_session()
        movimientos = crud.get_movimientos_inventario(db, producto_id=producto_id)
        return [self._movimiento_to_dict(m) for m in movimientos]
    
    # ==================== ÓRDENES ====================
    
    def get_ordenes(self, estado: Optional[str] = None) -> List[Dict]:
        """Obtener órdenes"""
        db = self._get_session()
        ordenes = crud.get_all_ordenes(db, estado=estado)
        return [self._orden_to_dict(o) for o in ordenes]
    
    def crear_orden(self, orden_data: Dict, items: List[Dict]) -> Optional[Dict]:
        """Crear nueva orden"""
        try:
            db = self._get_session()
            orden = crud.create_orden(db, orden_data, items)
            return self._orden_to_dict(orden)
        except Exception as e:
            print(f"Error al crear orden: {e}")
            return None
    
    def cambiar_estado_orden(self, orden_id: int, estado: str) -> bool:
        """Cambiar estado de orden"""
        try:
            db = self._get_session()
            crud.cambiar_estado_orden(db, orden_id, estado)
            return True
        except Exception as e:
            print(f"Error al cambiar estado: {e}")
            return False
    
    # ==================== COTIZACIONES ====================
    
    def get_cotizaciones(self, estado: Optional[str] = None) -> List[Dict]:
        """Obtener cotizaciones"""
        db = self._get_session()
        cotizaciones = crud.get_all_cotizaciones(db, estado=estado)
        return [self._cotizacion_to_dict(c) for c in cotizaciones]
    
    def crear_cotizacion(self, cotizacion_data: Dict, items: List[Dict]) -> Optional[Dict]:
        """Crear nueva cotización"""
        try:
            db = self._get_session()
            cotizacion = crud.create_cotizacion(db, cotizacion_data, items)
            return self._cotizacion_to_dict(cotizacion)
        except Exception as e:
            print(f"Error al crear cotización: {e}")
            return None
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_estadisticas(self) -> Dict:
        """Obtener estadísticas del dashboard"""
        db = self._get_session()
        return crud.get_estadisticas_dashboard(db)
    
    # ==================== CONVERSORES ====================
    
    @staticmethod
    def _cliente_to_dict(cliente) -> Dict:
        """Convertir Cliente ORM a diccionario"""
        return {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'tipo': cliente.tipo,
            'email': cliente.email or '',
            'telefono': cliente.telefono or '',
            'calle': cliente.calle or '',
            'colonia': cliente.colonia or '',
            'ciudad': cliente.ciudad or '',
            'estado': cliente.estado or '',
            'cp': cliente.cp or '',
            'pais': cliente.pais or 'México',
            'rfc': cliente.rfc or '',
            'activo': cliente.activo
        }
    
    @staticmethod
    def _proveedor_to_dict(proveedor) -> Dict:
        """Convertir Proveedor ORM a diccionario"""
        return {
            'id': proveedor.id,
            'nombre': proveedor.nombre,
            'tipo': proveedor.tipo,
            'email': proveedor.email or '',
            'telefono': proveedor.telefono or '',
            'calle': proveedor.calle or '',
            'colonia': proveedor.colonia or '',
            'ciudad': proveedor.ciudad or '',
            'estado': proveedor.estado or '',
            'cp': proveedor.cp or '',
            'rfc': proveedor.rfc or ''
        }
    
    @staticmethod
    def _producto_to_dict(producto) -> Dict:
        """Convertir Producto ORM a diccionario"""
        return {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'categoria': producto.categoria,
            'stock_actual': producto.stock_actual,
            'stock_min': producto.stock_min,
            'ubicacion': producto.ubicacion or '',
            'precio_compra': producto.precio_compra,
            'precio_venta': producto.precio_venta,
            'proveedor': producto.proveedor.nombre if producto.proveedor else '',
            'descripcion': producto.descripcion or ''
        }
    
    @staticmethod
    def _movimiento_to_dict(movimiento) -> Dict:
        """Convertir MovimientoInventario ORM a diccionario"""
        return {
            'id': movimiento.id,
            'fecha': movimiento.created_at.strftime("%d/%m/%Y %H:%M"),
            'tipo': movimiento.tipo,
            'producto': movimiento.producto.nombre,
            'cantidad': movimiento.cantidad,
            'usuario': movimiento.usuario,
            'motivo': movimiento.motivo
        }
    
    @staticmethod
    def _orden_to_dict(orden) -> Dict:
        """Convertir Orden ORM a diccionario"""
        return {
            'id': orden.id,
            'folio': orden.folio,
            'cliente_id': orden.cliente_id,
            'cliente_nombre': orden.cliente.nombre,
            'vehiculo_marca': orden.vehiculo_marca or '',
            'vehiculo_modelo': orden.vehiculo_modelo or '',
            'vehiculo_ano': orden.vehiculo_ano or '',
            'vehiculo_placas': orden.vehiculo_placas or '',
            'estado': orden.estado,
            'mecanico_asignado': orden.mecanico_asignado or '',
            'items': [{'cantidad': i.cantidad, 'descripcion': i.descripcion} for i in orden.items],
            'observaciones': orden.observaciones or ''
        }
    
    @staticmethod
    def _cotizacion_to_dict(cotizacion) -> Dict:
        """Convertir Cotizacion ORM a diccionario"""
        return {
            'id': cotizacion.id,
            'folio': cotizacion.folio,
            'cliente_id': cotizacion.cliente_id,
            'cliente_nombre': cotizacion.cliente.nombre,
            'estado': cotizacion.estado,
            'subtotal': cotizacion.subtotal,
            'impuestos': cotizacion.impuestos,
            'total': cotizacion.total,
            'items': [{
                'cantidad': i.cantidad,
                'descripcion': i.descripcion,
                'precio_unitario': i.precio_unitario,
                'importe': i.importe
            } for i in cotizacion.items]
        }


# Instancia global para usar en toda la aplicación
db_helper = DatabaseHelper()