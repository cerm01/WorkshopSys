"""
Script para generar datos completos y relacionados entre sí:
  - Órdenes de Trabajo
  - Notas de Venta (desde órdenes y desde cotizaciones)
  - Notas de Proveedor (compras de inventario)
  - Pagos parciales y completos
"""
import sys
import os
import random
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from server.database import SessionLocal
from server.models import (
    Cliente, Proveedor, Producto,
    Orden, OrdenItem,
    Cotizacion,
    NotaVenta, NotaVentaItem, NotaVentaPago,
    NotaProveedor, NotaProveedorItem, NotaProveedorPago,
    MovimientoInventario,
)

# ==================== CATÁLOGO DE VEHÍCULOS ====================
VEHICULOS = [
    ("Toyota",      "Corolla",   ["Blanco", "Gris", "Negro"]),
    ("Toyota",      "Camry",     ["Plata", "Blanco", "Azul"]),
    ("Honda",       "Civic",     ["Negro", "Rojo", "Blanco"]),
    ("Honda",       "CR-V",      ["Gris", "Blanco", "Plata"]),
    ("Nissan",      "Sentra",    ["Blanco", "Negro", "Rojo"]),
    ("Nissan",      "Versa",     ["Gris", "Blanco", "Azul"]),
    ("Volkswagen",  "Jetta",     ["Negro", "Blanco", "Gris"]),
    ("Volkswagen",  "Golf",      ["Rojo", "Negro", "Plata"]),
    ("Chevrolet",   "Aveo",      ["Blanco", "Rojo", "Gris"]),
    ("Chevrolet",   "Trax",      ["Azul", "Blanco", "Negro"]),
    ("Ford",        "Focus",     ["Gris", "Blanco", "Rojo"]),
    ("Ford",        "Escape",    ["Plata", "Negro", "Blanco"]),
    ("Hyundai",     "Tucson",    ["Gris", "Blanco", "Azul"]),
    ("Kia",         "Rio",       ["Rojo", "Blanco", "Negro"]),
    ("Mazda",       "CX-5",      ["Gris", "Blanco", "Rojo"]),
    ("Dodge",       "Charger",   ["Negro", "Rojo", "Plata"]),
]

# ==================== SERVICIOS PARA ÓRDENES ====================
SERVICIOS_ORDEN = [
    ("Cambio de aceite y filtro",          450,  80),
    ("Afinación menor",                    550, 100),
    ("Afinación mayor",                   1250, 200),
    ("Cambio de pastillas de freno",       900, 150),
    ("Cambio de zapatas de freno",         750, 120),
    ("Cambio de frenos completo",         1800, 300),
    ("Revisión de suspensión",             400,  80),
    ("Cambio de amortiguadores delant.",  2000, 400),
    ("Diagnóstico general de motor",       650, 100),
    ("Cambio de bujías",                   600, 100),
    ("Cambio de filtro de aire",           280,  60),
    ("Cambio de líquido de frenos",        400,  80),
    ("Cambio de refrigerante",             450,  80),
    ("Alineación y balanceo",              550,  80),
    ("Cambio de batería",                 1600, 300),
    ("Revisión de sistema eléctrico",      500, 100),
    ("Cambio de clutch",                  4000, 600),
    ("Servicio de transmisión automática",3000, 500),
    ("Cambio de correa de distribución",  3200, 500),
    ("Limpieza de inyectores",             700, 120),
]

# ==================== PRODUCTOS PARA NOTAS PROVEEDOR ====================
COMPRAS_PROVEEDOR = [
    ("Filtros de aceite (caja 12 pzas)",   540,  60),
    ("Aceite motor 10W-40 (caja 12L)",    1020, 100),
    ("Pastillas de freno (par)",           250,  40),
    ("Bujías de platino (set 4 pzas)",     400,  60),
    ("Refrigerante anticongelante (4L)",   260,  40),
    ("Líquido de frenos DOT4 (1L)",        120,  20),
    ("Filtros de aire",                    280,  40),
    ("Amortiguadores delanteros (par)",   1800, 200),
    ("Balatas traseras (par)",             380,  50),
    ("Correa de distribución",             650,  80),
    ("Termostatos",                        180,  30),
    ("Cables de bujías",                   320,  50),
    ("Batería 65 Amp",                    1400, 150),
    ("Aceite de transmisión (4L)",         480,  60),
]

