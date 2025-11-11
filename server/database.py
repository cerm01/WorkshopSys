"""Configuración de base de datos con soporte PostgreSQL"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# URL de base de datos (PostgreSQL en producción, SQLite en desarrollo)
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./taller.db'
)

# Ajuste para Railway (usa postgres:// en lugar de postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Configuración del engine
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency para obtener sesión de BD (async)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_sync():
    """Obtener sesión de BD (sync) para uso directo"""
    return SessionLocal()

def crear_tablas():
    """Crear todas las tablas"""
    import server.models
    Base.metadata.create_all(bind=engine)
    print(f"✅ Tablas creadas: {list(Base.metadata.tables.keys())}")
