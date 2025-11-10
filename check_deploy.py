#!/usr/bin/env python3
"""Script de verificación pre-despliegue"""

import os
import sys
from pathlib import Path

def check_files():
    """Verificar que existan archivos necesarios"""
    required_files = [
        'requirements.txt',
        'Procfile',
        'railway.json',
        'runtime.txt',
        'server/main.py',
        'server/models.py',
        'server/crud.py',
        'server/database.py'
    ]
    
    print("📁 Verificando archivos necesarios...")
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"❌ Falta: {file}")
        else:
            print(f"✅ {file}")
    
    if missing:
        print(f"\n⚠️  Faltan {len(missing)} archivo(s)")
        return False
    
    print("\n✅ Todos los archivos presentes")
    return True

def check_env_example():
    """Verificar .env.example"""
    print("\n🔑 Verificando variables de entorno...")
    
    if not Path('.env.example').exists():
        print("❌ Falta .env.example")
        return False
    
    with open('.env.example', 'r') as f:
        content = f.read()
        required_vars = ['DATABASE_URL', 'SECRET_KEY', 'PORT']
        
        for var in required_vars:
            if var in content:
                print(f"✅ {var}")
            else:
                print(f"❌ Falta {var}")
                return False
    
    print("✅ Variables de entorno configuradas")
    return True

def check_requirements():
    """Verificar requirements.txt"""
    print("\n📦 Verificando dependencias...")
    
    essential = ['fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2-binary']
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
        
        for pkg in essential:
            if pkg in content:
                print(f"✅ {pkg}")
            else:
                print(f"❌ Falta {pkg}")
                return False
    
    print("✅ Dependencias esenciales presentes")
    return True

def check_gitignore():
    """Verificar .gitignore"""
    print("\n🚫 Verificando .gitignore...")
    
    if not Path('.gitignore').exists():
        print("⚠️  No hay .gitignore")
        return True
    
    with open('.gitignore', 'r') as f:
        content = f.read()
        
        important = ['.env', '*.db', '__pycache__']
        for item in important:
            if item in content:
                print(f"✅ Ignora {item}")
            else:
                print(f"⚠️  Debería ignorar {item}")
    
    return True

def main():
    print("="*50)
    print("🚀 VERIFICACIÓN PRE-DESPLIEGUE RAILWAY")
    print("="*50)
    
    checks = [
        check_files(),
        check_env_example(),
        check_requirements(),
        check_gitignore()
    ]
    
    print("\n" + "="*50)
    if all(checks):
        print("✅ TODO LISTO PARA DESPLEGAR")
        print("="*50)
        print("\n📝 PRÓXIMOS PASOS:")
        print("1. git add .")
        print("2. git commit -m 'Preparar para Railway'")
        print("3. git push origin main")
        print("4. Crear proyecto en Railway")
        print("5. Agregar PostgreSQL")
        print("6. Configurar variables de entorno")
        print("7. Ejecutar: python setup_railway.py")
        return 0
    else:
        print("❌ CORRIGE LOS ERRORES ANTES DE DESPLEGAR")
        print("="*50)
        return 1

if __name__ == "__main__":
    sys.exit(main())
