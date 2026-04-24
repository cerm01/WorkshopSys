from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# ==================== CONFIGURACIÓN ====================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está configurada.")

# Railway entrega URLs con prefijo "postgres://", SQLAlchemy requiere "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ==================== ENGINE ====================

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
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
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
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