from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from server.models import (
    Cliente, Proveedor, Producto, MovimientoInventario,
    Orden, OrdenItem, Cotizacion, CotizacionItem,
    NotaVenta, NotaVentaItem, NotaVentaPago, Usuario,
    NotaProveedor, NotaProveedorItem, NotaProveedorPago
)


# ==================== CLIENTES ====================

def get_all_clientes(db: Session, activos_solo: bool = True) -> List[Cliente]:
    """Obtener todos los clientes"""
    query = db.query(Cliente)
    if activos_solo:
        query = query.filter(Cliente.activo == True)
    return query.order_by(Cliente.nombre).all()


def get_cliente(db: Session, cliente_id: int) -> Optional[Cliente]:
    """Obtener cliente por ID"""
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()


def get_cliente_by_nombre(db: Session, nombre: str) -> Optional[Cliente]:
    """Buscar cliente por nombre (búsqueda parcial)"""
    return db.query(Cliente).filter(
        Cliente.nombre.ilike(f"%{nombre}%")
    ).first()


def create_cliente(db: Session, cliente_data: Dict[str, Any]) -> Cliente:
    """Crear nuevo cliente"""
    nuevo_cliente = Cliente(**cliente_data)
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente


def update_cliente(db: Session, cliente_id: int, cliente_data: Dict[str, Any]) -> Optional[Cliente]:
    """Actualizar cliente existente"""
    cliente = get_cliente(db, cliente_id)
    if cliente:
        for key, value in cliente_data.items():
            setattr(cliente, key, value)
        cliente.updated_at = datetime.now()
        db.commit()
        db.refresh(cliente)
    return cliente


def delete_cliente(db: Session, cliente_id: int, soft_delete: bool = True) -> bool:
    """
    Eliminar cliente
    soft_delete=True: Solo marca como inactivo
    soft_delete=False: Elimina permanentemente
    """
    cliente = get_cliente(db, cliente_id)
    if cliente:
        if soft_delete:
            cliente.activo = False
            db.commit()
        else:
            db.delete(cliente)
            db.commit()
        return True
    return False


def search_clientes(db: Session, busqueda: str) -> List[Cliente]:
    """Buscar clientes por nombre, email o teléfono"""
    return db.query(Cliente).filter(
        or_(
            Cliente.nombre.ilike(f"%{busqueda}%"),
            Cliente.email.ilike(f"%{busqueda}%"),
            Cliente.telefono.ilike(f"%{busqueda}%")
        )
    ).all()


# ==================== PROVEEDORES ====================

def get_all_proveedores(db: Session, activos_solo: bool = True) -> List[Proveedor]:
    """Obtener todos los proveedores"""
    query = db.query(Proveedor)
    if activos_solo:
        query = query.filter(Proveedor.activo == True)
    return query.order_by(Proveedor.nombre).all()


def get_proveedor(db: Session, proveedor_id: int) -> Optional[Proveedor]:
    """Obtener proveedor por ID"""
    return db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()


def create_proveedor(db: Session, proveedor_data: Dict[str, Any]) -> Proveedor:
    """Crear nuevo proveedor"""
    nuevo_proveedor = Proveedor(**proveedor_data)
    db.add(nuevo_proveedor)
    db.commit()
    db.refresh(nuevo_proveedor)
    return nuevo_proveedor


def update_proveedor(db: Session, proveedor_id: int, proveedor_data: Dict[str, Any]) -> Optional[Proveedor]:
    """Actualizar proveedor existente"""
    proveedor = get_proveedor(db, proveedor_id)
    if proveedor:
        for key, value in proveedor_data.items():
            setattr(proveedor, key, value)
        proveedor.updated_at = datetime.now()
        db.commit()
        db.refresh(proveedor)
    return proveedor


def delete_proveedor(db: Session, proveedor_id: int, soft_delete: bool = True) -> bool:
    """Eliminar proveedor"""
    proveedor = get_proveedor(db, proveedor_id)
    if proveedor:
        if soft_delete:
            proveedor.activo = False
            db.commit()
        else:
            db.delete(proveedor)
            db.commit()
        return True
    return False

def search_proveedores(db: Session, busqueda: str) -> List[Proveedor]:
    """Buscar proveedores por nombre, email o teléfono"""
    return db.query(Proveedor).filter(
        or_(
            Proveedor.nombre.ilike(f"%{busqueda}%"),
            Proveedor.email.ilike(f"%{busqueda}%"),
            Proveedor.telefono.ilike(f"%{busqueda}%")
        )
    ).all()


# ==================== INVENTARIO ====================

def get_all_productos(db: Session, activos_solo: bool = True) -> List[Producto]:
    """Obtener todos los productos"""
    query = db.query(Producto)
    if activos_solo:
        query = query.filter(Producto.activo == True)
    return query.order_by(Producto.nombre).all()