METODOS_PAGO = ["Efectivo", "Transferencia", "Tarjeta de Débito", "Tarjeta de Crédito"]


# ==================== UTILIDADES ====================

def precio_variado(base, variacion):
    precio = base + random.randint(-variacion, variacion)
    return max(round(precio / 50) * 50, 100)


def fecha_aleatoria(dias_max=730):
    return datetime.now() - timedelta(days=random.randint(1, dias_max))


def siguiente_folio(prefijo, contadores, año):
    key = f"{prefijo}-{año}"
    contadores[key] = contadores.get(key, 0) + 1
    return f"{prefijo}-{año}-{contadores[key]:05d}"


def cargar_contadores_existentes(db, contadores):
    """Lee folios existentes para continuar la numeración sin duplicados."""
    for modelo, prefijo in [(Orden, "ORD"), (NotaVenta, "NV"), (NotaProveedor, "NP")]:
        for reg in db.query(modelo).all():
            try:
                partes = reg.folio.split("-")
                año = int(partes[1])
                num = int(partes[-1])
                key = f"{prefijo}-{año}"
                if contadores.get(key, 0) < num:
                    contadores[key] = num
            except Exception:
                pass


# ==================== MAIN ====================

def main():
    print("=" * 60)
    print("📦 GENERADOR DE DATOS COMPLETOS CON RELACIONES")
    print("=" * 60)

    db = SessionLocal()
    contadores = {}

    try:
        cargar_contadores_existentes(db, contadores)

        # ── Cargar entidades base ────────────────────────────────
        clientes    = db.query(Cliente).filter_by(activo=True).all()
        proveedores = db.query(Proveedor).filter_by(activo=True).all()
        productos   = db.query(Producto).filter_by(activo=True).all()

        # Cotizaciones aceptadas sin nota de venta aún
        cots_aceptadas = db.query(Cotizacion).filter(
            Cotizacion.estado == "Aceptada",
            Cotizacion.nota_folio == None
        ).all()

        print(f"\n📊 Estado actual:")
        print(f"   • Clientes:              {len(clientes)}")
        print(f"   • Proveedores:           {len(proveedores)}")
        print(f"   • Productos:             {len(productos)}")
        print(f"   • Cotizaciones aceptadas disponibles: {len(cots_aceptadas)}")

        if not clientes:
            print("❌ No hay clientes. Ejecuta primero generar_datos_entrenamiento.py")
            return
        if not proveedores:
            print("❌ No hay proveedores en la BD.")
            return

        # ════════════════════════════════════════════════════════
        # 1. ÓRDENES DE TRABAJO (150)
        # ════════════════════════════════════════════════════════
        print(f"\n🔧 Generando 150 órdenes de trabajo...")
        ordenes_generadas = []

        for i in range(150):
            cliente     = random.choice(clientes)
            marca, modelo_v, colores = random.choice(VEHICULOS)
            año_v       = str(random.randint(2014, 2023))
            color       = random.choice(colores)
            placas      = f"{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}-{random.randint(100,999)}-{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
            km          = str(random.randint(15000, 150000))
            fecha_rec   = fecha_aleatoria(600)
            fecha_prom  = fecha_rec + timedelta(days=random.randint(1, 5))

            # 50% completadas, 25% en proceso, 15% pendientes, 10% canceladas
            estado = random.choices(
                ["Completada", "En Proceso", "Pendiente", "Cancelada"],
                weights=[50, 25, 15, 10]
            )[0]

            folio = siguiente_folio("ORD", contadores, fecha_rec.year)

            n_servicios = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
            servicios   = random.sample(SERVICIOS_ORDEN, n_servicios)

            orden = Orden(
                folio=folio,
                cliente_id=cliente.id,
                vehiculo_marca=marca,
                vehiculo_modelo=modelo_v,
                vehiculo_ano=año_v,
                vehiculo_placas=placas,
                vehiculo_color=color,
                vehiculo_kilometraje=km,
                estado=estado,
                mecanico_asignado=random.choice(["mecanico1", "Juan Pérez", "Carlos Ruiz"]),
                fecha_recepcion=fecha_rec,
                fecha_promesa=fecha_prom,
                fecha_entrega=fecha_prom if estado == "Completada" else None,
                observaciones=random.choice([
                    "Cliente reporta ruido al frenar",
                    "Mantenimiento preventivo",
                    "Revisión general solicitada",
                    "Falla en el arranque",
                    "Vibración a alta velocidad",
                    None
                ]),
                created_at=fecha_rec,
                updated_at=fecha_rec,
            )
            db.add(orden)
            db.flush()

            for desc, precio_b, var in servicios:
                db.add(OrdenItem(
                    orden_id=orden.id,
                    cantidad=1,
                    descripcion=desc,
                    created_at=fecha_rec,
                ))

            ordenes_generadas.append(orden)

            if (i + 1) % 50 == 0:
                db.commit()
                print(f"   ✅ {i+1}/150 órdenes generadas")

        db.commit()
        print(f"   ✅ 150 órdenes generadas")

        # ════════════════════════════════════════════════════════
        # 2. NOTAS DE VENTA (desde órdenes completadas)
        # ════════════════════════════════════════════════════════
        ordenes_completadas = [o for o in ordenes_generadas if o.estado == "Completada"]
        # Convertir ~80% de completadas en notas
        ordenes_a_facturar  = random.sample(
            ordenes_completadas,
            min(int(len(ordenes_completadas) * 0.8), len(ordenes_completadas))
        )

        print(f"\n💰 Generando notas de venta desde {len(ordenes_a_facturar)} órdenes completadas...")
        notas_generadas = []

        for orden in ordenes_a_facturar:
            items_orden = db.query(OrdenItem).filter_by(orden_id=orden.id).all()
            fecha_nota  = orden.fecha_entrega or orden.fecha_promesa

            subtotal = 0.0
            items_nv = []
            for item in items_orden:
                # Buscar precio del servicio en catálogo
                precio_ref = next(
                    (p for d, p, v in SERVICIOS_ORDEN if d == item.descripcion),
                    800
                )
                variacion   = next(
                    (v for d, p, v in SERVICIOS_ORDEN if d == item.descripcion),
                    100
                )
                precio_unit = precio_variado(precio_ref, variacion)
                importe     = precio_unit * item.cantidad
                subtotal   += importe
                items_nv.append((item.descripcion, item.cantidad, float(precio_unit), float(importe)))

            impuestos = round(subtotal * 0.16, 2)
            total     = round(subtotal + impuestos, 2)

            estado_pago  = random.choices(
                ["Pagado", "Pagado Parcialmente", "Registrado"],
                weights=[60, 25, 15]
            )[0]
            metodo_pago  = random.choice(METODOS_PAGO)
            folio_nv     = siguiente_folio("NV", contadores, fecha_nota.year)

            nota = NotaVenta(
                folio=folio_nv,
                cliente_id=orden.cliente_id,
                estado=estado_pago,
                metodo_pago=metodo_pago,
                subtotal=round(subtotal, 2),
                impuestos=impuestos,
                total=total,
                total_pagado=0.0,
                saldo=total,
                orden_folio=orden.folio,
                fecha=fecha_nota,
                created_at=fecha_nota,
                updated_at=fecha_nota,
            )
            db.add(nota)
            db.flush()

            for desc, cant, precio_unit, importe in items_nv:
                db.add(NotaVentaItem(
                    nota_id=nota.id,
                    cantidad=cant,
                    descripcion=desc,
                    precio_unitario=precio_unit,
                    importe=importe,
                    impuesto=16.0,
                    created_at=fecha_nota,
                ))

            # Registrar pago según estado
            if estado_pago == "Pagado":
                db.add(NotaVentaPago(
                    nota_id=nota.id,
                    monto=total,
                    fecha_pago=fecha_nota + timedelta(days=random.randint(0, 3)),
                    metodo_pago=metodo_pago,
                    memo="Pago completo",
                    created_at=fecha_nota,
                ))
                nota.total_pagado = total
                nota.saldo        = 0.0

            elif estado_pago == "Pagado Parcialmente":
                abono = round(total * random.uniform(0.3, 0.7) / 50) * 50
                db.add(NotaVentaPago(
                    nota_id=nota.id,
                    monto=abono,
                    fecha_pago=fecha_nota + timedelta(days=1),
                    metodo_pago=metodo_pago,
                    memo="Abono inicial",
                    created_at=fecha_nota,
                ))
                nota.total_pagado = float(abono)
                nota.saldo        = round(total - abono, 2)

            # Actualizar orden como facturada
            orden.estado     = "Facturada"
            orden.nota_folio = folio_nv

            notas_generadas.append(nota)

        db.commit()
        print(f"   ✅ {len(ordenes_a_facturar)} notas de venta desde órdenes generadas")

        # ════════════════════════════════════════════════════════
        # 3. NOTAS DE VENTA (desde cotizaciones aceptadas)
        # ════════════════════════════════════════════════════════
        cots_disponibles = random.sample(
            cots_aceptadas,
            min(80, len(cots_aceptadas))
        )

        print(f"\n💰 Generando notas de venta desde {len(cots_disponibles)} cotizaciones aceptadas...")

        for cot in cots_disponibles:
            items_cot  = cot.items
            fecha_nota = cot.created_at + timedelta(days=random.randint(1, 7))

            subtotal = 0.0
            items_nv = []
            for item in items_cot:
                subtotal += item.importe
                items_nv.append((item.descripcion, item.cantidad, item.precio_unitario, item.importe))

            impuestos = round(subtotal * 0.16, 2)
            total     = round(subtotal + impuestos, 2)

            estado_pago = random.choices(
                ["Pagado", "Pagado Parcialmente", "Registrado"],
                weights=[65, 20, 15]
            )[0]
            metodo_pago = random.choice(METODOS_PAGO)
            folio_nv    = siguiente_folio("NV", contadores, fecha_nota.year)

            nota = NotaVenta(
                folio=folio_nv,
                cliente_id=cot.cliente_id,
                estado=estado_pago,
                metodo_pago=metodo_pago,
                subtotal=round(subtotal, 2),
                impuestos=impuestos,
                total=total,
                total_pagado=0.0,
                saldo=total,
                cotizacion_folio=cot.folio,
                fecha=fecha_nota,
                created_at=fecha_nota,
                updated_at=fecha_nota,
            )
            db.add(nota)
            db.flush()

            for desc, cant, precio_unit, importe in items_nv:
                db.add(NotaVentaItem(
                    nota_id=nota.id,
                    cantidad=cant,
                    descripcion=desc,
                    precio_unitario=float(precio_unit),
                    importe=float(importe),
                    impuesto=16.0,
                    created_at=fecha_nota,
                ))

            if estado_pago == "Pagado":
                db.add(NotaVentaPago(
                    nota_id=nota.id,
                    monto=total,
                    fecha_pago=fecha_nota + timedelta(days=random.randint(0, 2)),
                    metodo_pago=metodo_pago,
                    memo="Pago completo",
                    created_at=fecha_nota,
                ))
                nota.total_pagado = total
                nota.saldo        = 0.0

            elif estado_pago == "Pagado Parcialmente":
                abono = round(total * random.uniform(0.3, 0.7) / 50) * 50
                db.add(NotaVentaPago(
                    nota_id=nota.id,
                    monto=abono,
                    fecha_pago=fecha_nota + timedelta(days=1),
                    metodo_pago=metodo_pago,
                    memo="Abono inicial",
                    created_at=fecha_nota,
                ))
                nota.total_pagado = float(abono)
                nota.saldo        = round(total - abono, 2)

            # Marcar cotización como referenciada
            cot.nota_folio = folio_nv

            notas_generadas.append(nota)

        db.commit()
        print(f"   ✅ {len(cots_disponibles)} notas de venta desde cotizaciones generadas")

        # ════════════════════════════════════════════════════════
        # 4. NOTAS DE PROVEEDOR (80 compras de inventario)
        # ════════════════════════════════════════════════════════
        print(f"\n🏭 Generando 80 notas de proveedor...")

        for i in range(80):
            proveedor  = random.choice(proveedores)
            fecha_nota = fecha_aleatoria(600)
            n_items    = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
            compras    = random.sample(COMPRAS_PROVEEDOR, min(n_items, len(COMPRAS_PROVEEDOR)))

            subtotal = 0.0
            items_np = []
            for desc, precio_b, var in compras:
                cantidad    = random.randint(1, 5)
                precio_unit = precio_variado(precio_b, var)
                importe     = precio_unit * cantidad
                subtotal   += importe
                items_np.append((desc, cantidad, float(precio_unit), float(importe)))

            impuestos = round(subtotal * 0.16, 2)
            total     = round(subtotal + impuestos, 2)

            estado_pago = random.choices(
                ["Pagado", "Pagado Parcialmente", "Registrado"],
                weights=[55, 25, 20]
            )[0]
            metodo_pago = random.choice(METODOS_PAGO)
            folio_np    = siguiente_folio("NP", contadores, fecha_nota.year)

            nota_p = NotaProveedor(
                folio=folio_np,
                proveedor_id=proveedor.id,
                estado=estado_pago,
                metodo_pago=metodo_pago,
                subtotal=round(subtotal, 2),
                impuestos=impuestos,
                total=total,
                total_pagado=0.0,
                saldo=total,
                fecha=fecha_nota,
                created_at=fecha_nota,
                updated_at=fecha_nota,
            )
            db.add(nota_p)
            db.flush()

            for desc, cant, precio_unit, importe in items_np:
                db.add(NotaProveedorItem(
                    nota_id=nota_p.id,
                    cantidad=cant,
                    descripcion=desc,
                    precio_unitario=precio_unit,
                    importe=importe,
                    impuesto=16.0,
                    created_at=fecha_nota,
                ))

                # Registrar movimiento de inventario
                # Primero intenta match por palabra clave, si no toma uno al azar
                palabras_clave = [
                    p for p in desc.lower().split()
                    if p not in ("de", "del", "la", "el", "los", "las",
                                 "caja", "pzas", "pza", "par", "set", "4l",
                                 "12l", "1l", "4", "12")
                ]
                prod = next(
                    (p for p in productos if any(
                        palabra[:5] in p.nombre.lower()
                        for palabra in palabras_clave
                    )),
                    random.choice(productos) if productos else None
                )
                if prod:
                    db.add(MovimientoInventario(
                        tipo="Entrada",
                        cantidad=cant,
                        motivo=f"Compra: {folio_np}",
                        usuario="admin",
                        producto_id=prod.id,
                        created_at=fecha_nota,
                    ))

            if estado_pago == "Pagado":
                db.add(NotaProveedorPago(
                    nota_id=nota_p.id,
                    monto=total,
                    fecha_pago=fecha_nota + timedelta(days=random.randint(0, 5)),
                    metodo_pago=metodo_pago,
                    memo="Pago completo",
                    created_at=fecha_nota,
                ))
                nota_p.total_pagado = total
                nota_p.saldo        = 0.0

            elif estado_pago == "Pagado Parcialmente":
                abono = round(total * random.uniform(0.3, 0.6) / 50) * 50
                db.add(NotaProveedorPago(
                    nota_id=nota_p.id,
                    monto=abono,
                    fecha_pago=fecha_nota + timedelta(days=2),
                    metodo_pago=metodo_pago,
                    memo="Abono inicial",
                    created_at=fecha_nota,
                ))
                nota_p.total_pagado = float(abono)
                nota_p.saldo        = round(total - abono, 2)

            if (i + 1) % 20 == 0:
                db.commit()
                print(f"   ✅ {i+1}/80 notas de proveedor generadas")

        db.commit()
        print(f"   ✅ 80 notas de proveedor generadas")

        # ════════════════════════════════════════════════════════
        # RESUMEN
        # ════════════════════════════════════════════════════════
        print(f"\n{'=' * 60}")
        print(f"✅ DATOS GENERADOS EXITOSAMENTE")
        print(f"{'=' * 60}")
        print(f"   • Órdenes de trabajo:    {db.query(Orden).count()}")
        print(f"   • Notas de venta:        {db.query(NotaVenta).count()}")
        print(f"   • Notas de proveedor:    {db.query(NotaProveedor).count()}")
        print(f"   • Movimientos inventario:{db.query(MovimientoInventario).count()}")
        print(f"\n🔗 RELACIONES CREADAS:")
        print(f"   • Notas con referencia a orden:       {db.query(NotaVenta).filter(NotaVenta.orden_folio != None).count()}")
        print(f"   • Notas con referencia a cotización:  {db.query(NotaVenta).filter(NotaVenta.cotizacion_folio != None).count()}")
        print(f"   • Órdenes facturadas:                 {db.query(Orden).filter(Orden.estado == 'Facturada').count()}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
