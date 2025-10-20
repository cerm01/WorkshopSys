"""
Script de Inicialización de Base de Datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import SessionLocal, crear_tablas
from server.models import (
    Cliente, Proveedor, Producto, Orden, OrdenItem,
    Cotizacion, CotizacionItem, NotaVenta, NotaVentaItem,
    MovimientoInventario, Usuario
)
from datetime import datetime, timedelta

def generar_hash_password(password: str) -> str:
    """Generar hash simple (en producción usar bcrypt)"""
    # Por ahora hash simple, luego mejorar
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def cargar_datos_ejemplo():
    """Cargar datos de ejemplo en la base de datos"""
    db = SessionLocal()
    
    try:
        print("🔄 Cargando datos de ejemplo...")
        
        # ==================== USUARIOS ====================
        print("\n👤 Creando usuarios...")
        usuarios = [
            Usuario(
                username="admin",
                password_hash=generar_hash_password("admin123"),
                nombre_completo="Administrador del Sistema",
                email="admin@taller.com",
                rol="Admin",
                activo=True
            ),
            Usuario(
                username="mecanico1",
                password_hash=generar_hash_password("mec123"),
                nombre_completo="Juan Pérez Mecánico",
                email="mecanico@taller.com",
                rol="Mecánico",
                activo=True
            ),
            Usuario(
                username="vendedor1",
                password_hash=generar_hash_password("vend123"),
                nombre_completo="María López Ventas",
                email="ventas@taller.com",
                rol="Vendedor",
                activo=True
            )
        ]
        db.add_all(usuarios)
        db.commit()
        print(f"✅ {len(usuarios)} usuarios creados")
        
        # ==================== CLIENTES ====================
        print("\n👥 Creando clientes...")
        clientes = [
            Cliente(
                nombre="Juan Pérez García",
                tipo="Particular",
                email="juan.perez@email.com",
                telefono="(33) 1234-5678",
                calle="Av. Hidalgo 123",
                colonia="Centro",
                ciudad="Guadalajara",
                estado="Jalisco",
                cp="44100"
            ),
            Cliente(
                nombre="Autopartes López SA de CV",
                tipo="Empresa",
                email="contacto@autopartes.com",
                telefono="(33) 9876-5432",
                calle="Blvd. Marcelino García 456",
                colonia="Americana",
                ciudad="Zapopan",
                estado="Jalisco",
                cp="45100",
                rfc="ALP850315ABC"
            ),
            Cliente(
                nombre="Carlos Ramírez Torres",
                tipo="Particular",
                email="carlos.ramirez@correo.com",
                telefono="(33) 5555-1234",
                calle="Av. Américas 789",
                colonia="Providencia",
                ciudad="Guadalajara",
                estado="Jalisco",
                cp="44630"
            )
        ]
        db.add_all(clientes)
        db.commit()
        print(f"✅ {len(clientes)} clientes creados")
        
        # ==================== PROVEEDORES ====================
        print("\n🏭 Creando proveedores...")
        proveedores = [
            Proveedor(
                nombre="Refacciones del Norte",
                tipo="Empresa",
                email="ventas@refaccionesnorte.com",
                telefono="(33) 1111-2222",
                calle="Calle Industria 100",
                colonia="Industrial",
                ciudad="Guadalajara",
                estado="Jalisco",
                cp="44940",
                rfc="RNO920101ABC"
            ),
            Proveedor(
                nombre="Lubricantes Profesionales",
                tipo="Empresa",
                email="info@lubricantes.com",
                telefono="(33) 3333-4444",
                calle="Av. Federalismo 500",
                colonia="Centro",
                ciudad="Guadalajara",
                estado="Jalisco",
                cp="44100",
                rfc="LUP880215DEF"
            )
        ]
        db.add_all(proveedores)
        db.commit()
        print(f"✅ {len(proveedores)} proveedores creados")
        
        # Obtener IDs de proveedores
        prov1 = db.query(Proveedor).filter_by(nombre="Refacciones del Norte").first()
        prov2 = db.query(Proveedor).filter_by(nombre="Lubricantes Profesionales").first()
        
        # ==================== INVENTARIO ====================
        print("\n📦 Creando productos...")
        productos = [
            Producto(
                codigo="REF-001",
                nombre="Filtro de Aceite Universal",
                categoria="Refacciones",
                stock_actual=25,
                stock_min=10,
                ubicacion="Estante A1",
                precio_compra=45.00,
                precio_venta=85.00,
                proveedor_id=prov1.id,
                descripcion="Filtro de aceite compatible con múltiples modelos"
            ),
            Producto(
                codigo="REF-002",
                nombre="Pastillas de Freno Delanteras",
                categoria="Refacciones",
                stock_actual=15,
                stock_min=8,
                ubicacion="Estante A2",
                precio_compra=250.00,
                precio_venta=450.00,
                proveedor_id=prov1.id,
                descripcion="Pastillas cerámicas de alta calidad"
            ),
            Producto(
                codigo="CON-001",
                nombre="Aceite Motor 10W-40 Sintético",
                categoria="Consumibles",
                stock_actual=50,
                stock_min=20,
                ubicacion="Bodega C1",
                precio_compra=85.00,
                precio_venta=150.00,
                proveedor_id=prov2.id,
                descripcion="Aceite sintético premium 1 litro"
            ),
            Producto(
                codigo="CON-002",
                nombre="Refrigerante Anticongelante",
                categoria="Consumibles",
                stock_actual=30,
                stock_min=15,
                ubicacion="Bodega C2",
                precio_compra=65.00,
                precio_venta=120.00,
                proveedor_id=prov2.id,
                descripcion="Refrigerante verde concentrado 1 galón"
            ),
            Producto(
                codigo="ACC-001",
                nombre="Tapete Automotriz Universal",
                categoria="Accesorios",
                stock_actual=20,
                stock_min=10,
                ubicacion="Estante D1",
                precio_compra=150.00,
                precio_venta=280.00,
                proveedor_id=prov1.id,
                descripcion="Juego de 4 tapetes de hule"
            )
        ]
        db.add_all(productos)
        db.commit()
        print(f"✅ {len(productos)} productos creados")
        
        # ==================== MOVIMIENTOS DE INVENTARIO ====================
        print("\n📊 Creando movimientos de inventario...")
        prod_filtro = db.query(Producto).filter_by(codigo="REF-001").first()
        prod_aceite = db.query(Producto).filter_by(codigo="CON-001").first()
        
        movimientos = [
            MovimientoInventario(
                tipo="Entrada",
                cantidad=50,
                motivo="Compra inicial",
                usuario="admin",
                producto_id=prod_filtro.id,
                created_at=datetime.now() - timedelta(days=10)
            ),
            MovimientoInventario(
                tipo="Salida",
                cantidad=25,
                motivo="Venta a cliente",
                usuario="vendedor1",
                producto_id=prod_filtro.id,
                created_at=datetime.now() - timedelta(days=5)
            ),
            MovimientoInventario(
                tipo="Entrada",
                cantidad=100,
                motivo="Reabastecimiento",
                usuario="admin",
                producto_id=prod_aceite.id,
                created_at=datetime.now() - timedelta(days=7)
            )
        ]
        db.add_all(movimientos)
        db.commit()
        print(f"✅ {len(movimientos)} movimientos registrados")
        
        # ==================== ÓRDENES DE TRABAJO ====================
        print("\n🔧 Creando órdenes de trabajo...")
        cliente1 = db.query(Cliente).first()
        
        orden1 = Orden(
            folio="ORD-2025-001",
            cliente_id=cliente1.id,
            vehiculo_marca="Toyota",
            vehiculo_modelo="Corolla",
            vehiculo_ano="2018",
            vehiculo_placas="ABC-123-D",
            vehiculo_color="Blanco",
            vehiculo_kilometraje="85000",
            estado="En Proceso",
            mecanico_asignado="mecanico1",
            fecha_recepcion=datetime.now() - timedelta(days=2),
            fecha_promesa=datetime.now() + timedelta(days=1),
            observaciones="Cliente reporta ruido en frenos"
        )
        db.add(orden1)
        db.commit()
        
        # Items de la orden
        items_orden = [
            OrdenItem(
                orden_id=orden1.id,
                cantidad=1,
                descripcion="Cambio de pastillas de freno delanteras"
            ),
            OrdenItem(
                orden_id=orden1.id,
                cantidad=4,
                descripcion="Cambio de aceite de motor 10W-40"
            ),
            OrdenItem(
                orden_id=orden1.id,
                cantidad=1,
                descripcion="Cambio de filtro de aceite"
            )
        ]
        db.add_all(items_orden)
        db.commit()
        print(f"✅ 1 orden creada con {len(items_orden)} items")
        
        # ==================== COTIZACIONES ====================
        print("\n💰 Creando cotizaciones...")
        cotizacion1 = Cotizacion(
            folio="COT-2025-001",
            cliente_id=cliente1.id,
            estado="Pendiente",
            vigencia="30 días",
            subtotal=1850.00,
            impuestos=296.00,
            total=2146.00
        )
        db.add(cotizacion1)
        db.commit()
        
        items_cotizacion = [
            CotizacionItem(
                cotizacion_id=cotizacion1.id,
                cantidad=1,
                descripcion="Servicio de afinación mayor",
                precio_unitario=850.00,
                importe=850.00,
                impuesto=16.0
            ),
            CotizacionItem(
                cotizacion_id=cotizacion1.id,
                cantidad=4,
                descripcion="Bujías de platino",
                precio_unitario=250.00,
                importe=1000.00,
                impuesto=16.0
            )
        ]
        db.add_all(items_cotizacion)
        db.commit()
        print(f"✅ 1 cotización creada con {len(items_cotizacion)} items")
        
        print("\n" + "="*50)
        print("✅ BASE DE DATOS INICIALIZADA EXITOSAMENTE")
        print("="*50)
        print("\n📊 RESUMEN:")
        print(f"  • Usuarios: {len(usuarios)}")
        print(f"  • Clientes: {len(clientes)}")
        print(f"  • Proveedores: {len(proveedores)}")
        print(f"  • Productos: {len(productos)}")
        print(f"  • Órdenes: 1")
        print(f"  • Cotizaciones: 1")
        print("\n🔑 CREDENCIALES DE PRUEBA:")
        print("  • Admin: admin / admin123")
        print("  • Mecánico: mecanico1 / mec123")
        print("  • Vendedor: vendedor1 / vend123")
        
    except Exception as e:
        print(f"\n❌ Error al cargar datos: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("="*50)
    print("INICIALIZACIÓN DE BASE DE DATOS")
    print("Sistema de Gestión de Taller Automotriz")
    print("="*50)
    
    # Crear tablas
    print("\n1️⃣ Creando estructura de base de datos...")
    crear_tablas()
    
    # Cargar datos de ejemplo
    print("\n2️⃣ Cargando datos de ejemplo...")
    cargar_datos_ejemplo()
    
    print("\n✅ Proceso completado. La base de datos está lista para usar.")