def get_producto(db: Session, producto_id: int) -> Optional[Producto]:
    """Obtener producto por ID"""
    return db.query(Producto).filter(Producto.id == producto_id).first()


def get_producto_by_codigo(db: Session, codigo: str) -> Optional[Producto]:
    """Obtener producto por código"""
    return db.query(Producto).filter(Producto.codigo == codigo).first()


def create_producto(db: Session, producto_data: Dict[str, Any]) -> Producto:
    """Crear nuevo producto"""
    nuevo_producto = Producto(**producto_data)
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


def update_producto(db: Session, producto_id: int, producto_data: Dict[str, Any]) -> Optional[Producto]:
    """Actualizar producto existente"""
    producto = get_producto(db, producto_id)
    if producto:
        for key, value in producto_data.items():
            setattr(producto, key, value)
        producto.updated_at = datetime.now()
        db.commit()
        db.refresh(producto)
    return producto


def delete_producto(db: Session, producto_id: int, soft_delete: bool = True) -> bool:
    """Eliminar producto"""
    producto = get_producto(db, producto_id)
    if producto:
        if soft_delete:
            producto.activo = False
            db.commit()
        else:
            db.delete(producto)
            db.commit()
        return True
    return False


def get_productos_bajo_stock(db: Session) -> List[Producto]:
    """Obtener productos con stock bajo (stock_actual <= stock_min)"""
    return db.query(Producto).filter(
        Producto.stock_actual <= Producto.stock_min
    ).all()


def get_productos_sin_stock(db: Session) -> List[Producto]:
    """Obtener productos sin stock"""
    return db.query(Producto).filter(Producto.stock_actual == 0).all()


def search_productos(db: Session, busqueda: str) -> List[Producto]:
    """Buscar productos por código, nombre o categoría"""
    return db.query(Producto).filter(
        or_(
            Producto.codigo.ilike(f"%{busqueda}%"),
            Producto.nombre.ilike(f"%{busqueda}%"),
            Producto.categoria.ilike(f"%{busqueda}%")
        )
    ).all()


# ==================== MOVIMIENTOS DE INVENTARIO ====================

def registrar_movimiento_inventario(
    db: Session,
    producto_id: int,
    tipo: str,  # "Entrada" o "Salida"
    cantidad: int,
    motivo: str,
    usuario: str
) -> Optional[MovimientoInventario]:
    """
    Registrar movimiento de inventario y actualizar stock
    """
    producto = get_producto(db, producto_id)
    if not producto:
        return None
    
    # Actualizar stock
    if tipo == "Entrada":
        producto.stock_actual += cantidad
    elif tipo == "Salida":
        if producto.stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {producto.stock_actual}")
        producto.stock_actual -= cantidad
    else:
        raise ValueError("Tipo de movimiento inválido. Use 'Entrada' o 'Salida'")
    
    # Crear movimiento
    movimiento = MovimientoInventario(
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo,
        usuario=usuario
    )
    
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    db.refresh(producto)
    
    return movimiento


def get_movimientos_inventario(
    db: Session,
    producto_id: Optional[int] = None,
    tipo: Optional[str] = None,
    limit: int = 100
) -> List[MovimientoInventario]:
    """Obtener historial de movimientos"""
    query = db.query(MovimientoInventario)
    
    if producto_id:
        query = query.filter(MovimientoInventario.producto_id == producto_id)
    if tipo:
        query = query.filter(MovimientoInventario.tipo == tipo)
    
    return query.order_by(MovimientoInventario.created_at.desc()).limit(limit).all()


# ==================== ÓRDENES DE TRABAJO ====================

def get_all_ordenes(db: Session, estado: Optional[str] = None) -> List[Orden]:
    """Obtener todas las órdenes (opcional: filtrar por estado)"""
    query = db.query(Orden).options(
        joinedload(Orden.cliente), 
        joinedload(Orden.items)
    )
    if estado:
        query = query.filter(Orden.estado == estado)
    return query.order_by(Orden.created_at.desc()).all()


def get_orden(db: Session, orden_id: int) -> Optional[Orden]:
    """Obtener orden por ID con sus items"""
    return db.query(Orden).filter(Orden.id == orden_id).first()


def get_orden_by_folio(db: Session, folio: str) -> Optional[Orden]:
    """Obtener orden por folio"""
    return db.query(Orden).filter(Orden.folio == folio).first()

def search_ordenes_by_folio(db: Session, folio: str) -> List[Orden]:
    """Buscar órdenes por folio (búsqueda parcial)"""
    return db.query(Orden).options(
        joinedload(Orden.cliente),
        joinedload(Orden.items)
    ).filter(
        Orden.folio.ilike(f"%{folio}%")
    ).order_by(Orden.created_at.desc()).all()


