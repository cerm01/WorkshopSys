"""
Limpia todos los datos transaccionales manteniendo
clientes, proveedores, productos, usuarios y configuración.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from server.database import SessionLocal
from sqlalchemy import text

TABLAS_A_LIMPIAR = [
    "notas_proveedor_pagos",
    "notas_proveedor_items",
    "notas_proveedor",
    "notas_venta_pagos",
    "notas_venta_items",
    "notas_venta",
    "cotizaciones_items",
    "cotizaciones",
    "ordenes_items",
    "ordenes",
    "movimientos_inventario",
]

def main():
    print("=" * 50)
    print("🗑️  LIMPIEZA DE DATOS TRANSACCIONALES")
    print("=" * 50)
    print("\nSe conservarán: clientes, proveedores, productos, usuarios, configuración")
    print("\nEsto eliminará:")
    for t in TABLAS_A_LIMPIAR:
        print(f"  • {t}")

    confirmacion = input("\n¿Confirmas? Escribe 'SI' para continuar: ")
    if confirmacion.strip().upper() != "SI":
        print("Cancelado.")
        return

    db = SessionLocal()
    try:
        for tabla in TABLAS_A_LIMPIAR:
            db.execute(text(f"DELETE FROM {tabla}"))
            print(f"  ✅ {tabla} limpiada")

        db.commit()

        # Resetear secuencias
        for tabla in TABLAS_A_LIMPIAR:
            try:
                db.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), 1, false)"
                ))
            except Exception:
                pass
        db.commit()

        print("\n✅ Limpieza completada. Las secuencias fueron reseteadas.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
