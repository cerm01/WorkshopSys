from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

# ==================== CONFIGURACIÓN ====================

# Para desarrollo: SQLite (simple, sin instalación)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taller.db")

# Para producción: PostgreSQL
# DATABASE_URL = "postgresql://usuario:password@localhost/taller_db"

# ==================== ENGINE ====================

if DATABASE_URL.startswith("sqlite"):
    # SQLite: configuración especial para multi-threading
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True  # Ver queries SQL en consola (desactivar en producción)
    )
else:
    # PostgreSQL/MySQL: configuración estándar
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,  # Conexiones simultáneas
        max_overflow=20,
        pool_pre_ping=True,  # Verificar conexión antes de usar
        echo=True
    )

# ==================== SESSION ====================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==================== DEPENDENCIAS ====================

def get_db() -> Generator[Session, None, None]:
    """
    Dependencia para obtener sesión de base de datos.
    Uso en FastAPI:
        @app.get("/clientes")
        def get_clientes(db: Session = Depends(get_db)):
            return db.query(Cliente).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync() -> Session:
    """
    Obtener sesión de forma síncrona (para uso en PyQt5)
    """
    return SessionLocal()


# ==================== INICIALIZACIÓN ====================

def crear_tablas():
    """
    Crear todas las tablas en la base de datos.
    Llamar una sola vez al inicio.
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")


def eliminar_tablas():
    """
    PELIGRO: Elimina todas las tablas.
    Solo usar en desarrollo.
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️  Tablas eliminadas")


# ==================== VERIFICACIÓN ====================

def verificar_conexion() -> bool:
    """
    Verificar que la conexión a la base de datos funciona.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


# ==================== EJEMPLO DE USO ====================

if __name__ == "__main__":
    print("Probando conexión a base de datos...")
    print(f"URL: {DATABASE_URL}")
    
    # Verificar conexión
    if verificar_conexion():
        # Crear tablas
        crear_tablas()
        
        # Probar crear un cliente
        from models import Cliente
        
        db = get_db_sync()
        try:
            nuevo_cliente = Cliente(
                nombre="Cliente de Prueba",
                tipo="Particular",
                email="test@example.com",
                telefono="3312345678",
                ciudad="Guadalajara",
                estado="Jalisco"
            )
            db.add(nuevo_cliente)
            db.commit()
            db.refresh(nuevo_cliente)
            print(f"✅ Cliente creado: {nuevo_cliente}")
            
            # Verificar que se guardó
            clientes = db.query(Cliente).all()
            print(f"Total de clientes en BD: {len(clientes)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()
        finally:
            db.close()