def create_orden(db: Session, orden_data: Dict[str, Any], items: List[Dict[str, Any]]) -> Orden:
    """Crear nueva orden de trabajo con items"""
    # Generar folio único si no existe
    if 'folio' not in orden_data:
        ultimo_folio = db.query(Orden).order_by(Orden.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        orden_data['folio'] = f"ORD-{datetime.now().year}-{numero:05d}"
    
    # Crear orden
    nueva_orden = Orden(**orden_data)
    db.add(nueva_orden)
    db.flush()  # Obtener ID sin commit
    
    # Agregar items
    for item_data in items:
        item = OrdenItem(orden_id=nueva_orden.id, **item_data)
        db.add(item)
    
    db.commit()
    db.refresh(nueva_orden)
    return nueva_orden


def update_orden(
    db: Session, 
    orden_id: int, 
    orden_data: Dict[str, Any], 
    items: Optional[List[Dict[str, Any]]] = None
) -> Optional[Orden]:
    orden = get_orden(db, orden_id)
    if not orden:
        return None

    if orden.estado == 'Cancelada':
        raise ValueError("No se puede modificar una orden cancelada.")

    if orden.nota_folio and 'nota_folio' not in orden_data:
        raise ValueError(f"Orden ligada a la nota {orden.nota_folio}, no se puede modificar.")

    for key, value in orden_data.items():
        if hasattr(orden, key):
            setattr(orden, key, value)
    
    if items is not None:
        db.query(OrdenItem).filter(OrdenItem.orden_id == orden_id).delete()
        
        for item_data in items:
            item = OrdenItem(orden_id=orden.id, **item_data)
            db.add(item)
    
    orden.updated_at = datetime.now()
    
    db.commit()
    db.refresh(orden)
    return orden


def cambiar_estado_orden(db: Session, orden_id: int, nuevo_estado: str) -> Optional[Orden]:
    """Cambiar estado de orden"""
    orden = get_orden(db, orden_id)
    if orden:
        orden.estado = nuevo_estado
        if nuevo_estado == "Completada" and not orden.fecha_entrega:
            orden.fecha_entrega = datetime.now()
        orden.updated_at = datetime.now()
        db.commit()
        db.refresh(orden)
    return orden


def delete_orden(db: Session, orden_id: int) -> bool:
    """Eliminar orden (también elimina items por cascade)"""
    orden = get_orden(db, orden_id)
    if orden:
        db.delete(orden)
        db.commit()
        return True
    return False


# ==================== COTIZACIONES ====================

def get_all_cotizaciones(db: Session, estado: Optional[str] = None) -> List[Cotizacion]:
    """Obtener todas las cotizaciones"""
    query = db.query(Cotizacion).options(
        joinedload(Cotizacion.cliente), 
        joinedload(Cotizacion.items)
    )
    if estado:
        query = query.filter(Cotizacion.estado == estado)
    return query.order_by(Cotizacion.created_at.desc()).all()

def search_cotizaciones(db: Session, folio: Optional[str] = None, cliente_id: Optional[int] = None) -> List[Cotizacion]:
    """Buscar cotizaciones por folio o cliente_id"""
    query = db.query(Cotizacion).options(joinedload(Cotizacion.cliente))
    if folio:
        query = query.filter(Cotizacion.folio.ilike(f"%{folio}%"))
    if cliente_id:
        query = query.filter(Cotizacion.cliente_id == cliente_id)
    return query.order_by(Cotizacion.created_at.desc()).all()

def get_cotizacion(db: Session, cotizacion_id: int) -> Optional[Cotizacion]:
    """Obtener cotización por ID"""
    return db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id).first()

def search_cotizaciones_by_folio(db: Session, folio: str) -> List[Cotizacion]:
    """Buscar cotizaciones por folio (búsqueda parcial)"""
    return db.query(Cotizacion).options(
        joinedload(Cotizacion.cliente),
        joinedload(Cotizacion.items)
    ).filter(
        Cotizacion.folio.ilike(f"%{folio}%")
    ).order_by(Cotizacion.created_at.desc()).all()


