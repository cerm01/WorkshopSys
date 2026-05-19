"""
Script para generar datos sintéticos de entrenamiento del modelo ML.
Genera 500 cotizaciones con servicios y precios realistas de taller automotriz.
"""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from server.database import SessionLocal
from server.models import Cliente, Cotizacion, CotizacionItem

# ==================== CATÁLOGO DE SERVICIOS ====================
# Formato: (descripcion, precio_base, variacion)
SERVICIOS = [
    ("Afinación Menor",                  550,   100),
    ("Afinación Mayor",                 1250,   200),
    ("Cambio de Aceite",                 450,    80),
    ("Cambio de Frenos Delanteros",     1000,   150),
    ("Cambio de Frenos Traseros",        900,   150),
    ("Cambio de Frenos Completo",       1800,   300),
    ("Revisión de Suspensión",           400,    80),
    ("Cambio de Amortiguadores",        2000,   400),
    ("Diagnóstico General",              350,    80),
    ("Cambio de Bujías",                 600,   100),
    ("Cambio de Filtro de Aire",         280,    60),
    ("Cambio de Filtro de Aceite",       200,    50),
    ("Cambio de Líquido de Frenos",      400,    80),
    ("Cambio de Refrigerante",           450,    80),
    ("Alineación y Balanceo",            550,    80),
    ("Cambio de Batería",               1600,   300),
    ("Servicio de Transmisión",         3000,   500),
    ("Cambio de Clutch",                4000,   600),
    ("Diagnóstico de Motor",             650,   100),
    ("Cambio de Correa de Distribución",3200,   500),
    ("Limpieza de Inyectores",           700,   120),
    ("Cambio de Termostato",             550,    80),
    ("Reparación de Escape",             800,   150),
    ("Cambio de Zapatas",                750,   120),
    ("Revisión Eléctrica",               500,   100),
]

# ==================== CLIENTES ADICIONALES ====================
CLIENTES_EXTRA = [
    ("Roberto Mendoza Ruiz",     "Particular"),
    ("Fletes y Transportes SA",  "Empresa"),
    ("Ana García Morales",       "Particular"),
    ("Taxis del Centro SC",      "Empresa"),
    ("Miguel Torres Vega",       "Particular"),
    ("Distribuidora Norteña SA", "Empresa"),
    ("Laura Sánchez Pérez",      "Particular"),
    ("Constructora Jalisco SA",  "Empresa"),
    ("Fernando López Díaz",      "Particular"),
    ("Servicios Urbanos SA",     "Empresa"),
    ("Patricia Reyes Luna",      "Particular"),
    ("Grupo Logístico MX SA",    "Empresa"),
    ("José Martínez Cruz",       "Particular"),
    ("Escuela de Manejo GDL",    "Empresa"),
    ("Carmen Flores Ibarra",     "Particular"),
]

ESTADOS = ["Pendiente", "Aceptada", "Aceptada", "Aceptada", "Rechazada"]  # Más aceptadas


def precio_con_variacion(base, variacion):
    """Genera un precio realista con variación aleatoria."""
    precio = base + random.randint(-variacion, variacion)
    # Redondear a múltiplos de 50
    precio = round(precio / 50) * 50
    return max(precio, 100)


def generar_fecha_aleatoria():
    """Genera una fecha aleatoria en los últimos 2 años."""
    dias_atras = random.randint(0, 730)
    return datetime.now() - timedelta(days=dias_atras)


def main():
    print("=" * 60)
    print("📦 GENERADOR DE DATOS DE ENTRENAMIENTO ML")
    print("=" * 60)

    db = SessionLocal()

    try:
        # ── 1. Obtener o crear clientes ──────────────────────────
        clientes = db.query(Cliente).filter_by(activo=True).all()
        print(f"\n👥 Clientes existentes: {len(clientes)}")

        if len(clientes) < 10:
            print("   Creando clientes adicionales...")
            for nombre, tipo in CLIENTES_EXTRA:
                # Evitar duplicados
                existe = db.query(Cliente).filter_by(nombre=nombre).first()
                if not existe:
                    db.add(Cliente(
                        nombre=nombre,
                        tipo=tipo,
                        ciudad="Guadalajara",
                        estado="Jalisco",
                    ))
            db.commit()
            clientes = db.query(Cliente).filter_by(activo=True).all()
            print(f"   ✅ Total clientes ahora: {len(clientes)}")

        # ── 2. Obtener folios existentes para no duplicar ────────
        folios_existentes = {c.folio for c in db.query(Cotizacion).all()}

        # Contador por año para generar folios realistas COT-YYYY-NNN
        contadores_año = {}
        for folio in folios_existentes:
            try:
                partes = folio.split("-")
                anio = int(partes[1])
                num = int(partes[2])
                if anio not in contadores_año or contadores_año[anio] < num:
                    contadores_año[anio] = num
            except Exception:
                pass

        print(f"\n📋 Folios existentes: {len(folios_existentes)}")
        print(f"🔄 Generando 500 cotizaciones...\n")

        def siguiente_folio(anio):
            contadores_año[anio] = contadores_año.get(anio, 0) + 1
            return f"COT-{anio}-{contadores_año[anio]:05d}"

        # ── 3. Generar cotizaciones ──────────────────────────────
        generadas = 0

        for i in range(500):
            fecha = generar_fecha_aleatoria()
            folio = siguiente_folio(fecha.year)

            # Por si acaso ya existe (muy improbable)
            while folio in folios_existentes:
                folio = siguiente_folio(fecha.year)
            folios_existentes.add(folio)

            cliente = random.choice(clientes)
            estado = random.choice(ESTADOS)

            # Elegir entre 1 y 3 servicios distintos por cotización
            n_servicios = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
            servicios_elegidos = random.sample(SERVICIOS, n_servicios)

            subtotal = 0.0
            items = []

            for descripcion, precio_base, variacion in servicios_elegidos:
                precio_unitario = precio_con_variacion(precio_base, variacion)
                cantidad = 1
                importe = precio_unitario * cantidad
                subtotal += importe
                items.append(CotizacionItem(
                    cantidad=cantidad,
                    descripcion=descripcion,
                    precio_unitario=float(precio_unitario),
                    importe=float(importe),
                    impuesto=16.0,
                    created_at=fecha,
                ))

            impuestos = round(subtotal * 0.16, 2)
            total = round(subtotal + impuestos, 2)

            cot = Cotizacion(
                folio=folio,
                cliente_id=cliente.id,
                estado=estado,
                vigencia="30 días",
                subtotal=round(subtotal, 2),
                impuestos=impuestos,
                total=total,
                created_at=fecha,
                updated_at=fecha,
            )
            db.add(cot)
            db.flush()  # Obtener ID antes de agregar items

            for item in items:
                item.cotizacion_id = cot.id
                db.add(item)

            generadas += 1

            if generadas % 100 == 0:
                db.commit()
                print(f"   ✅ {generadas}/500 cotizaciones generadas...")

        db.commit()

        # ── 4. Resumen ───────────────────────────────────────────
        total_cots = db.query(Cotizacion).count()
        total_items = db.query(CotizacionItem).count()

        print(f"\n{'=' * 60}")
        print(f"✅ DATOS GENERADOS EXITOSAMENTE")
        print(f"{'=' * 60}")
        print(f"   • Cotizaciones generadas:  500")
        print(f"   • Total cotizaciones en BD: {total_cots}")
        print(f"   • Total ítems en BD:        {total_items}")
        print(f"\n🎯 Ahora puedes ejecutar:")
        print(f"   python entrenar_onehot.py")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
