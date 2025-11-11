"""
Inicialización completa de Railway desde cero
Crea tablas, usuario admin y datos de ejemplo
"""
import requests
import json
from datetime import datetime, date

RAILWAY_URL = "https://web-production-96c8.up.railway.app"

def crear_tablas():
    """Crear todas las tablas en el orden correcto"""
    print("\n" + "="*60)
    print("CREANDO ESTRUCTURA DE BASE DE DATOS")
    print("="*60)
    
    response = requests.post(f"{RAILWAY_URL}/admin/recreate-all-tables")
    data = response.json()
    
    if data.get("success"):
        print(f"✅ {data['count']} tablas creadas:")
        for tabla in data['tables']:
            print(f"   • {tabla}")
    else:
        print(f"❌ Error: {data.get('error')}")
        return False
    
    return True

def crear_admin():
    """Crear usuario admin"""
    print("\n" + "="*60)
    print("CREANDO USUARIO ADMIN")
    print("="*60)
    
    response = requests.post(f"{RAILWAY_URL}/admin/create-admin")
    data = response.json()
    
    if data.get("success"):
        print("✅ Usuario admin creado")
        print(f"   👤 Usuario: admin")
        print(f"   🔑 Password: admin123")
    else:
        print(f"❌ Error: {data.get('error')}")
        return False
    
    return True

def cargar_datos_ejemplo():
    """Cargar datos de ejemplo"""
    print("\n" + "="*60)
    print("CARGANDO DATOS DE EJEMPLO")
    print("="*60)
    
    response = requests.post(f"{RAILWAY_URL}/admin/load-sample-data")
    data = response.json()
    
    if data.get("success"):
        print("✅ Datos de ejemplo cargados:")
        loaded = data.get('loaded', {})
        for tabla, count in loaded.items():
            if count > 0:
                print(f"   • {tabla}: {count}")
    else:
        print(f"❌ Error: {data.get('error')}")
        return False
    
    return True

def importar_datos_json():
    """Importar datos desde JSON local"""
    print("\n" + "="*60)
    print("¿IMPORTAR DATOS DESDE JSON LOCAL?")
    print("="*60)
    
    respuesta = input("¿Tienes data_export.json para importar? (s/n): ").lower()
    
    if respuesta == 's':
        try:
            with open('data_export.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            print("\n📤 Enviando datos a Railway...")
            response = requests.post(
                f"{RAILWAY_URL}/admin/import-data",
                json=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            
            if data.get("success"):
                print("✅ Datos importados correctamente:")
                imported = data.get('imported', {})
                total = data.get('total', 0)
                
                for tabla, count in imported.items():
                    if count > 0:
                        print(f"   • {tabla}: {count}")
                
                print(f"\n📊 TOTAL: {total} registros importados")
            else:
                print(f"❌ Error: {data.get('error')}")
                return False
        
        except FileNotFoundError:
            print("❌ No se encontró data_export.json")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("⏭️  Saltando importación de datos")
    
    return True

def verificar_sistema():
    """Verificar que todo esté funcionando"""
    print("\n" + "="*60)
    print("VERIFICANDO SISTEMA")
    print("="*60)
    
    # Verificar tablas
    response = requests.get(f"{RAILWAY_URL}/admin/check-tables")
    data = response.json()
    
    if data.get("success"):
        print(f"✅ Sistema operativo con {data['count']} tablas")
    else:
        print("❌ Error al verificar sistema")
        return False
    
    return True

def main():
    print("\n" + "="*70)
    print("🚀 INICIALIZACIÓN COMPLETA DE RAILWAY")
    print("="*70)
    print(f"🌐 URL: {RAILWAY_URL}")
    print()
    
    # Paso 1: Crear tablas
    if not crear_tablas():
        print("\n❌ Falló la creación de tablas. Abortando.")
        return
    
    # Paso 2: Crear admin
    if not crear_admin():
        print("\n❌ Falló la creación del admin. Abortando.")
        return
    
    # Paso 3: Cargar datos de ejemplo
    if not cargar_datos_ejemplo():
        print("\n⚠️  No se cargaron datos de ejemplo, continuando...")
    
    # Paso 4: Importar JSON (opcional)
    importar_datos_json()
    
    # Paso 5: Verificar
    if not verificar_sistema():
        print("\n⚠️  Sistema configurado pero con advertencias")
    
    print("\n" + "="*70)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("="*70)
    print(f"\n🌐 URL: {RAILWAY_URL}")
    print(f"👤 Usuario: admin")
    print(f"🔑 Password: admin123")
    print("\n🎯 Sistema listo para usar!")
    print("="*70)

if __name__ == "__main__":
    main()
