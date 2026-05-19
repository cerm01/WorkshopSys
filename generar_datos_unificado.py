"""
Script unificado: genera cotizaciones, órdenes, notas de venta
y notas de proveedor con todas las relaciones correctas.

Regla clave: si una cotización queda "Aceptada", su nota de venta
se crea en el mismo paso para mantener consistencia.
"""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from server.database import SessionLocal
from server.models import (
    Cliente, Proveedor, Producto,
    Cotizacion, CotizacionItem,
    Orden, OrdenItem,
    NotaVenta, NotaVentaItem, NotaVentaPago,
    NotaProveedor, NotaProveedorItem, NotaProveedorPago,
    MovimientoInventario,
)

# ==================== CATÁLOGOS ====================

SERVICIOS = [
    ("Afinación Menor",                   550,  100),
    ("Afinación Mayor",                  1250,  200),
    ("Cambio de Aceite",                  450,   80),
    ("Cambio de Frenos Delanteros",      1000,  150),
    ("Cambio de Frenos Traseros",         900,  150),
    ("Cambio de Frenos Completo",        1800,  300),
    ("Revisión de Suspensión",            400,   80),
    ("Cambio de Amortiguadores",         2000,  400),
    ("Diagnóstico General",               350,   80),
    ("Cambio de Bujías",                  600,  100),
    ("Cambio de Filtro de Aire",          280,   60),
    ("Cambio de Filtro de Aceite",        200,   50),
    ("Cambio de Líquido de Frenos",       400,   80),
    ("Cambio de Refrigerante",            450,   80),
    ("Alineación y Balanceo",             550,   80),
    ("Cambio de Batería",                1600,  300),
    ("Servicio de Transmisión",          3000,  500),
    ("Cambio de Clutch",                 4000,  600),
    ("Diagnóstico de Motor",              650,  100),
    ("Cambio de Correa de Distribución", 3200,  500),
    ("Limpieza de Inyectores",            700,  120),
    ("Cambio de Termostato",              550,   80),
    ("Reparación de Escape",              800,  150),
    ("Cambio de Zapatas",                 750,  120),
    ("Revisión Eléctrica",                500,  100),
]

VEHICULOS = [
    ("Toyota",     "Corolla",  ["Blanco", "Gris", "Negro"]),
    ("Toyota",     "Camry",    ["Plata", "Blanco", "Azul"]),
    ("Honda",      "Civic",    ["Negro", "Rojo", "Blanco"]),
    ("Honda",      "CR-V",     ["Gris", "Blanco", "Plata"]),
    ("Nissan",     "Sentra",   ["Blanco", "Negro", "Rojo"]),
    ("Nissan",     "Versa",    ["Gris", "Blanco", "Azul"]),
    ("Volkswagen", "Jetta",    ["Negro", "Blanco", "Gris"]),
    ("Chevrolet",  "Aveo",     ["Blanco", "Rojo", "Gris"]),
    ("Ford",       "Focus",    ["Gris", "Blanco", "Rojo"]),
    ("Hyundai",    "Tucson",   ["Gris", "Blanco", "Azul"]),
    ("Kia",        "Rio",      ["Rojo", "Blanco", "Negro"]),
    ("Mazda",      "CX-5",     ["Gris", "Blanco", "Rojo"]),
]

COMPRAS_PROVEEDOR = [
    ("Filtros de aceite (caja 12 pzas)",    540,  60),
    ("Aceite motor 10W-40 (caja 12L)",     1020, 100),
    ("Pastillas de freno (par)",            500,   80),
    ("Bujías de platino (set 4 pzas)",      400,   60),
    ("Refrigerante anticongelante (4L)",    260,   40),
    ("Líquido de frenos DOT4 (1L)",         120,   20),
    ("Filtros de aire",                     280,   40),
    ("Amortiguadores delanteros (par)",    1800,  200),
    ("Balatas traseras (par)",              380,   50),
    ("Correa de distribución",              650,   80),
    ("Cables de bujías",                    320,   50),
    ("Batería 65 Amp",                     1400,  150),
    ("Aceite de transmisión (4L)",          480,   60),
    ("Termostatos",                         180,   30),
]

METODOS_PAGO = ["Efectivo", "Transferencia", "Tarjeta de Débito", "Tarjeta de Crédito"]


# ==================== UTILIDADES ====================

def precio_variado(base, variacion):
    precio = base + random.randint(-variacion, variacion)
    return float(max(round(precio / 50) * 50, 100))


