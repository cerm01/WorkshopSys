from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ==================== CLIENTES ====================

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    tipo = Column(String(50), nullable=False)  # 'Particular' o 'Empresa'
    email = Column(String(150), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    # Dirección
    calle = Column(String(200), nullable=True)
    colonia = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    estado = Column(String(100), nullable=True)
    cp = Column(String(10), nullable=True)
    pais = Column(String(100), default="México")
    
    # Fiscal
    rfc = Column(String(13), nullable=True)
    
    # Metadata
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    ordenes = relationship("Orden", back_populates="cliente")
    cotizaciones = relationship("Cotizacion", back_populates="cliente")
    notas = relationship("NotaVenta", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nombre='{self.nombre}')>"


# ==================== PROVEEDORES ====================

class Proveedor(Base):
    __tablename__ = "proveedores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    tipo = Column(String(50), nullable=False)
    email = Column(String(150), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    # Dirección
    calle = Column(String(200), nullable=True)
    colonia = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    estado = Column(String(100), nullable=True)
    cp = Column(String(10), nullable=True)
    pais = Column(String(100), default="México")
    
    # Fiscal
    rfc = Column(String(13), nullable=True)
    
    # Metadata
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    productos = relationship("Producto", back_populates="proveedor")
    notas = relationship("NotaProveedor", back_populates="proveedor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Proveedor(id={self.id}, nombre='{self.nombre}')>"


# ==================== INVENTARIO ====================

class Producto(Base):
    __tablename__ = "inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    categoria = Column(String(100), nullable=False)
    
    # Stock
    stock_actual = Column(Integer, default=0)
    stock_min = Column(Integer, default=0)
    ubicacion = Column(String(100), nullable=True)
    
    # Precios
    precio_compra = Column(Float, default=0.0)
    precio_venta = Column(Float, default=0.0)
    
    # Proveedor
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    proveedor = relationship("Proveedor", back_populates="productos")
    
    # Metadata
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    movimientos = relationship("MovimientoInventario", back_populates="producto")

    def __repr__(self):
        return f"<Producto(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)  # 'Entrada' o 'Salida'
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String(200), nullable=True)
    usuario = Column(String(100), nullable=True)
    
    # Relación con producto
    producto_id = Column(Integer, ForeignKey("inventario.id"), nullable=False)
    producto = relationship("Producto", back_populates="movimientos")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Movimiento(id={self.id}, tipo='{self.tipo}', cantidad={self.cantidad})>"


# ==================== ÓRDENES DE TRABAJO ====================

class Orden(Base):
    __tablename__ = "ordenes"
    
    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    
    # Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="ordenes")
    
    # Vehículo
    vehiculo_marca = Column(String(100), nullable=True)
    vehiculo_modelo = Column(String(100), nullable=True)
    vehiculo_ano = Column(String(10), nullable=True)
    vehiculo_placas = Column(String(20), nullable=True)
    vehiculo_vin = Column(String(50), nullable=True)
    vehiculo_color = Column(String(50), nullable=True)
    vehiculo_kilometraje = Column(String(20), nullable=True)
    
    # Estado
    estado = Column(String(50), default="Pendiente")  # Pendiente, En Proceso, Completada, Cancelada
    mecanico_asignado = Column(String(100), nullable=True)
    
    # Fechas
    fecha_recepcion = Column(DateTime, default=datetime.now)
    fecha_promesa = Column(DateTime, nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)
    
    # Metadata
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    nota_folio = Column(String, nullable=True)
    
    # Relaciones
    items = relationship("OrdenItem", back_populates="orden", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Orden(id={self.id}, folio='{self.folio}', estado='{self.estado}')>"


class OrdenItem(Base):
    __tablename__ = "ordenes_items"
    
    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey("ordenes.id"), nullable=False)
    orden = relationship("Orden", back_populates="items")
    
    cantidad = Column(Integer, default=1)
    descripcion = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<OrdenItem(id={self.id}, descripcion='{self.descripcion[:30]}')>"


# ==================== COTIZACIONES ====================

class Cotizacion(Base):
    __tablename__ = "cotizaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    
    # Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="cotizaciones")
    
    # Estado
    estado = Column(String(50), default="Pendiente")  # Pendiente, Aceptada, Rechazada
    vigencia = Column(String(50), default="30 días")
    
    # Totales
    subtotal = Column(Float, default=0.0)
    impuestos = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Metadata
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    nota_folio = Column(String, nullable=True)
    
    # Relaciones
    items = relationship("CotizacionItem", back_populates="cotizacion", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cotizacion(id={self.id}, folio='{self.folio}', total={self.total})>"


class CotizacionItem(Base):
    __tablename__ = "cotizaciones_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"), nullable=False)
    cotizacion = relationship("Cotizacion", back_populates="items")
    
    cantidad = Column(Integer, default=1)
    descripcion = Column(Text, nullable=False)
    precio_unitario = Column(Float, default=0.0)
    importe = Column(Float, default=0.0)
    impuesto = Column(Float, default=0.0)  # Porcentaje
    
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<CotizacionItem(id={self.id}, descripcion='{self.descripcion[:30]}')>"


# ==================== NOTAS DE VENTA ====================

class NotaVenta(Base):
    __tablename__ = "notas_venta"
    
    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    
    # Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente", back_populates="notas")
    
    # Estado
    estado = Column(String(50), default="Registrado")  # Registrado, Pagado Parcialmente, Pagado, Cancelado
    metodo_pago = Column(String(50), nullable=True)
    
    # Totales
    subtotal = Column(Float, default=0.0)
    impuestos = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Cuentas por Cobrar
    total_pagado = Column(Float, default=0.0)
    saldo = Column(Float, default=0.0)
    
    # Metadata
    observaciones = Column(Text, nullable=True)
    fecha = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    cotizacion_folio = Column(String, nullable=True)
    orden_folio = Column(String, nullable=True)
    
    # Relaciones
    items = relationship("NotaVentaItem", back_populates="nota", cascade="all, delete-orphan")
    pagos = relationship("NotaVentaPago", back_populates="nota", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NotaVenta(id={self.id}, folio='{self.folio}', total={self.total}, saldo={self.saldo})>"


class NotaVentaItem(Base):
    __tablename__ = "notas_venta_items"
    
    id = Column(Integer, primary_key=True, index=True)
    nota_id = Column(Integer, ForeignKey("notas_venta.id"), nullable=False)
    nota = relationship("NotaVenta", back_populates="items")
    
    cantidad = Column(Integer, default=1)
    descripcion = Column(Text, nullable=False)
    precio_unitario = Column(Float, default=0.0)
    importe = Column(Float, default=0.0)
    impuesto = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<NotaVentaItem(id={self.id}, descripcion='{self.descripcion[:30]}')>"


class NotaVentaPago(Base):
    __tablename__ = "notas_venta_pagos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con NotaVenta
    nota_id = Column(Integer, ForeignKey("notas_venta.id"), nullable=False)
    nota = relationship("NotaVenta", back_populates="pagos")
    
    # Datos del pago
    monto = Column(Float, nullable=False)
    fecha_pago = Column(DateTime, default=datetime.now)
    metodo_pago = Column(String(50), nullable=False)
    memo = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<NotaVentaPago(id={self.id}, nota_id={self.nota_id}, monto={self.monto})>"


# ==================== NOTAS DE PROVEEDOR ====================

class NotaProveedor(Base):
    __tablename__ = "notas_proveedor"
    
    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(50), unique=True, nullable=False, index=True)
    
    # Proveedor
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    proveedor = relationship("Proveedor", back_populates="notas")
    
    # Estado
    estado = Column(String(50), default="Registrado")  # Registrado, Pagado Parcialmente, Pagado, Cancelado
    metodo_pago = Column(String(50), nullable=True)
    
    # Totales
    subtotal = Column(Float, default=0.0)
    impuestos = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Cuentas por Pagar
    total_pagado = Column(Float, default=0.0)
    saldo = Column(Float, default=0.0)
    
    # Metadata
    observaciones = Column(Text, nullable=True)
    fecha = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    items = relationship("NotaProveedorItem", back_populates="nota", cascade="all, delete-orphan")
    pagos = relationship("NotaProveedorPago", back_populates="nota", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NotaProveedor(id={self.id}, folio='{self.folio}', total={self.total}, saldo={self.saldo})>"


class NotaProveedorItem(Base):
    __tablename__ = "notas_proveedor_items"
    
    id = Column(Integer, primary_key=True, index=True)
    nota_id = Column(Integer, ForeignKey("notas_proveedor.id"), nullable=False)
    nota = relationship("NotaProveedor", back_populates="items")
    
    cantidad = Column(Integer, default=1)
    descripcion = Column(Text, nullable=False)
    precio_unitario = Column(Float, default=0.0)
    importe = Column(Float, default=0.0)
    impuesto = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<NotaProveedorItem(id={self.id}, descripcion='{self.descripcion[:30]}')>"


class NotaProveedorPago(Base):
    __tablename__ = "notas_proveedor_pagos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con NotaProveedor
    nota_id = Column(Integer, ForeignKey("notas_proveedor.id"), nullable=False)
    nota = relationship("NotaProveedor", back_populates="pagos")
    
    # Datos del pago
    monto = Column(Float, nullable=False)
    fecha_pago = Column(DateTime, default=datetime.now)
    metodo_pago = Column(String(50), nullable=False)
    memo = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<NotaProveedorPago(id={self.id}, nota_id={self.nota_id}, monto={self.monto})>"


# ==================== USUARIOS ====================

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Hash bcrypt
    nombre_completo = Column(String(200), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    
    # Rol
    rol = Column(String(50), default="Usuario")  # Admin, Mecánico, Vendedor, Usuario
    
    # Estado
    activo = Column(Boolean, default=True)
    ultimo_acceso = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', rol='{self.rol}')>"


# ==================== CONFIGURACIÓN EMPRESA ====================

class ConfigEmpresa(Base):
    __tablename__ = "config_empresa"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_comercial = Column(String(200), nullable=False)
    razon_social = Column(String(200), nullable=True)
    rfc = Column(String(13), nullable=True)
    
    # Dirección
    calle = Column(String(200), nullable=True)
    colonia = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    estado = Column(String(100), nullable=True)
    cp = Column(String(10), nullable=True)
    pais = Column(String(100), default="México")
    
    # Contacto
    telefono1 = Column(String(20), nullable=True)
    telefono2 = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    sitio_web = Column(String(200), nullable=True)
    
    # Logo (BLOB - guardado en base de datos)
    logo_data = Column(LargeBinary, nullable=True)  # Bytes de la imagen
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<ConfigEmpresa(nombre='{self.nombre_comercial}')>"