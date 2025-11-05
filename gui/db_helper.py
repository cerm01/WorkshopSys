import sys
import os
import hashlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_sync
from server import crud
from typing import List, Optional, Dict, Any
from datetime import datetime

@staticmethod
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
    
    def get_productos_sin_stock(self) -> List[Dict]:
        """Obtener productos sin stock"""
        db = self._get_session()
        productos = crud.get_productos_sin_stock(db)
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
        """Eliminar producto"""
        try:
            db = self._get_session()
            return crud.delete_producto(db, producto_id, soft_delete=True)
        except Exception as e:
            print(f"Error al eliminar producto: {e}")
            return False
    
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
    
    def buscar_ordenes(self, folio: str = None, cliente_id: int = None) -> List[Dict]:
        """Buscar órdenes por folio o cliente"""
        db = self._get_session()
        ordenes = crud.get_all_ordenes(db)
        
        if folio:
            ordenes = [o for o in ordenes if folio.upper() in o.folio.upper()]
        if cliente_id:
            ordenes = [o for o in ordenes if o.cliente_id == cliente_id]
        
        return [self._orden_to_dict(o) for o in ordenes]

    def crear_orden(self, orden_data: Dict, items: List[Dict]) -> Optional[Dict]:
        try:
            db = self._get_session()
            orden = crud.create_orden(db, orden_data, items)
            return self._orden_to_dict(orden)
        except Exception as e:
            print(f"Error al crear orden: {e}")
            return None

    def actualizar_orden(self, orden_id: int, orden_data: Dict, items: List[Dict]) -> Optional[Dict]:
        try:
            db = self._get_session()
            orden = crud.update_orden(db, orden_id, orden_data)
            if not orden:
                return None
            
            # Eliminar items viejos
            db.query(crud.OrdenItem).filter(crud.OrdenItem.orden_id == orden_id).delete()
            
            # Agregar nuevos items
            for item_data in items:
                item = crud.OrdenItem(orden_id=orden_id, **item_data)
                db.add(item)
            
            db.commit()
            db.refresh(orden)
            return self._orden_to_dict(orden)
        except Exception as e:
            print(f"Error al actualizar orden: {e}")
            db.rollback()
            return None

    def cancelar_orden(self, orden_id: int) -> bool:
        try:
            db = self._get_session()
            return crud.cambiar_estado_orden(db, orden_id, "Cancelada") is not None
        except Exception as e:
            print(f"Error al cancelar orden: {e}")
            return False
    
    def actualizar_orden_campos_simples(self, orden_id: int, datos: Dict) -> Optional[Dict]:
        """Actualiza solo los campos principales de una orden (sin tocar items)"""
        try:
            db = self._get_session()
            # crud.update_orden es seguro, no borra items
            orden = crud.update_orden(db, orden_id, datos)
            return self._orden_to_dict(orden) if orden else None
        except Exception as e:
            print(f"Error al actualizar campos de orden: {e}")
            return None

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
        
    def buscar_cotizaciones(self, folio: str = None, cliente_id: int = None) -> List[Dict]:
        """Buscar cotizaciones por folio o cliente"""
        db = self._get_session()
        cotizaciones = crud.get_all_cotizaciones(db)
        
        # Filtrar según criterios
        if folio:
            cotizaciones = [c for c in cotizaciones if folio.upper() in c.folio.upper()]
        if cliente_id:
            cotizaciones = [c for c in cotizaciones if c.cliente_id == cliente_id]
        
        return [self._cotizacion_to_dict(c) for c in cotizaciones]

    def actualizar_cotizacion(self, cotizacion_id: int, cotizacion_data: Dict, items: List[Dict], nota_folio: str = None) -> Optional[Dict]:
        """Actualizar cotización, opcionalmente vincular con nota"""
        try:
            db = self._get_session()
            
            cotizacion = crud.get_cotizacion(db, cotizacion_id)
            if not cotizacion:
                print(f"❌ No se encontró la cotización con ID {cotizacion_id}")
                return None
            
            print(f"📝 Actualizando cotización {cotizacion.folio}...")
            
            # Actualizar datos principales
            cotizacion.cliente_id = cotizacion_data.get('cliente_id', cotizacion.cliente_id)
            cotizacion.estado = cotizacion_data.get('estado', cotizacion.estado)
            cotizacion.vigencia = cotizacion_data.get('vigencia', cotizacion.vigencia)
            cotizacion.observaciones = cotizacion_data.get('observaciones', cotizacion.observaciones)
            
            # Vincular con nota si se proporciona
            if nota_folio:
                cotizacion.nota_folio = nota_folio
            
            # Eliminar items anteriores
            from server.models import CotizacionItem
            for item in cotizacion.items:
                db.delete(item)
            db.flush()
            
            # Agregar nuevos items y recalcular
            subtotal = 0
            impuestos_total = 0
            
            for item_data in items:
                item = CotizacionItem(cotizacion_id=cotizacion.id, **item_data)
                db.add(item)
                subtotal += item.importe
                impuestos_total += (item.importe * item.impuesto / 100)
            
            cotizacion.subtotal = subtotal
            cotizacion.impuestos = impuestos_total
            cotizacion.total = subtotal + impuestos_total
            
            db.commit()
            db.refresh(cotizacion)
            
            print(f"✅ Cotización actualizada correctamente")
            return self._cotizacion_to_dict(cotizacion)
            
        except Exception as e:
            print(f"❌ Error al actualizar cotización: {e}")
            db.rollback()
            import traceback
            traceback.print_exc()
            return None
    
    def cancelar_cotizacion(self, cotizacion_id: int) -> bool:
        """Cancelar una cotización"""
        try:
            db = self._get_session()
            return crud.cancelar_cotizacion(db, cotizacion_id)
        except Exception as e:
            print(f"Error al cancelar cotización: {e}")
            return False
    # ==================== NOTAS DE VENTA ====================
    
    def get_notas(self, estado: Optional[str] = None) -> List[Dict]:
        """Obtener todas las notas de venta"""
        db = self._get_session()
        notas = crud.get_all_notas(db, estado=estado)
        return [self._nota_to_dict(n) for n in notas]
    
    def get_nota(self, nota_id: int) -> Optional[Dict]:
        """Obtener nota por ID"""
        db = self._get_session()
        nota = crud.get_nota(db, nota_id)
        return self._nota_to_dict(nota) if nota else None
    
    def buscar_notas(self, folio: str = None, cliente_id: int = None, orden_folio: str = None) -> List[Dict]:
        """Buscar notas por folio, cliente_id u orden_folio"""
        db = self._get_session()
        notas = crud.get_all_notas(db)
        
        if folio:
            notas = [n for n in notas if folio.upper() in n.folio.upper()]
        if cliente_id:
            notas = [n for n in notas if n.cliente_id == cliente_id]
        if orden_folio:
            notas = [n for n in notas if n.orden_folio == orden_folio]
        
        return [self._nota_to_dict(n) for n in notas]
    
    def crear_nota(self, nota_data: Dict, items: List[Dict], cotizacion_folio: str = None, orden_folio: str = None, estado: str = 'Registrado') -> Optional[Dict]:
        """Crear nueva nota de venta, opcionalmente vinculada a cotización u orden, con estado específico"""
        try:
            db = self._get_session()
            
            if cotizacion_folio:
                nota_data['cotizacion_folio'] = cotizacion_folio
            
            if orden_folio:
                nota_data['orden_folio'] = orden_folio
            
            nota = crud.create_nota_venta(db, nota_data, items, estado=estado)
            return self._nota_to_dict(nota)
        except Exception as e:
            print(f"Error al crear nota: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def actualizar_nota(self, nota_id: int, nota_data: Dict, items: List[Dict]) -> Optional[Dict]:
        try:
            db = self._get_session()
            
            nota = crud.get_nota(db, nota_id)
            if not nota:
                print(f"❌ No se encontró la nota con ID {nota_id}")
                return None
            
            print(f"📝 Actualizando nota {nota.folio}...")
            
            # --- INICIO DE MODIFICACIÓN (PUNTO 1) ---
            # Guardar el estado original antes de cualquier cambio
            estado_original = nota.estado
            # --- FIN DE MODIFICACIÓN ---

            nota.cliente_id = nota_data.get('cliente_id', nota.cliente_id)
            # nota.estado = nota_data.get('estado', nota.estado) # <- No actualizar estado desde aquí
            nota.metodo_pago = nota_data.get('metodo_pago', nota.metodo_pago)
            nota.fecha = nota_data.get('fecha', nota.fecha)
            nota.observaciones = nota_data.get('observaciones', nota.observaciones)
            
            from server.models import NotaVentaItem
            
            for item in nota.items:
                db.delete(item)
            db.flush()
            
            subtotal = 0
            total_impuestos = 0
            
            for item_data in items:
                cantidad = item_data['cantidad']
                precio_unitario = item_data['precio_unitario']
                impuesto_porcentaje = item_data.get('impuesto', 16.0)
                
                importe_sin_iva = cantidad * precio_unitario
                iva_item = importe_sin_iva * (impuesto_porcentaje / 100)
                
                nuevo_item = NotaVentaItem(
                    nota_id=nota.id,
                    cantidad=cantidad,
                    descripcion=item_data['descripcion'],
                    precio_unitario=precio_unitario,
                    importe=importe_sin_iva,
                    impuesto=impuesto_porcentaje
                )
                
                db.add(nuevo_item)
                
                subtotal += importe_sin_iva
                total_impuestos += iva_item
            
            nota.subtotal = subtotal
            nota.impuestos = total_impuestos
            nota.total = subtotal + total_impuestos
            nota.saldo = nota.total - nota.total_pagado
            
            # Lógica de actualización de estado
            if nota.saldo <= 0.01 and nota.estado != 'Cancelada':
                nota.saldo = 0.0
                nota.estado = 'Pagado'
            elif nota.total_pagado > 0 and nota.estado != 'Cancelada':
                nota.estado = 'Pagado Parcialmente'
            elif nota.total_pagado == 0 and nota.estado != 'Cancelada':
                # Si el estado original era Borrador, al actualizar pasa a Registrado
                if estado_original == 'Borrador':
                    nota.estado = 'Registrado'

            nota.updated_at = datetime.now()
            
            db.commit()
            db.refresh(nota)
            
            print(f"✅ Nota {nota.folio} actualizada correctamente")
            return self._nota_to_dict(nota)
            
        except Exception as e:
            print(f"❌ Error al actualizar nota: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return None
        
    def cancelar_nota(self, nota_id: int) -> bool:
        """Cancelar una nota de venta"""
        try:
            db = self._get_session()
            return crud.cancelar_nota(db, nota_id)
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
    
    def get_notas_proveedor(self) -> List[Dict]:
        """Obtener todas las notas de proveedor"""
        db = self._get_session()
        notas = crud.get_all_notas_proveedor(db)
        return [self._nota_proveedor_to_dict(n) for n in notas]
    
    def get_nota_proveedor(self, nota_id: int) -> Optional[Dict]:
        """Obtener nota de proveedor por ID"""
        db = self._get_session()
        nota = crud.get_nota_proveedor(db, nota_id)
        return self._nota_proveedor_to_dict(nota) if nota else None
    
    def buscar_notas_proveedor(self, folio: str = None, proveedor_id: int = None) -> List[Dict]:
        """Buscar notas de proveedor por folio o proveedor_id"""
        db = self._get_session()
        notas = crud.get_all_notas_proveedor(db)
        
        if folio:
            notas = [n for n in notas if folio.upper() in n.folio.upper()]
        if proveedor_id:
            notas = [n for n in notas if n.proveedor_id == proveedor_id]
        
        return [self._nota_proveedor_to_dict(n) for n in notas]
    
    def crear_nota_proveedor(self, nota_data: Dict, items: List[Dict]) -> Optional[Dict]:
        """Crear nueva nota de proveedor"""
        try:
            db = self._get_session()
            nota = crud.create_nota_proveedor(db, nota_data, items)
            return self._nota_proveedor_to_dict(nota)
        except Exception as e:
            print(f"Error al crear nota proveedor: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def actualizar_nota_proveedor(self, nota_id: int, nota_data: Dict, items: List[Dict]) -> Optional[Dict]:
        """Actualizar nota de proveedor (lógica similar a actualizar_nota)"""
        try:
            db = self._get_session()
            nota = crud.get_nota_proveedor(db, nota_id)
            if not nota:
                print(f"❌ No se encontró la nota proveedor con ID {nota_id}")
                return None
            
            print(f"📝 Actualizando nota proveedor {nota.folio}...")
            
            # Actualizar datos
            nota.proveedor_id = nota_data.get('proveedor_id', nota.proveedor_id)
            nota.estado = nota_data.get('estado', nota.estado)
            nota.metodo_pago = nota_data.get('metodo_pago', nota.metodo_pago)
            nota.fecha = nota_data.get('fecha', nota.fecha)
            nota.observaciones = nota_data.get('observaciones', nota.observaciones)
            
            # Importar el modelo de item correcto
            from server.models import NotaProveedorItem
            
            # Eliminar items anteriores
            for item in nota.items:
                db.delete(item)
            db.flush()
            
            # Agregar nuevos items y calcular totales
            subtotal = 0
            total_impuestos = 0
            
            for item_data in items:
                cantidad = item_data['cantidad']
                precio_unitario = item_data['precio_unitario']
                impuesto_porcentaje = item_data.get('impuesto', 16.0)
                
                importe_sin_iva = cantidad * precio_unitario
                iva_item = importe_sin_iva * (impuesto_porcentaje / 100)
                
                nuevo_item = NotaProveedorItem(
                    nota_id=nota.id,
                    cantidad=cantidad,
                    descripcion=item_data['descripcion'],
                    precio_unitario=precio_unitario,
                    importe=importe_sin_iva,
                    impuesto=impuesto_porcentaje
                )
                
                db.add(nuevo_item)
                subtotal += importe_sin_iva
                total_impuestos += iva_item
            
            # Actualizar totales en la nota
            nota.subtotal = subtotal
            nota.impuestos = total_impuestos
            nota.total = subtotal + total_impuestos
            nota.saldo = nota.total - nota.total_pagado
            
            # Actualizar estado basado en saldo
            if nota.saldo <= 0.01 and nota.estado != 'Cancelada':
                nota.saldo = 0.0
                nota.estado = 'Pagado'
            elif nota.total_pagado > 0 and nota.estado != 'Cancelada':
                nota.estado = 'Pagado Parcialmente'
            elif nota.total_pagado == 0 and nota.estado != 'Cancelada':
                nota.estado = 'Registrado'

            nota.updated_at = datetime.now()
            
            db.commit()
            db.refresh(nota)
            
            print(f"✅ Nota proveedor {nota.folio} actualizada correctamente")
            return self._nota_proveedor_to_dict(nota)
            
        except Exception as e:
            print(f"❌ Error al actualizar nota proveedor: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return None
        
    def cancelar_nota_proveedor(self, nota_id: int) -> bool:
        """Cancelar una nota de proveedor"""
        try:
            db = self._get_session()
            return crud.cancelar_nota_proveedor(db, nota_id)
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

    # ==================== ESTADÍSTICAS ====================
    
    def get_reporte_ventas(self, fecha_ini: datetime, fecha_fin: datetime) -> List[Dict]:
        db = self._get_session()
        notas = crud.get_reporte_ventas_por_periodo(db, fecha_ini, fecha_fin)
        return [self._nota_to_dict(n) for n in notas]

    def get_reporte_servicios(self, fecha_ini: datetime, fecha_fin: datetime) -> List[Dict]:
        db = self._get_session()
        resultados = crud.get_reporte_servicios_mas_solicitados(db, fecha_ini, fecha_fin)
        # Convertir resultados de consulta (tuplas) a dict
        return [
            {'descripcion': r.descripcion, 'total_vendido': int(r.total_vendido)}
            for r in resultados
        ]

    def get_reporte_clientes(self, fecha_ini: datetime, fecha_fin: datetime) -> List[Dict]:
        db = self._get_session()
        resultados = crud.get_reporte_clientes_frecuentes(db, fecha_ini, fecha_fin)
        # Convertir resultados de consulta (tuplas) a dict
        return [
            {'cliente': r.nombre, 'total_notas': int(r.total_notas), 'monto_total': r.monto_total}
            for r in resultados
        ]

    def get_reporte_cuentas_por_cobrar(self) -> List[Dict]:
        db = self._get_session()
        notas = crud.get_reporte_cuentas_por_cobrar(db)
        return [self._nota_to_dict(n) for n in notas]
        
    def get_reporte_inventario_bajo_stock(self) -> List[Dict]:
        """Re-usando la función existente de inventario."""
        # Esta función ya existe en db_helper.py
        return self.get_productos_bajo_stock()
    
    # ==================== CONFIGURACIÓN EMPRESA ====================

    def get_config_empresa(self) -> Optional[Dict]:
        """Obtener configuración de la empresa"""
        try:
            from server.models import ConfigEmpresa
            
            db = self._get_session()
            config = db.query(ConfigEmpresa).first()
            
            if config:
                return {
                    'id': config.id,
                    'nombre_comercial': config.nombre_comercial,
                    'razon_social': config.razon_social,
                    'rfc': config.rfc,
                    'calle': config.calle,
                    'colonia': config.colonia,
                    'ciudad': config.ciudad,
                    'estado': config.estado,
                    'cp': config.cp,
                    'telefono1': config.telefono1,
                    'telefono2': config.telefono2,
                    'email': config.email,
                    'sitio_web': config.sitio_web,
                    'logo_path': config.logo_path
                }
            return None
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
                # Actualizar
                for key, value in datos.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
            else:
                # Crear nueva
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
            
            return [{
                'id': u.id,
                'username': u.username,
                'nombre_completo': u.nombre_completo,
                'email': u.email,
                'rol': u.rol,
                'activo': u.activo,
                'ultimo_acceso': u.ultimo_acceso.strftime('%Y-%m-%d %H:%M') if u.ultimo_acceso else ''
            } for u in usuarios]
        except Exception as e:
            print(f"Error get_usuarios: {e}")
            return []


    def get_usuario_by_id(self, usuario_id: int) -> Optional[Dict]:
        """Obtener usuario por ID"""
        try:
            from server.models import Usuario
            
            db = self._get_session()
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            
            if usuario:
                return {
                    'id': usuario.id,
                    'username': usuario.username,
                    'nombre_completo': usuario.nombre_completo,
                    'email': usuario.email,
                    'rol': usuario.rol,
                    'activo': usuario.activo
                }
            return None
        except Exception as e:
            print(f"Error get_usuario_by_id: {e}")
            return None


    def get_usuario_by_username(self, username: str) -> Optional[Dict]:
        """Obtener usuario por username (para login)"""
        try:
            from server.models import Usuario
            
            db = self._get_session()
            usuario = db.query(Usuario).filter(Usuario.username == username).first()
            
            if usuario:
                return {
                    'id': usuario.id,
                    'username': usuario.username,
                    'password_hash': usuario.password_hash,
                    'nombre_completo': usuario.nombre_completo,
                    'rol': usuario.rol,
                    'activo': usuario.activo
                }
            return None
        except Exception as e:
            print(f"Error get_usuario_by_username: {e}")
            return None


    def crear_usuario(self, datos: Dict) -> bool:
        """Crear nuevo usuario"""
        try:
            from server.models import Usuario
            
            db = self._get_session()
            
            # Verificar si ya existe
            existe = db.query(Usuario).filter(Usuario.username == datos['username']).first()
            if existe:
                return False
            
            # Hash de contraseña
            if 'password' in datos:
                datos['password_hash'] = self._generar_hash_password(datos['password'])
                del datos['password']
            
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
            
            # Hash de contraseña si se proporciona
            if 'password' in datos and datos['password']:
                datos['password_hash'] = self._generar_hash_password(datos['password'])
                del datos['password']
            elif 'password' in datos:
                del datos['password']
            
            for key, value in datos.items():
                if hasattr(usuario, key):
                    setattr(usuario, key, value)
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error actualizar_usuario: {e}")
            db.rollback()
            return False


    def eliminar_usuario(self, usuario_id: int, soft_delete: bool = True) -> bool:
        """Eliminar usuario (soft delete por defecto)"""
        try:
            from server.models import Usuario
            
            db = self._get_session()
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            
            if not usuario:
                return False
            
            if soft_delete:
                usuario.activo = False
                db.commit()
            else:
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
        
        if not usuario:
            return None
        
        if not usuario['activo']:
            return None
        
        password_hash = self._generar_hash_password(password)
        
        if usuario['password_hash'] == password_hash:
            # Actualizar último acceso
            try:
                from server.models import Usuario
                from datetime import datetime
                
                db = self._get_session()
                user = db.query(Usuario).filter(Usuario.id == usuario['id']).first()
                if user:
                    user.ultimo_acceso = datetime.now()
                    db.commit()
            except:
                pass
            
            return {
                'id': usuario['id'],
                'username': usuario['username'],
                'nombre_completo': usuario['nombre_completo'],
                'rol': usuario['rol']
            }
        
        return None
    
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
    def _orden_to_dict(orden) -> Dict:
        """Convertir Orden ORM a diccionario"""
        if not orden: return {}
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
            'fecha_recepcion': orden.fecha_recepcion,
            'nota_folio': orden.nota_folio or None,
            'items': [{'cantidad': i.cantidad, 'descripcion': i.descripcion} for i in orden.items],
            'observaciones': orden.observaciones or ''
        }
    
    @staticmethod
    def _cotizacion_to_dict(cotizacion) -> Dict:
        """Convertir Cotizacion ORM a diccionario"""
        if not cotizacion: return {}
        return {
            'id': cotizacion.id,
            'folio': cotizacion.folio,
            'cliente_id': cotizacion.cliente_id,
            'cliente_nombre': cotizacion.cliente.nombre,
            'estado': cotizacion.estado,
            'vigencia': cotizacion.vigencia,
            'subtotal': cotizacion.subtotal,
            'impuestos': cotizacion.impuestos,
            'total': cotizacion.total,
            'observaciones': cotizacion.observaciones or '',
            'created_at': cotizacion.created_at.strftime("%d/%m/%Y") if cotizacion.created_at else '',
            'nota_folio': cotizacion.nota_folio or None,
            'items': [{
                'cantidad': i.cantidad,
                'descripcion': i.descripcion,
                'precio_unitario': i.precio_unitario,
                'importe': i.importe,
                'impuesto': i.impuesto
            } for i in cotizacion.items]
        }
    
    @staticmethod
    def _nota_to_dict(nota) -> Dict:
        """Convertir NotaVenta ORM a diccionario"""
        
        if not nota:
            return None
            
        return {
            'id': nota.id,
            'folio': nota.folio,
            'cliente_id': nota.cliente_id,
            'cliente_nombre': nota.cliente.nombre if nota.cliente else 'Sin cliente',
            'estado': nota.estado or 'Registrado',
            
            'metodo_pago': nota.metodo_pago or 'Efectivo',
            'fecha': nota.fecha.strftime("%d/%m/%Y") if nota.fecha else '',
            'observaciones': nota.observaciones or '',
            'subtotal': nota.subtotal,
            'impuestos': nota.impuestos,
            'total': nota.total,
            'total_pagado': nota.total_pagado,
            'saldo': nota.saldo,
            'cotizacion_folio': nota.cotizacion_folio or None,
            'orden_folio': nota.orden_folio or None,
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
        
        if not nota:
            return None
            
        return {
            'id': nota.id,
            'folio': nota.folio,
            'proveedor_id': nota.proveedor_id,
            'proveedor_nombre': nota.proveedor.nombre if nota.proveedor else 'Sin proveedor',
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

# Instancia global para usar en toda la aplicación
db_helper = DatabaseHelper()