def fecha_aleatoria(dias_max=700):
    return datetime.now() - timedelta(days=random.randint(1, dias_max))


def sig_folio(prefijo, contadores, año):
    key = f"{prefijo}-{año}"
    contadores[key] = contadores.get(key, 0) + 1
    return f"{prefijo}-{año}-{contadores[key]:05d}"


def calcular_totales(items_precios):
    """items_precios: lista de (desc, cant, precio_unit)"""
    subtotal = sum(cant * precio for _, cant, precio in items_precios)
    impuestos = round(subtotal * 0.16, 2)
    total = round(subtotal + impuestos, 2)
    return round(subtotal, 2), impuestos, total


def crear_pago_nota_venta(db, nota, total, fecha):
    estado = random.choices(
        ["Pagado", "Pagado Parcialmente", "Registrado"],
        weights=[60, 25, 15]
    )[0]
    metodo = random.choice(METODOS_PAGO)
    nota.estado = estado
    nota.metodo_pago = metodo

    if estado == "Pagado":
        db.add(NotaVentaPago(
            nota_id=nota.id, monto=total,
            fecha_pago=fecha + timedelta(days=random.randint(0, 3)),
            metodo_pago=metodo, memo="Pago completo", created_at=fecha,
        ))
        nota.total_pagado = total
        nota.saldo = 0.0

    elif estado == "Pagado Parcialmente":
        abono = float(round(total * random.uniform(0.3, 0.7) / 50) * 50)
        db.add(NotaVentaPago(
            nota_id=nota.id, monto=abono,
            fecha_pago=fecha + timedelta(days=1),
            metodo_pago=metodo, memo="Abono inicial", created_at=fecha,
        ))
        nota.total_pagado = abono
        nota.saldo = round(total - abono, 2)


def crear_pago_nota_proveedor(db, nota, total, fecha):
    estado = random.choices(
        ["Pagado", "Pagado Parcialmente", "Registrado"],
        weights=[55, 25, 20]
    )[0]
    metodo = random.choice(METODOS_PAGO)
    nota.estado = estado
    nota.metodo_pago = metodo

    if estado == "Pagado":
        db.add(NotaProveedorPago(
            nota_id=nota.id, monto=total,
            fecha_pago=fecha + timedelta(days=random.randint(0, 5)),
            metodo_pago=metodo, memo="Pago completo", created_at=fecha,
        ))
        nota.total_pagado = total
        nota.saldo = 0.0

    elif estado == "Pagado Parcialmente":
        abono = float(round(total * random.uniform(0.3, 0.6) / 50) * 50)
        db.add(NotaProveedorPago(
            nota_id=nota.id, monto=abono,
            fecha_pago=fecha + timedelta(days=2),
            metodo_pago=metodo, memo="Abono inicial", created_at=fecha,
        ))
        nota.total_pagado = abono
        nota.saldo = round(total - abono, 2)


# ==================== MAIN ====================

