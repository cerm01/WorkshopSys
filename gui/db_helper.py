import sys
import os
import hashlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_sync
from server import crud
from typing import List, Optional, Dict, Any
from datetime import datetime

def generar_hash_password(password: str) -> str:
    """Generar hash SHA256 de contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

class DatabaseHelper:
    
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
        """Obtener todos los clientes"""
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
    
    def buscar_proveedores(self, texto: str) -> List[Dict]:
        """Buscar proveedores por texto"""
        db = self._get_session()
        proveedores = crud.search_proveedores(db, texto)
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
        """Actualizar proveedor existente"""
        try:
            db = self._get_session()
            proveedor = crud.update_proveedor(db, proveedor_id, datos)
            return self._proveedor_to_dict(proveedor) if proveedor else None
        except Exception as e:
            print(f"Error al actualizar proveedor: {e}")
            return None
    
    def eliminar_proveedor(self, proveedor_id: int) -> bool:
        """Eliminar proveedor (soft delete)"""
        try:
            db = self._get_session()
            return crud.delete_proveedor(db, proveedor_id, soft_delete=True)
        except Exception as e:
            print(f"Error al eliminar proveedor: {e}")
            return False
    
    # ==================== PRODUCTOS ====================
    
    def get_productos(self) -> List[Dict]:
        """Obtener todos los productos"""
        db = self._get_session()
        productos = crud.get_all_productos(db)
        return [self._producto_to_dict(p) for p in productos]
    
    def buscar_productos(self, texto: str) -> List[Dict]:
        """Buscar productos por texto"""
        db = self._get_session()
        productos = crud.search_productos(db, texto)
        return [self._producto_to_dict(p) for p in productos]
    
    def get_productos_bajo_stock(self) -> List[Dict]:
        """Obtener productos bajo stock mínimo"""
        db = self._get_session()
        productos = crud.get_productos_bajo_stock(db)
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
    
    def actualizar_producto(self, producto_id: int, datos: Dict) -> Optional[Dict]:
        """Actualizar producto existente"""
        try:
            db = self._get_session()
            producto = crud.update_producto(db, producto_id, datos)
            return self._producto_to_dict(producto) if producto else None
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            return None
    
    def eliminar_producto(self, producto_id: int) -> bool:
        """Eliminar producto (soft delete)"""
        try:
            db = self._get_session()
            return crud.delete_producto(db, producto_id, soft_delete=True)
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            return False
    
    # ==================== MOVIMIENTOS ====================
    
    def registrar_movimiento(self, datos: Dict) -> bool:
        """Registrar movimiento de inventario"""
        try:
            db = self._get_session()
            crud.registrar_movimiento_inventario(db, datos)
            return True
        except Exception as e:
            print(f"Error al registrar movimiento: {e}")
            return False
    
    def get_movimientos(self, producto_id: Optional[int] = None) -> List[Dict]:
        """Obtener movimientos de inventario"""
        db = self._get_session()
        movimientos = crud.get_movimientos_inventario(db, producto_id)
        return [self._movimiento_to_dict(m) for m in movimientos]
    
    # ==================== ÓRDENES ====================
    
    def crear_orden(self, datos: Dict) -> Optional[int]:
        """Crear nueva orden"""
        try:
            db = self._get_session()
            orden = crud.create_orden(db, datos)
            return orden.id if orden else None
        except Exception as e:
            print(f"Error al crear orden: {e}")
            return None
    
    def buscar_ordenes(self, **filtros) -> List[Dict]:
        """Buscar órdenes con filtros"""
        db = self._get_session()
        ordenes = crud.search_ordenes(db, **filtros)
        return [self._orden_to_dict(o) for o in ordenes]
    
    def get_orden(self, orden_id: int) -> Optional[Dict]:
        """Obtener orden por ID"""
        db = self._get_session()
        orden = crud.get_orden(db, orden_id)
        return self._orden_to_dict(orden) if orden else None
    
    def actualizar_orden(self, orden_id: int, datos: Dict) -> bool:
        """Actualizar orden"""
        try:
            db = self._get_session()
            crud.update_orden(db, orden_id, datos)
            return True
        except Exception as e:
            print(f"Error al actualizar orden: {e}")
            return False
    
    def cancelar_orden(self, orden_id: int) -> bool:
        """Cancelar orden"""
        try:
            db = self._get_session()
            crud.cancel_orden(db, orden_id)
            return True
        except Exception as e:
            print(f"Error al cancelar orden: {e}")
            return False
    
    # ==================== COTIZACIONES ====================
    
    def crear_cotizacion(self, datos: Dict) -> Optional[int]:
        """Crear nueva cotización"""
        try:
            db = self._get_session()
            cotizacion = crud.create_cotizacion(db, datos)
            return cotizacion.id if cotizacion else None
        except Exception as e:
            print(f"Error al crear cotización: {e}")
            return None
    
    def buscar_cotizaciones(self, **filtros) -> List[Dict]:
        """Buscar cotizaciones con filtros"""
        db = self._get_session()
        cotizaciones = crud.search_cotizaciones(db, **filtros)
        return [self._cotizacion_to_dict(c) for c in cotizaciones]
    
    def get_cotizacion(self, cotizacion_id: int) -> Optional[Dict]:
        """Obtener cotización por ID"""
        db = self._get_session()
        cotizacion = crud.get_cotizacion(db, cotizacion_id)
        return self._cotizacion_to_dict(cotizacion) if cotizacion else None
    
    def actualizar_cotizacion(self, cotizacion_id: int, datos: Dict) -> bool:
        """Actualizar cotización"""
        try:
            db = self._get_session()
            crud.update_cotizacion(db, cotizacion_id, datos)
            return True
        except Exception as e:
            print(f"Error al actualizar cotización: {e}")
            return False
    
    def cancelar_cotizacion(self, cotizacion_id: int) -> bool:
        """Cancelar cotización"""
        try:
            db = self._get_session()
            crud.cancel_cotizacion(db, cotizacion_id)
            return True
        except Exception as e:
            print(f"Error al cancelar cotización: {e}")
            return False
    
    def convertir_cotizacion_a_nota(self, cotizacion_id: int) -> Optional[int]:
        """Convertir cotización a nota de venta"""
        try:
            db = self._get_session()
            nota = crud.convertir_cotizacion_a_nota(db, cotizacion_id)
            return nota.id if nota else None
        except Exception as e:
            print(f"Error al convertir cotización: {e}")
            return None
    
    # ==================== NOTAS DE VENTA ====================
    
    def crear_nota(self, datos: Dict) -> Optional[int]:
        """Crear nueva nota de venta"""
        try:
            db = self._get_session()
            nota = crud.create_nota_venta(db, datos)
            return nota.id if nota else None
        except Exception as e:
            print(f"Error al crear nota: {e}")
            return None
    
    def buscar_notas(self, **filtros) -> List[Dict]:
        """Buscar notas con filtros"""
        db = self._get_session()
        notas = crud.search_notas_venta(db, **filtros)
        return [self._nota_to_dict(n) for n in notas]
    
    def get_nota(self, nota_id: int) -> Optional[Dict]:
        """Obtener nota por ID"""
        db = self._get_session()
        nota = crud.get_nota_venta(db, nota_id)
        return self._nota_to_dict(nota) if nota else None
    
    def actualizar_nota(self, nota_id: int, datos: Dict) -> bool:
        """Actualizar nota"""
        try:
            db = self._get_session()
            crud.update_nota_venta(db, nota_id, datos)
            return True
        except Exception as e:
            print(f"Error al actualizar nota: {e}")
            return False
    
    def cancelar_nota(self, nota_id: int) -> bool:
        """Cancelar nota"""
        try:
            db = self._get_session()
            crud.cancel_nota_venta(db, nota_id)
            return True
        except Exception as e:
            print(f"Error al cancelar nota: {e}")
            return False
    
    # ==================== PAGOS DE NOTAS ====================
    
    def get_pagos_nota(self, nota_id: int) -> List[Dict]:
        """Obtener historial de pagos de una nota"""
        db = self._get_session()
        pagos = crud.get_pagos_por_nota(db, nota_id)
        return [self._pago_to_dict(p) for p in pagos]

    def registrar_pago(self, nota_id: int, monto: float, fecha_pago: datetime, metodo_pago: str, memo: str) -> Optional[Dict]:
        """Registrar un pago y devolver la nota actualizada"""
        try:
            db = self._get_session()
            nota_actualizada = crud.registrar_pago_nota(db, nota_id, monto, fecha_pago, metodo_pago, memo)
            return self._nota_to_dict(nota_actualizada) if nota_actualizada else None
        except Exception as e:
            print(f"Error en db_helper al registrar pago: {e}")
            raise e
    
    def eliminar_pago(self, pago_id: int) -> Optional[Dict]:
        """Elimina un pago y devuelve la nota actualizada"""
        try:
            db = self._get_session()
            nota_actualizada = crud.eliminar_pago_nota(db, pago_id)
            return self._nota_to_dict(nota_actualizada)
        except Exception as e:
            print(f"Error en db_helper al eliminar pago: {e}")
            raise e
    
    # ==================== NOTAS DE PROVEEDOR ====================
    
    def crear_nota_proveedor(self, datos: Dict) -> Optional[int]:
        """Crear nueva nota de proveedor"""
        try:
            db = self._get_session()
            nota = crud.create_nota_proveedor(db, datos)
            return nota.id if nota else None
        except Exception as e:
            print(f"Error al crear nota proveedor: {e}")
            return None
    
    def buscar_notas_proveedor(self, **filtros) -> List[Dict]:
        """Buscar notas de proveedor con filtros"""
        db = self._get_session()
        notas = crud.search_notas_proveedor(db, **filtros)
        return [self._nota_proveedor_to_dict(n) for n in notas]
    
    def get_nota_proveedor(self, nota_id: int) -> Optional[Dict]:
        """Obtener nota de proveedor por ID"""
        db = self._get_session()
        nota = crud.get_nota_proveedor(db, nota_id)
        return self._nota_proveedor_to_dict(nota) if nota else None
    
    def actualizar_nota_proveedor(self, nota_id: int, datos: Dict) -> bool:
        """Actualizar nota de proveedor"""
        try:
            db = self._get_session()
            crud.update_nota_proveedor(db, nota_id, datos)
            return True
        except Exception as e:
            print(f"Error al actualizar nota proveedor: {e}")
            return False
    
    def cancelar_nota_proveedor(self, nota_id: int) -> bool:
        """Cancelar nota de proveedor"""
        try:
            db = self._get_session()
            crud.cancel_nota_proveedor(db, nota_id)
            return True
        except Exception as e:
            print(f"Error al cancelar nota proveedor: {e}")
            return False
    
    # ==================== PAGOS DE NOTAS PROVEEDOR ====================
    
    def get_pagos_nota_proveedor(self, nota_id: int) -> List[Dict]:
        """Obtener historial de pagos de una nota de proveedor"""
        db = self._get_session()
        pagos = crud.get_pagos_por_nota_proveedor(db, nota_id)
        return [self._pago_proveedor_to_dict(p) for p in pagos]

    def registrar_pago_proveedor(self, nota_id: int, monto: float, fecha_pago: datetime, metodo_pago: str, memo: str) -> Optional[Dict]:
        """Registrar un pago a proveedor y devolver la nota actualizada"""
        try:
            db = self._get_session()
            nota_actualizada = crud.registrar_pago_nota_proveedor(db, nota_id, monto, fecha_pago, metodo_pago, memo)
            return self._nota_proveedor_to_dict(nota_actualizada) if nota_actualizada else None
        except Exception as e:
            print(f"Error en db_helper al registrar pago proveedor: {e}")
            raise e
    
    def eliminar_pago_proveedor(self, pago_id: int) -> Optional[Dict]:
        """Elimina un pago a proveedor y devuelve la nota actualizada"""
        try:
            db = self._get_session()
            nota_actualizada = crud.eliminar_pago_nota_proveedor(db, pago_id)
            return self._nota_proveedor_to_dict(nota_actualizada)
        except Exception as e:
            print(f"Error en db_helper al eliminar pago proveedor: {e}")
            raise e
    
    # ==================== CONFIGURACIÓN EMPRESA ====================
    
    def get_config_empresa(self) -> Optional[Dict]:
        """Obtener configuración de empresa"""
        try:
            from server.models import ConfigEmpresa
            db = self._get_session()
            config = db.query(ConfigEmpresa).first()
            
            if not config:
                return None
            
            return {
                'id': config.id,
                'nombre_comercial': config.nombre_comercial,
                'razon_social': config.razon_social or '',
                'rfc': config.rfc or '',
                'calle': config.calle or '',
                'colonia': config.colonia or '',
                'ciudad': config.ciudad or '',
                'estado': config.estado or '',
                'cp': config.cp or '',
                'pais': config.pais or 'México',
                'telefono1': config.telefono1 or '',
                'telefono2': config.telefono2 or '',
                'email': config.email or '',
                'sitio_web': config.sitio_web or '',
                'logo_data': config.logo_data
            }
        except Exception as e:
            print(f"Error get_config_empresa: {e}")
            return None

    def guardar_config_empresa(self, datos: Dict) -> bool:
        """Guardar o actualizar configuración de empresa"""
        try:
            from server.models import ConfigEmpresa
            db = self._get_session()
            config = db.query(ConfigEmpresa).first()
            
            if config:
                for key, value in datos.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            else:
                config = ConfigEmpresa(**datos)
                db.add(config)
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error guardar_config_empresa: {e}")
            db.rollback()
            return False

    # ==================== USUARIOS ====================

    def get_usuarios(self) -> List[Dict]:
        """Obtener todos los usuarios"""
        try:
            from server.models import Usuario
            db = self._get_session()
            usuarios = db.query(Usuario).all()
            return [self._usuario_to_dict(u) for u in usuarios]
        except Exception as e:
            print(f"Error get_usuarios: {e}")
            return []

    def get_usuario(self, usuario_id: int) -> Optional[Dict]:
        """Obtener usuario por ID"""
        try:
            from server.models import Usuario
            db = self._get_session()
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            return self._usuario_to_dict(usuario) if usuario else None
        except Exception as e:
            print(f"Error get_usuario: {e}")
            return None

    def get_usuario_by_username(self, username: str) -> Optional[Dict]:
        """Obtener usuario por username"""
        try:
            from server.models import Usuario
            db = self._get_session()
            usuario = db.query(Usuario).filter(Usuario.username == username).first()
            return self._usuario_to_dict(usuario) if usuario else None
        except Exception as e:
            print(f"Error get_usuario_by_username: {e}")
            return None

    def crear_usuario(self, datos: Dict) -> bool:
        """Crear nuevo usuario"""
        try:
            from server.models import Usuario
            db = self._get_session()
            
            # Validar username único
            existe = db.query(Usuario).filter(Usuario.username == datos['username']).first()
            if existe:
                return False
            
            nuevo_usuario = Usuario(**datos)
            db.add(nuevo_usuario)
            db.commit()
            return True
        except Exception as e:
            print(f"Error crear_usuario: {e}")
            db.rollback()
            return False

    def actualizar_usuario(self, usuario_id: int, datos: Dict) -> bool:
        """Actualizar usuario existente"""
        try:
            from server.models import Usuario
            db = self._get_session()
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            
            if not usuario:
                return False
            
            for key, value in datos.items():
                if hasattr(usuario, key):
                    setattr(usuario, key, value)
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error actualizar_usuario: {e}")
            db.rollback()
            return False

    def contar_admins_activos(self) -> int:
        """Contar admins activos en el sistema"""
        try:
            from server.models import Usuario
            db = self._get_session()
            return db.query(Usuario).filter(
                Usuario.rol == 'Admin',
                Usuario.activo == True
            ).count()
        except Exception as e:
            print(f"Error contar_admins_activos: {e}")
            return 0

    def eliminar_usuario(self, usuario_id: int) -> bool:
        """Eliminar usuario (hard delete)"""
        try:
            from server.models import Usuario
            db = self._get_session()
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            
            if not usuario:
                return False
            
            db.delete(usuario)
            db.commit()
            return True
        except Exception as e:
            print(f"Error eliminar_usuario: {e}")
            db.rollback()
            return False

    def validar_login(self, username: str, password: str) -> Optional[Dict]:
        """Validar credenciales de login"""
        usuario = self.get_usuario_by_username(username)
        
        if not usuario or not usuario['activo']:
            return None
        
        password_hash = generar_hash_password(password)
        
        if usuario['password_hash'] == password_hash:
            try:
                from server.models import Usuario
                db = self._get_session()
                user = db.query(Usuario).filter(Usuario.id == usuario['id']).first()
                if user:
                    user.ultimo_acceso = datetime.now()
                    db.commit()
            except:
                pass
            return usuario
        
        return None
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_estadisticas(self) -> Dict:
        """Obtener estadísticas del dashboard"""
        db = self._get_session()
        return crud.get_estadisticas_dashboard(db)
    
    # ==================== CONVERSORES (ORM -> Dict) ====================
    
    @staticmethod
    def _cliente_to_dict(cliente) -> Dict:
        """Convertir Cliente ORM a diccionario"""
        if not cliente: return {}
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
            'rfc': cliente.rfc or ''
        }
    
    @staticmethod
    def _proveedor_to_dict(proveedor) -> Dict:
        """Convertir Proveedor ORM a diccionario"""
        if not proveedor: return {}
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
            'pais': proveedor.pais or 'México',
            'rfc': proveedor.rfc or ''
        }
    
    @staticmethod
    def _producto_to_dict(producto) -> Dict:
        """Convertir Producto ORM a diccionario"""
        if not producto: return {}
        return {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'categoria': producto.categoria or '',
            'ubicacion': producto.ubicacion or '',
            'proveedor': producto.proveedor.nombre if producto.proveedor else '',
            'proveedor_id': producto.proveedor_id,
            'precio_compra': producto.precio_compra,
            'precio_venta': producto.precio_venta,
            'stock_actual': producto.stock_actual,
            'stock_min': producto.stock_min,
            'descripcion': producto.descripcion or ''
        }
    
    @staticmethod
    def _movimiento_to_dict(movimiento) -> Dict:
        """Convertir MovimientoInventario ORM a diccionario"""
        if not movimiento: return {}
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
        if not orden: return {}
        return {
            'id': orden.id,
            'folio': orden.folio,
            'cliente_id': orden.cliente_id,
            'cliente_nombre': orden.cliente.nombre if orden.cliente else '',
            'vehiculo': orden.vehiculo or '',
            'estado': orden.estado,
            'fecha_entrada': orden.fecha_entrada.strftime("%d/%m/%Y %H:%M"),
            'fecha_promesa': orden.fecha_promesa.strftime("%d/%m/%Y") if orden.fecha_promesa else '',
            'fecha_salida': orden.fecha_salida.strftime("%d/%m/%Y %H:%M") if orden.fecha_salida else '',
            'mecanico': orden.mecanico or '',
            'observaciones': orden.observaciones or '',
            'subtotal': orden.subtotal,
            'impuestos': orden.impuestos,
            'total': orden.total,
            'servicios': [s.descripcion for s in orden.servicios]
        }
    
    @staticmethod
    def _cotizacion_to_dict(cotizacion) -> Dict:
        """Convertir Cotizacion ORM a diccionario"""
        if not cotizacion: return {}
        return {
            'id': cotizacion.id,
            'folio': cotizacion.folio,
            'cliente_id': cotizacion.cliente_id,
            'cliente_nombre': cotizacion.cliente.nombre if cotizacion.cliente else '',
            'proyecto': cotizacion.proyecto or '',
            'estado': cotizacion.estado,
            'fecha': cotizacion.fecha.strftime("%d/%m/%Y"),
            'vigencia': cotizacion.vigencia.strftime("%d/%m/%Y") if cotizacion.vigencia else '',
            'subtotal': cotizacion.subtotal,
            'impuestos': cotizacion.impuestos,
            'total': cotizacion.total,
            'nota_folio': cotizacion.nota_folio,
            'items': [{
                'cantidad': i.cantidad,
                'descripcion': i.descripcion,
                'precio_unitario': i.precio_unitario,
                'importe': i.importe
            } for i in cotizacion.items]
        }
    
    @staticmethod
    def _pago_to_dict(pago) -> Dict:
        """Convertir NotaVentaPago ORM a diccionario"""
        if not pago: return {}
        return {
            'id': pago.id,
            'nota_id': pago.nota_id,
            'monto': pago.monto,
            'fecha_pago': pago.fecha_pago.strftime("%d/%m/%Y %H:%M"),
            'metodo_pago': pago.metodo_pago,
            'memo': pago.memo or ''
        }

    @staticmethod
    def _nota_to_dict(nota) -> Dict:
        """Convertir NotaVenta ORM a diccionario"""
        if not nota: return {}
        return {
            'id': nota.id,
            'folio': nota.folio,
            'cliente_id': nota.cliente_id,
            'cliente_nombre': nota.cliente.nombre if nota.cliente else '',
            'estado': nota.estado or 'Registrado',
            'metodo_pago': nota.metodo_pago or 'Efectivo',
            'fecha': nota.fecha.strftime("%d/%m/%Y") if nota.fecha else '',
            'observaciones': nota.observaciones or '',
            'subtotal': nota.subtotal,
            'impuestos': nota.impuestos,
            'total': nota.total,
            'total_pagado': nota.total_pagado,
            'saldo': nota.saldo,
            'items': [{
                'cantidad': i.cantidad,
                'descripcion': i.descripcion,
                'precio_unitario': i.precio_unitario,
                'importe': i.importe,
                'impuesto': i.impuesto
            } for i in nota.items],
            'pagos': [DatabaseHelper._pago_to_dict(p) for p in nota.pagos]
        }

    @staticmethod
    def _pago_proveedor_to_dict(pago) -> Dict:
        """Convertir NotaProveedorPago ORM a diccionario"""
        if not pago: return {}
        return {
            'id': pago.id,
            'nota_id': pago.nota_id,
            'monto': pago.monto,
            'fecha_pago': pago.fecha_pago.strftime("%d/%m/%Y %H:%M"),
            'metodo_pago': pago.metodo_pago,
            'memo': pago.memo or ''
        }

    @staticmethod
    def _nota_proveedor_to_dict(nota) -> Dict:
        """Convertir NotaProveedor ORM a diccionario"""
        if not nota: return {}
        return {
            'id': nota.id,
            'folio': nota.folio,
            'proveedor_id': nota.proveedor_id,
            'proveedor_nombre': nota.proveedor.nombre if nota.proveedor else '',
            'estado': nota.estado or 'Registrado',
            'metodo_pago': nota.metodo_pago or 'Efectivo',
            'fecha': nota.fecha.strftime("%d/%m/%Y") if nota.fecha else '',
            'observaciones': nota.observaciones or '',
            'subtotal': nota.subtotal,
            'impuestos': nota.impuestos,
            'total': nota.total,
            'total_pagado': nota.total_pagado,
            'saldo': nota.saldo,
            'items': [{
                'cantidad': i.cantidad,
                'descripcion': i.descripcion,
                'precio_unitario': i.precio_unitario,
                'importe': i.importe,
                'impuesto': i.impuesto
            } for i in nota.items],
            'pagos': [DatabaseHelper._pago_proveedor_to_dict(p) for p in nota.pagos]
        }

    @staticmethod
    def _usuario_to_dict(usuario) -> Dict:
        """Convertir Usuario ORM a diccionario"""
        if not usuario: return {}
        return {
            'id': usuario.id,
            'username': usuario.username,
            'password_hash': usuario.password_hash,
            'nombre_completo': usuario.nombre_completo,
            'email': usuario.email or '',
            'rol': usuario.rol,
            'activo': usuario.activo,
            'ultimo_acceso': usuario.ultimo_acceso.strftime("%d/%m/%Y %H:%M") if usuario.ultimo_acceso else ''
        }

# Instancia global
db_helper = DatabaseHelper()