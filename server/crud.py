"""
CRUD Operations - Sistema de Taller Automotriz
Día 2: 20 Octubre 2025

Funciones para Create, Read, Update, Delete de todas las entidades
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from server.models import (
    Cliente, Proveedor, Producto, MovimientoInventario,
    Orden, OrdenItem, Cotizacion, CotizacionItem,
    NotaVenta, NotaVentaItem, Usuario
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
    query = db.query(Orden)
    if estado:
        query = query.filter(Orden.estado == estado)
    return query.order_by(Orden.created_at.desc()).all()


def get_orden(db: Session, orden_id: int) -> Optional[Orden]:
    """Obtener orden por ID con sus items"""
    return db.query(Orden).filter(Orden.id == orden_id).first()


def get_orden_by_folio(db: Session, folio: str) -> Optional[Orden]:
    """Obtener orden por folio"""
    return db.query(Orden).filter(Orden.folio == folio).first()


def create_orden(db: Session, orden_data: Dict[str, Any], items: List[Dict[str, Any]]) -> Orden:
    """Crear nueva orden de trabajo con items"""
    # Generar folio único si no existe
    if 'folio' not in orden_data:
        ultimo_folio = db.query(Orden).order_by(Orden.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        orden_data['folio'] = f"ORD-{datetime.now().year}-{numero:04d}"
    
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


def update_orden(db: Session, orden_id: int, orden_data: Dict[str, Any]) -> Optional[Orden]:
    """Actualizar orden existente"""
    orden = get_orden(db, orden_id)
    if orden:
        for key, value in orden_data.items():
            setattr(orden, key, value)
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
    query = db.query(Cotizacion)
    if estado:
        query = query.filter(Cotizacion.estado == estado)
    return query.order_by(Cotizacion.created_at.desc()).all()


def get_cotizacion(db: Session, cotizacion_id: int) -> Optional[Cotizacion]:
    """Obtener cotización por ID"""
    return db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id).first()


def create_cotizacion(db: Session, cotizacion_data: Dict[str, Any], items: List[Dict[str, Any]]) -> Cotizacion:
    """Crear nueva cotización con items"""
    # Generar folio único si no existe
    if 'folio' not in cotizacion_data:
        ultimo_folio = db.query(Cotizacion).order_by(Cotizacion.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        cotizacion_data['folio'] = f"COT-{datetime.now().year}-{numero:04d}"
    
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


def update_cotizacion(db: Session, cotizacion_id: int, cotizacion_data: Dict[str, Any]) -> Optional[Cotizacion]:
    """Actualizar cotización existente"""
    cotizacion = get_cotizacion(db, cotizacion_id)
    if cotizacion:
        for key, value in cotizacion_data.items():
            setattr(cotizacion, key, value)
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


# ==================== NOTAS DE VENTA ====================

def get_all_notas(db: Session) -> List[NotaVenta]:
    """Obtener todas las notas de venta"""
    return db.query(NotaVenta).order_by(NotaVenta.fecha.desc()).all()


def get_nota(db: Session, nota_id: int) -> Optional[NotaVenta]:
    """Obtener nota por ID"""
    return db.query(NotaVenta).filter(NotaVenta.id == nota_id).first()


def create_nota_venta(db: Session, nota_data: Dict[str, Any], items: List[Dict[str, Any]]) -> NotaVenta:
    """Crear nueva nota de venta con items"""
    # Generar folio único si no existe
    if 'folio' not in nota_data:
        ultimo_folio = db.query(NotaVenta).order_by(NotaVenta.id.desc()).first()
        numero = 1 if not ultimo_folio else ultimo_folio.id + 1
        nota_data['folio'] = f"NV-{datetime.now().year}-{numero:05d}"
    
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
    
    db.commit()
    db.refresh(nueva_nota)
    return nueva_nota


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

def get_estadisticas_dashboard(db: Session) -> Dict[str, Any]:
    """Obtener estadísticas para dashboard"""
    return {
        'total_clientes': db.query(Cliente).filter(Cliente.activo == True).count(),
        'total_proveedores': db.query(Proveedor).filter(Proveedor.activo == True).count(),
        'total_productos': db.query(Producto).filter(Producto.activo == True).count(),
        'productos_bajo_stock': db.query(Producto).filter(
            Producto.stock_actual <= Producto.stock_min
        ).count(),
        'ordenes_pendientes': db.query(Orden).filter(Orden.estado == 'Pendiente').count(),
        'ordenes_en_proceso': db.query(Orden).filter(Orden.estado == 'En Proceso').count(),
        'cotizaciones_pendientes': db.query(Cotizacion).filter(Cotizacion.estado == 'Pendiente').count(),
    }