def main():
    print("=" * 60)
    print("📦 GENERADOR UNIFICADO DE DATOS")
    print("=" * 60)

    db = SessionLocal()
    contadores = {}

    try:
        clientes    = db.query(Cliente).filter_by(activo=True).all()
        proveedores = db.query(Proveedor).filter_by(activo=True).all()
        productos   = db.query(Producto).filter_by(activo=True).all()

        if not clientes:
            print("❌ No hay clientes. Agrega clientes primero.")
            return
        if not proveedores:
            print("❌ No hay proveedores.")
            return

        print(f"\n📊 Base:")
        print(f"   • Clientes:    {len(clientes)}")
        print(f"   • Proveedores: {len(proveedores)}")
        print(f"   • Productos:   {len(productos)}")

        # ════════════════════════════════════════════════════════
        # 1. COTIZACIONES (500)
        #    - Pendiente  (~35%)
        #    - Aceptada   (~45%) → nota de venta creada al momento
        #    - Rechazada  (~20%)
        # ════════════════════════════════════════════════════════
        print(f"\n📋 Generando 500 cotizaciones...")

        for i in range(500):
            cliente = random.choice(clientes)
            fecha   = fecha_aleatoria(700)

            n_items  = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
            servicios = random.sample(SERVICIOS, n_items)

            items_data = [
                (desc, 1, precio_variado(base, var))
                for desc, base, var in servicios
            ]
            subtotal, impuestos, total = calcular_totales(items_data)

            estado_cot = random.choices(
                ["Pendiente", "Aceptada", "Rechazada"],
                weights=[35, 45, 20]
            )[0]

            folio_cot = sig_folio("COT", contadores, fecha.year)

            cot = Cotizacion(
                folio=folio_cot,
                cliente_id=cliente.id,
                estado=estado_cot,
                vigencia="30 días",
                subtotal=subtotal,
                impuestos=impuestos,
                total=total,
                created_at=fecha,
                updated_at=fecha,
            )
            db.add(cot)
            db.flush()

            for desc, cant, precio_unit in items_data:
                db.add(CotizacionItem(
                    cotizacion_id=cot.id,
                    cantidad=cant,
                    descripcion=desc,
                    precio_unitario=precio_unit,
                    importe=round(cant * precio_unit, 2),
                    impuesto=16.0,
                    created_at=fecha,
                ))

            # Si es Aceptada → crear nota de venta inmediatamente
            if estado_cot == "Aceptada":
                fecha_nv   = fecha + timedelta(days=random.randint(1, 5))
                folio_nv   = sig_folio("NV", contadores, fecha_nv.year)

                nota = NotaVenta(
                    folio=folio_nv,
                    cliente_id=cliente.id,
                    estado="Registrado",
                    subtotal=subtotal,
                    impuestos=impuestos,
                    total=total,
                    total_pagado=0.0,
                    saldo=total,
                    cotizacion_folio=folio_cot,
                    fecha=fecha_nv,
                    created_at=fecha_nv,
                    updated_at=fecha_nv,
                )
                db.add(nota)
                db.flush()

                for desc, cant, precio_unit in items_data:
                    db.add(NotaVentaItem(
                        nota_id=nota.id,
                        cantidad=cant,
                        descripcion=desc,
                        precio_unitario=precio_unit,
                        importe=round(cant * precio_unit, 2),
                        impuesto=16.0,
                        created_at=fecha_nv,
                    ))

                crear_pago_nota_venta(db, nota, total, fecha_nv)
                cot.nota_folio = folio_nv

            if (i + 1) % 100 == 0:
                db.commit()
                print(f"   ✅ {i+1}/500 cotizaciones")

        db.commit()
        print(f"   ✅ 500 cotizaciones generadas")

        # ════════════════════════════════════════════════════════
        # 2. ÓRDENES DE TRABAJO (150)
        #    - Completada (~50%) → nota de venta creada al momento
        #    - En Proceso (~25%)
        #    - Pendiente  (~15%)
        #    - Cancelada  (~10%)
        # ════════════════════════════════════════════════════════
        print(f"\n🔧 Generando 150 órdenes de trabajo...")

        for i in range(150):
            cliente       = random.choice(clientes)
            marca, modelo_v, colores = random.choice(VEHICULOS)
            fecha_rec     = fecha_aleatoria(600)
            fecha_prom    = fecha_rec + timedelta(days=random.randint(1, 5))

            estado_ord = random.choices(
                ["Completada", "En Proceso", "Pendiente", "Cancelada"],
                weights=[50, 25, 15, 10]
            )[0]

            folio_ord = sig_folio("ORD", contadores, fecha_rec.year)

            n_items   = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
            servicios = random.sample(SERVICIOS, n_items)
            items_data = [
                (desc, 1, precio_variado(base, var))
                for desc, base, var in servicios
            ]
            subtotal, impuestos, total = calcular_totales(items_data)

            orden = Orden(
                folio=folio_ord,
                cliente_id=cliente.id,
                vehiculo_marca=marca,
                vehiculo_modelo=modelo_v,
                vehiculo_ano=str(random.randint(2014, 2023)),
                vehiculo_placas=f"{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}-{random.randint(100,999)}-{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}",
                vehiculo_color=random.choice(colores),
                vehiculo_kilometraje=str(random.randint(15000, 150000)),
                estado=estado_ord,
                mecanico_asignado=random.choice(["mecanico1", "Juan Pérez", "Carlos Ruiz"]),
                fecha_recepcion=fecha_rec,
                fecha_promesa=fecha_prom,
                fecha_entrega=fecha_prom if estado_ord == "Completada" else None,
                observaciones=random.choice([
                    "Cliente reporta ruido al frenar",
                    "Mantenimiento preventivo",
                    "Revisión general solicitada",
                    "Falla en el arranque",
                    "Vibración a alta velocidad",
                    None,
                ]),
                created_at=fecha_rec,
                updated_at=fecha_rec,
            )
            db.add(orden)
            db.flush()

            for desc, cant, _ in items_data:
                db.add(OrdenItem(
                    orden_id=orden.id,
                    cantidad=cant,
                    descripcion=desc,
                    created_at=fecha_rec,
                ))

            # Si es Completada → crear nota de venta inmediatamente
            if estado_ord == "Completada":
                fecha_nv = fecha_prom + timedelta(days=random.randint(0, 2))
                folio_nv = sig_folio("NV", contadores, fecha_nv.year)

                nota = NotaVenta(
                    folio=folio_nv,
                    cliente_id=cliente.id,
                    estado="Registrado",
                    subtotal=subtotal,
                    impuestos=impuestos,
                    total=total,
                    total_pagado=0.0,
                    saldo=total,
                    orden_folio=folio_ord,
                    fecha=fecha_nv,
                    created_at=fecha_nv,
                    updated_at=fecha_nv,
                )
                db.add(nota)
                db.flush()

                for desc, cant, precio_unit in items_data:
                    db.add(NotaVentaItem(
                        nota_id=nota.id,
                        cantidad=cant,
                        descripcion=desc,
                        precio_unitario=precio_unit,
                        importe=round(cant * precio_unit, 2),
                        impuesto=16.0,
                        created_at=fecha_nv,
                    ))

                crear_pago_nota_venta(db, nota, total, fecha_nv)
                orden.estado     = "Facturada"
                orden.nota_folio = folio_nv

            if (i + 1) % 50 == 0:
                db.commit()
                print(f"   ✅ {i+1}/150 órdenes")

        db.commit()
        print(f"   ✅ 150 órdenes generadas")

        # ════════════════════════════════════════════════════════
        # 3. NOTAS DE PROVEEDOR (80)
        # ════════════════════════════════════════════════════════
        print(f"\n🏭 Generando 80 notas de proveedor...")

        for i in range(80):
            proveedor  = random.choice(proveedores)
            fecha_nota = fecha_aleatoria(600)
            n_items    = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
            compras    = random.sample(COMPRAS_PROVEEDOR, min(n_items, len(COMPRAS_PROVEEDOR)))

            items_data = [
                (desc, random.randint(1, 5), precio_variado(base, var))
                for desc, base, var in compras
            ]
            subtotal, impuestos, total = calcular_totales(items_data)
            folio_np = sig_folio("NP", contadores, fecha_nota.year)

            nota_p = NotaProveedor(
                folio=folio_np,
                proveedor_id=proveedor.id,
                estado="Registrado",
                subtotal=subtotal,
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

            for desc, cant, precio_unit in items_data:
                db.add(NotaProveedorItem(
                    nota_id=nota_p.id,
                    cantidad=cant,
                    descripcion=desc,
                    precio_unitario=precio_unit,
                    importe=round(cant * precio_unit, 2),
                    impuesto=16.0,
                    created_at=fecha_nota,
                ))

                # Movimiento de inventario
                palabras = [p for p in desc.lower().split()
                            if p not in ("de","del","la","el","los","las",
                                         "caja","pzas","pza","par","set")]
                prod = next(
                    (p for p in productos if any(
                        pal[:5] in p.nombre.lower() for pal in palabras
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

            crear_pago_nota_proveedor(db, nota_p, total, fecha_nota)

            if (i + 1) % 20 == 0:
                db.commit()
                print(f"   ✅ {i+1}/80 notas de proveedor")

        db.commit()
        print(f"   ✅ 80 notas de proveedor generadas")

        # ════════════════════════════════════════════════════════
        # RESUMEN
        # ════════════════════════════════════════════════════════
        from server.models import Cotizacion as C, Orden as O, NotaVenta as NV, NotaProveedor as NP
        print(f"\n{'=' * 60}")
        print(f"✅ GENERACIÓN COMPLETADA")
        print(f"{'=' * 60}")
        print(f"   • Cotizaciones:          {db.query(C).count()}")
        print(f"     - Pendiente:           {db.query(C).filter_by(estado='Pendiente').count()}")
        print(f"     - Aceptada:            {db.query(C).filter_by(estado='Aceptada').count()}")
        print(f"     - Rechazada:           {db.query(C).filter_by(estado='Rechazada').count()}")
        print(f"   • Órdenes de trabajo:    {db.query(O).count()}")
        print(f"   • Notas de venta:        {db.query(NV).count()}")
        print(f"     - desde cotización:    {db.query(NV).filter(NV.cotizacion_folio != None).count()}")
        print(f"     - desde orden:         {db.query(NV).filter(NV.orden_folio != None).count()}")
        print(f"   • Notas de proveedor:    {db.query(NP).count()}")
        print(f"   • Movimientos inventario:{db.query(MovimientoInventario).count()}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