def create_cotizacion(db: Session, cotizacion_data: Dict[str, Any], items: List[Dict[str, Any]]) -> Cotizacion:
    """Crear nueva cotización con items"""
    # Generar folio único si no existe
    if 'folio' not in cotizacion_data:
        ultimo_folio = db.query(Cotizacion).order_by(Cotizacion.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        cotizacion_data['folio'] = f"COT-{datetime.now().year}-{numero:05d}"
    
    # Crear cotización
    nueva_cotizacion = Cotizacion(**cotizacion_data)
    db.add(nueva_cotizacion)
    db.flush()
    
    # Agregar items y calcular totales
    subtotal = 0
    impuestos_total = 0
    
    for item_data in items:
        item = CotizacionItem(cotizacion_id=nueva_cotizacion.id, **item_data)
        db.add(item)
        subtotal += item.importe
        impuestos_total += (item.importe * item.impuesto / 100)
    
    nueva_cotizacion.subtotal = subtotal
    nueva_cotizacion.impuestos = impuestos_total
    nueva_cotizacion.total = subtotal + impuestos_total
    
    db.commit()
    db.refresh(nueva_cotizacion)
    return nueva_cotizacion


def update_cotizacion(
    db: Session, 
    cotizacion_id: int, 
    cotizacion_data: Dict[str, Any], 
    items: List[Dict[str, Any]],
    nota_folio: Optional[str] = None
) -> Optional[Cotizacion]:
    """
    Actualizar una cotización existente.
    Borrará los items anteriores y los reemplazará.
    """
    # Usamos get_cotizacion (que ya debe cargar 'items' y 'cliente' por las correcciones anteriores)
    cotizacion = get_cotizacion(db, cotizacion_id)
    if not cotizacion:
        return None

    if cotizacion.estado == 'Cancelada':
            raise ValueError("No se puede modificar una cotización Cancelada.")

    # 1. Actualizar datos de la cotización
    for key, value in cotizacion_data.items():
        if hasattr(cotizacion, key):
            setattr(cotizacion, key, value)
    
    # 1.b. Actualizar el nota_folio si se proveyó (para "Generar Nota")
    if nota_folio:
        cotizacion.nota_folio = nota_folio
        cotizacion.estado = 'Aceptada' # Marcar como Aceptada

    # 2. Borrar items viejos
    db.query(CotizacionItem).filter(CotizacionItem.cotizacion_id == cotizacion_id).delete()
    
    # 3. Agregar items nuevos y recalcular totales
    subtotal = 0
    impuestos_total = 0
    
    for item_data in items:
        # Aseguramos que los items tengan los campos correctos
        item_data_limpia = {
            'cantidad': item_data.get('cantidad', 0),
            'descripcion': item_data.get('descripcion', 'N/A'),
            'precio_unitario': item_data.get('precio_unitario', 0),
            'importe': item_data.get('importe', 0),
            'impuesto': item_data.get('impuesto', 0)
        }
        item = CotizacionItem(cotizacion_id=cotizacion.id, **item_data_limpia)
        db.add(item)
        subtotal += item_data_limpia.get('importe', 0)
        impuestos_total += (item_data_limpia.get('importe', 0) * item_data_limpia.get('impuesto', 0) / 100)
    
    cotizacion.subtotal = subtotal
    cotizacion.impuestos = impuestos_total
    cotizacion.total = subtotal + impuestos_total
    
    cotizacion.updated_at = datetime.now()
    
    db.commit()
    db.refresh(cotizacion)
    return cotizacion


def delete_cotizacion(db: Session, cotizacion_id: int) -> bool:
    """Eliminar cotización"""
    cotizacion = get_cotizacion(db, cotizacion_id)
    if cotizacion:
        db.delete(cotizacion)
        db.commit()
        return True
    return False

def cancelar_cotizacion(db: Session, cotizacion_id: int) -> bool:
    """Cancelar una cotización"""
    cotizacion = get_cotizacion(db, cotizacion_id)
    if not cotizacion:
        return False
    
    if cotizacion.estado == 'Cancelada':
        return False
    
    cotizacion.estado = 'Cancelada'
    cotizacion.updated_at = datetime.now()
    db.commit()
    return True

# ==================== NOTAS DE VENTA ====================

def get_all_notas(db: Session, estado: Optional[str] = None) -> List[NotaVenta]:
    """Obtener todas las notas de venta"""
    query = db.query(NotaVenta)
    if estado:
        query = query.filter(NotaVenta.estado == estado)
    return query.order_by(NotaVenta.fecha.desc()).all()


def get_nota(db: Session, nota_id: int) -> Optional[NotaVenta]:
    """Obtener nota por ID"""
    return db.query(NotaVenta).filter(NotaVenta.id == nota_id).first()


def create_nota_venta(db: Session, nota_data: Dict[str, Any], items: List[Dict[str, Any]], estado: Optional[str] = 'Registrado') -> NotaVenta:
    """Crear nueva nota de venta con items"""
    # Generar folio único si no existe
    if 'folio' not in nota_data:
        ultimo_folio = db.query(NotaVenta).order_by(NotaVenta.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        nota_data['folio'] = f"NV-{datetime.now().year}-{numero:05d}"
    
    nota_data['estado'] = estado
    nota_data['total_pagado'] = 0.0
    # Crear nota
    nueva_nota = NotaVenta(**nota_data)
    db.add(nueva_nota)
    db.flush()
    
    # Agregar items y calcular totales
    subtotal = 0
    impuestos_total = 0
    
    for item_data in items:
        item = NotaVentaItem(nota_id=nueva_nota.id, **item_data)
        db.add(item)
        subtotal += item.importe
        impuestos_total += (item.importe * item.impuesto / 100)
    
    nueva_nota.subtotal = subtotal
    nueva_nota.impuestos = impuestos_total
    nueva_nota.total = subtotal + impuestos_total
    nueva_nota.saldo = nueva_nota.total
    
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota

def update_nota_venta(
    db: Session, 
    nota_id: int, 
    nota_data: Dict[str, Any], 
    items: List[Dict[str, Any]]
) -> Optional[NotaVenta]:
    """
    Actualizar una nota de venta existente.
    Esto borrará los items anteriores y los reemplazará.
    """
    nota = get_nota(db, nota_id)
    if not nota:
        return None
    
    if nota.estado == 'Cancelada' or nota.estado == 'Pagado':
        raise ValueError("No se puede modificar una nota Pagada o Cancelada.")
    
    # 1. Actualizar datos de la nota
    for key, value in nota_data.items():
        if hasattr(nota, key):
            setattr(nota, key, value)
    
    # 2. Borrar items viejos
    db.query(NotaVentaItem).filter(NotaVentaItem.nota_id == nota_id).delete()
    
    # 3. Agregar items nuevos y recalcular totales
    subtotal = 0
    impuestos_total = 0
    
    for item_data in items:
        item = NotaVentaItem(nota_id=nota.id, **item_data)
        db.add(item)
        subtotal += item.importe
        impuestos_total += (item.importe * item.impuesto / 100)
    
    nota.subtotal = subtotal
    nota.impuestos = impuestos_total
    nota.total = subtotal + impuestos_total
    
    # 4. Recalcular saldo
    # (No se debe tocar el total_pagado, solo recalcular el saldo)
    nota.saldo = nota.total - nota.total_pagado
    
    # 5. Re-evaluar estado (si el nuevo total es menor que lo pagado)
    if nota.saldo <= 0.01:
        nota.saldo = 0.0
        nota.estado = 'Pagado'
    elif nota.total_pagado > 0:
        nota.estado = 'Pagado Parcialmente'
    else:
        nota.estado = 'Registrado'
        
    nota.updated_at = datetime.now()
    
    db.commit()
    db.refresh(nota)
    return nota

def cancelar_nota(db: Session, nota_id: int) -> bool:
    """Cancelar una nota de venta"""
    nota = get_nota(db, nota_id)
    if not nota:
        return False
    
    # Solo se puede cancelar si no está pagada.
    if nota.estado == 'Pagado' or nota.estado == 'Cancelada':
        return False  # No se puede cancelar una nota pagada o ya cancelada
    
    nota.estado = 'Cancelada'
    nota.saldo = 0.0 # Al cancelar, el saldo pendiente es 0
    nota.updated_at = datetime.now()
    db.commit()
    return True

def get_pagos_por_nota(db: Session, nota_id: int) -> List[NotaVentaPago]:
    """Obtener historial de pagos de una nota"""
    return db.query(NotaVentaPago).filter(NotaVentaPago.nota_id == nota_id).order_by(NotaVentaPago.fecha_pago.desc()).all()


def registrar_pago_nota(
    db: Session, 
    nota_id: int, 
    monto: float, 
    fecha_pago: datetime, 
    metodo_pago: str, 
    memo: Optional[str] = None
) -> Optional[NotaVenta]:
    """
    Registrar un pago o abono a una nota de venta y actualizar su estado.
    """
    nota = get_nota(db, nota_id)
    if not nota:
        raise ValueError("La nota de venta no existe.")
    
    if nota.estado == 'Cancelada':
        raise ValueError("No se pueden aplicar pagos a una nota cancelada.")
        
    if nota.estado == 'Pagado':
        raise ValueError("Esta nota ya ha sido liquidada.")
        
    if monto <= 0:
        raise ValueError("El monto debe ser positivo.")
        
    # Usar una tolerancia de 0.01 (un centavo) para comparaciones de punto flotante
    if monto > (nota.saldo + 0.01):
        raise ValueError(f"El monto ${monto} excede el saldo pendiente de ${nota.saldo:.2f}.")
    
    # 1. Registrar el pago
    nuevo_pago = NotaVentaPago(
        nota_id=nota_id,
        monto=monto,
        fecha_pago=fecha_pago,
        metodo_pago=metodo_pago,
        memo=memo
    )
    db.add(nuevo_pago)
    
    # 2. Actualizar la nota
    nota.total_pagado += monto
    nota.saldo -= monto
    
    # 3. Actualizar estado de la nota (Cumpliendo Punto 7 de tus requisitos)
    if nota.saldo <= 0.01:
        nota.saldo = 0.0  # Forzar a 0 exacto si se liquida
        nota.estado = 'Pagado'
    else:
        nota.estado = 'Pagado Parcialmente'
        
    nota.updated_at = datetime.now()
    
    db.commit()
    db.refresh(nota)
    
    return nota

def get_pago_by_id(db: Session, pago_id: int) -> Optional[NotaVentaPago]:
    """Obtener un pago específico por su ID"""
    return db.query(NotaVentaPago).filter(NotaVentaPago.id == pago_id).first()

def eliminar_pago_nota(db: Session, pago_id: int) -> Optional[NotaVenta]:
    """
    Elimina un registro de pago y revierte los cambios en la Nota de Venta.
    """
    # 1. Buscar el pago
    pago = get_pago_by_id(db, pago_id)
    if not pago:
        raise ValueError("El pago no existe.")

    # 2. Buscar la nota principal
    nota = get_nota(db, pago.nota_id)
    if not nota:
        raise ValueError("La nota asociada no existe.")
        
    if nota.estado == 'Cancelada':
        raise ValueError("No se puede modificar o revertir pagos de una nota cancelada.")

    # 3. Revertir los montos en la nota
    monto_pago = pago.monto
    nota.total_pagado -= monto_pago
    nota.saldo += monto_pago

    # 4. Re-evaluar el estado de la nota
    # Tolerancia para floats
    if nota.total_pagado <= 0.01:
        # Si el estado era 'Borrador', no debe cambiar a 'Registrado'
        if nota.estado != 'Borrador':
            nota.estado = 'Registrado'
            
        nota.total_pagado = 0.0 # Asegurar 0
        nota.saldo = nota.total # Asegurar saldo completo
    else:
        nota.estado = 'Pagado Parcialmente'
        
    # 5. Eliminar el pago
    db.delete(pago)
    
    # 6. Guardar cambios
    db.commit()
    db.refresh(nota)
    
    return nota

# ==================== NOTAS DE PROVEEDOR ====================

def get_all_notas_proveedor(db: Session) -> List[NotaProveedor]:
    """Obtener todas las notas de proveedor"""
    return db.query(NotaProveedor).order_by(NotaProveedor.fecha.desc()).all()


def get_nota_proveedor(db: Session, nota_id: int) -> Optional[NotaProveedor]:
    """Obtener nota de proveedor por ID"""
    return db.query(NotaProveedor).filter(NotaProveedor.id == nota_id).first()

def search_notas_proveedor_by_folio(db: Session, folio: str) -> List[NotaProveedor]:
    """Buscar notas de proveedor por folio (búsqueda parcial)"""
    return db.query(NotaProveedor).options(
        joinedload(NotaProveedor.proveedor)
    ).filter(
        NotaProveedor.folio.ilike(f"%{folio}%")
    ).order_by(NotaProveedor.fecha.desc()).all()

def create_nota_proveedor(db: Session, nota_data: Dict[str, Any], items: List[Dict[str, Any]]) -> NotaProveedor:
    """Crear nueva nota de proveedor con items"""
    # Generar folio único si no existe
    if 'folio' not in nota_data:
        ultimo_folio = db.query(NotaProveedor).order_by(NotaProveedor.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        nota_data['folio'] = f"NP-{datetime.now().year}-{numero:05d}"
    
    nota_data['estado'] = 'Registrado'
    nota_data['total_pagado'] = 0.0
    
    # Crear nota
    nueva_nota = NotaProveedor(**nota_data)
    db.add(nueva_nota)
    db.flush()
    
    # Agregar items y calcular totales
    subtotal = 0
    impuestos_total = 0
    
    for item_data in items:
        item = NotaProveedorItem(nota_id=nueva_nota.id, **item_data)
        db.add(item)
        subtotal += item.importe
        impuestos_total += (item.importe * item.impuesto / 100)
    
    nueva_nota.subtotal = subtotal
    nueva_nota.impuestos = impuestos_total
    nueva_nota.total = subtotal + impuestos_total
    nueva_nota.saldo = nueva_nota.total
    
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota

def update_nota_proveedor(
    db: Session, 
    nota_id: int, 
    nota_data: Dict[str, Any], 
    items: List[Dict[str, Any]]
) -> Optional[NotaProveedor]:
    """
    Actualizar una nota de proveedor existente.
    """
    nota = get_nota_proveedor(db, nota_id)
    if not nota:
        return None
    
    if nota.estado == 'Cancelada' or nota.estado == 'Pagado':
        raise ValueError("No se puede modificar una nota Pagada o Cancelada.")
    
    # 1. Actualizar datos de la nota
    for key, value in nota_data.items():
        if hasattr(nota, key):
            setattr(nota, key, value)
    
    # 2. Borrar items viejos
    db.query(NotaProveedorItem).filter(NotaProveedorItem.nota_id == nota_id).delete()
    
    # 3. Agregar items nuevos y recalcular totales
    subtotal = 0
    impuestos_total = 0
    
    for item_data in items:
        item = NotaProveedorItem(nota_id=nota.id, **item_data)
        db.add(item)
        subtotal += item.importe
        impuestos_total += (item.importe * item.impuesto / 100)
    
    nota.subtotal = subtotal
    nota.impuestos = impuestos_total
    nota.total = subtotal + impuestos_total
    
    # 4. Recalcular saldo
    nota.saldo = nota.total - nota.total_pagado
    
    # 5. Re-evaluar estado
    if nota.saldo <= 0.01:
        nota.saldo = 0.0
        nota.estado = 'Pagado'
    elif nota.total_pagado > 0:
        nota.estado = 'Pagado Parcialmente'
    else:
        nota.estado = 'Registrado'
        
    nota.updated_at = datetime.now()
    
    db.commit()
    db.refresh(nota)
    return nota


def create_nota_proveedor(db: Session, nota_data: Dict[str, Any], items: List[Dict[str, Any]]) -> NotaProveedor:
    """Crear nueva nota de proveedor con items"""
    # Generar folio único si no existe
    if 'folio' not in nota_data:
        ultimo_folio = db.query(NotaProveedor).order_by(NotaProveedor.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        nota_data['folio'] = f"NP-{datetime.now().year}-{numero:05d}"
    
    nota_data['estado'] = 'Registrado'
    nota_data['total_pagado'] = 0.0
    
    # Crear nota
    nueva_nota = NotaProveedor(**nota_data)
    db.add(nueva_nota)
    db.flush()
    
    # Agregar items y calcular totales
    subtotal = 0
    impuestos_total = 0
    
    for item_data in items:
        item = NotaProveedorItem(nota_id=nueva_nota.id, **item_data)
        db.add(item)
        subtotal += item.importe
        impuestos_total += (item.importe * item.impuesto / 100)
    
    nueva_nota.subtotal = subtotal
    nueva_nota.impuestos = impuestos_total
    nueva_nota.total = subtotal + impuestos_total
    nueva_nota.saldo = nueva_nota.total
    
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota

def cancelar_nota_proveedor(db: Session, nota_id: int) -> bool:
    """Cancelar una nota de proveedor"""
    nota = get_nota_proveedor(db, nota_id)
    if not nota:
        return False
    
    if nota.estado == 'Pagado' or nota.estado == 'Cancelada':
        return False
    
    nota.estado = 'Cancelada'
    nota.saldo = 0.0
    nota.updated_at = datetime.now()
    db.commit()
    return True

def get_pagos_por_nota_proveedor(db: Session, nota_id: int) -> List[NotaProveedorPago]:
    """Obtener historial de pagos de una nota de proveedor"""
    return db.query(NotaProveedorPago).filter(NotaProveedorPago.nota_id == nota_id).order_by(NotaProveedorPago.fecha_pago.desc()).all()


def registrar_pago_nota_proveedor(
    db: Session, 
    nota_id: int, 
    monto: float, 
    fecha_pago: datetime, 
    metodo_pago: str, 
    memo: Optional[str] = None
) -> Optional[NotaProveedor]:
    """
    Registrar un pago a una nota de proveedor y actualizar su estado.
    """
    nota = get_nota_proveedor(db, nota_id)
    if not nota:
        raise ValueError("La nota de proveedor no existe.")
    
    if nota.estado == 'Cancelada':
        raise ValueError("No se pueden aplicar pagos a una nota cancelada.")
        
    if nota.estado == 'Pagado':
        raise ValueError("Esta nota ya ha sido liquidada.")
        
    if monto <= 0:
        raise ValueError("El monto debe ser positivo.")
        
    if monto > (nota.saldo + 0.01):
        raise ValueError(f"El monto ${monto} excede el saldo pendiente de ${nota.saldo:.2f}.")
    
    # 1. Registrar el pago
    nuevo_pago = NotaProveedorPago(
        nota_id=nota_id,
        monto=monto,
        fecha_pago=fecha_pago,
        metodo_pago=metodo_pago,
        memo=memo
    )
    db.add(nuevo_pago)
    
    # 2. Actualizar la nota
    nota.total_pagado += monto
    nota.saldo -= monto
    
    # 3. Actualizar estado de la nota
    if nota.saldo <= 0.01:
        nota.saldo = 0.0
        nota.estado = 'Pagado'
    else:
        nota.estado = 'Pagado Parcialmente'
        
    nota.updated_at = datetime.now()
    
    db.commit()
    db.refresh(nota)
    
    return nota

def get_pago_proveedor_by_id(db: Session, pago_id: int) -> Optional[NotaProveedorPago]:
    """Obtener un pago a proveedor específico por su ID"""
    return db.query(NotaProveedorPago).filter(NotaProveedorPago.id == pago_id).first()

def eliminar_pago_nota_proveedor(db: Session, pago_id: int) -> Optional[NotaProveedor]:
    """
    Elimina un registro de pago a proveedor y revierte los cambios en la Nota de Proveedor.
    """
    # 1. Buscar el pago
    pago = get_pago_proveedor_by_id(db, pago_id)
    if not pago:
        raise ValueError("El pago no existe.")

    # 2. Buscar la nota principal
    nota = get_nota_proveedor(db, pago.nota_id)
    if not nota:
        raise ValueError("La nota asociada no existe.")
        
    if nota.estado == 'Cancelada':
        raise ValueError("No se puede modificar o revertir pagos de una nota cancelada.")

    # 3. Revertir los montos en la nota
    monto_pago = pago.monto
    nota.total_pagado -= monto_pago
    nota.saldo += monto_pago

    # 4. Re-evaluar el estado de la nota
    if nota.total_pagado <= 0.01:
        nota.estado = 'Registrado'
        nota.total_pagado = 0.0
        nota.saldo = nota.total
    else:
        nota.estado = 'Pagado Parcialmente'
        
    # 5. Eliminar el pago
    db.delete(pago)
    
    # 6. Guardar cambios
    db.commit()
    db.refresh(nota)
    
    return nota

# ==================== USUARIOS ====================

def get_usuario_by_username(db: Session, username: str) -> Optional[Usuario]:
    """Obtener usuario por username"""
    return db.query(Usuario).filter(Usuario.username == username).first()


def verificar_credenciales(db: Session, username: str, password: str) -> Optional[Usuario]:
    """
    Verificar credenciales de usuario
    NOTA: Por ahora usa hash simple, en producción usar bcrypt
    """
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    usuario = db.query(Usuario).filter(
        and_(
            Usuario.username == username,
            Usuario.password_hash == password_hash,
            Usuario.activo == True
        )
    ).first()
    
    if usuario:
        usuario.ultimo_acceso = datetime.now()
        db.commit()
    
    return usuario


def create_usuario(db: Session, usuario_data: Dict[str, Any]) -> Usuario:
    """Crear nuevo usuario"""
    import hashlib
    
    # Hash del password
    if 'password' in usuario_data:
        password = usuario_data.pop('password')
        usuario_data['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
    
    nuevo_usuario = Usuario(**usuario_data)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


# ==================== ESTADÍSTICAS Y REPORTES ====================

def get_reporte_ventas_por_periodo(db: Session, fecha_ini: datetime, fecha_fin: datetime) -> List[NotaVenta]:
    """Obtiene notas de venta (no canceladas) dentro de un rango de fechas."""
    return db.query(NotaVenta).filter(
        NotaVenta.fecha.between(fecha_ini, fecha_fin),
        NotaVenta.estado != 'Cancelada'
    ).order_by(NotaVenta.fecha.asc()).all()

def get_reporte_servicios_mas_solicitados(db: Session, fecha_ini: datetime, fecha_fin: datetime) -> List[Any]:
    """Obtiene servicios (items de nota) más vendidos por cantidad en un periodo."""
    return db.query(
        NotaVentaItem.descripcion,
        func.sum(NotaVentaItem.cantidad).label('total_vendido')
    ).join(NotaVenta, NotaVenta.id == NotaVentaItem.nota_id).filter(
        NotaVenta.fecha.between(fecha_ini, fecha_fin),
        NotaVenta.estado != 'Cancelada'
    ).group_by(NotaVentaItem.descripcion).order_by(
        func.sum(NotaVentaItem.cantidad).desc()
    ).limit(100).all()

def get_reporte_clientes_frecuentes(db: Session, fecha_ini: datetime, fecha_fin: datetime) -> List[Any]:
    """Obtiene clientes con más compras (por monto total) en el periodo."""
    return db.query(
        Cliente.nombre,
        func.count(NotaVenta.id).label('total_notas'),
        func.sum(NotaVenta.total).label('monto_total')
    ).join(NotaVenta, Cliente.id == NotaVenta.cliente_id).filter(
        NotaVenta.fecha.between(fecha_ini, fecha_fin),
        NotaVenta.estado != 'Cancelada'
    ).group_by(Cliente.nombre).order_by(
        func.sum(NotaVenta.total).desc()
    ).limit(100).all()

def get_reporte_cuentas_por_cobrar(db: Session) -> List[NotaVenta]:
    """Obtiene todas las notas de venta con saldo pendiente (no canceladas)."""
    return db.query(NotaVenta).filter(
        NotaVenta.saldo > 0.01,
        NotaVenta.estado != 'Cancelada'
    ).order_by(NotaVenta.fecha.asc()).all()