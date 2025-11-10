#!/usr/bin/env python3
"""Script de inicialización para Railway"""

import os
import sys
from pathlib import Path

# Configurar path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def setup_database():
    """Crear tablas y datos iniciales"""
    from server.database import crear_tablas
    from server.init_db import cargar_datos_ejemplo
    
    print("🔧 Inicializando base de datos...")
    
    # Crear tablas
    crear_tablas()
    print("✅ Tablas creadas")
    
    # Cargar datos de ejemplo solo en desarrollo
    if os.getenv('ENV') != 'production':
        cargar_datos_ejemplo()
        print("✅ Datos de ejemplo cargados")

if __name__ == "__main__":
    setup_database()
