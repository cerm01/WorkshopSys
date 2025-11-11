"""
Script de Migración - Actualizar BD en Railway
Ejecutar: python migrate_db.py
"""
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

# URL de la BD (Railway usa PostgreSQL)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@host:5432/dbname"
)

def migrate():
    """Aplicar migraciones necesarias"""
    print("🔄 Iniciando migración...")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # 1. Verificar si tabla usuarios existe
        if 'usuarios' not in inspector.get_table_names():
            print("❌ Tabla 'usuarios' no existe. Ejecuta crear_tablas() primero.")
            return
        
        # 2. Agregar columna ultimo_acceso si no existe
        columns = [col['name'] for col in inspector.get_columns('usuarios')]
        
        if 'ultimo_acceso' not in columns:
            print("➕ Agregando columna 'ultimo_acceso'...")
            conn.execute(text("""
                ALTER TABLE usuarios 
                ADD COLUMN ultimo_acceso TIMESTAMP NULL
            """))
            conn.commit()
            print("✅ Columna 'ultimo_acceso' agregada")
        else:
            print("✓ Columna 'ultimo_acceso' ya existe")
        
        # 3. Agregar UNIQUE constraint a username si no existe
        try:
            print("➕ Verificando constraint UNIQUE en username...")
            # Intentar agregar el constraint
            conn.execute(text("""
                ALTER TABLE usuarios 
                ADD CONSTRAINT usuarios_username_key UNIQUE (username)
            """))
            conn.commit()
            print("✅ Constraint UNIQUE agregado a username")
        except Exception as e:
            if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                print("✓ Constraint UNIQUE en username ya existe")
                conn.rollback()
            else:
                print(f"⚠️  Error al agregar constraint: {e}")
                conn.rollback()
        
        # 4. Verificar índice en username
        indexes = inspector.get_indexes('usuarios')
        username_indexed = any(
            'username' in idx.get('column_names', []) 
            for idx in indexes
        )
        
        if not username_indexed:
            print("➕ Creando índice en username...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_usuarios_username 
                ON usuarios (username)
            """))
            conn.commit()
            print("✅ Índice creado")
        else:
            print("✓ Índice en username ya existe")
        
        # 5. Verificar que email tenga constraint UNIQUE
        try:
            conn.execute(text("""
                ALTER TABLE usuarios 
                ADD CONSTRAINT usuarios_email_key UNIQUE (email)
            """))
            conn.commit()
            print("✅ Constraint UNIQUE agregado a email")
        except Exception as e:
            if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                print("✓ Constraint UNIQUE en email ya existe")
                conn.rollback()
            else:
                print(f"⚠️  Error al agregar constraint email: {e}")
                conn.rollback()
        
        print("\n✅ Migración completada")
        print("\n📋 Estado final de la tabla usuarios:")
        
        # Mostrar estructura final
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'usuarios'
            ORDER BY ordinal_position
        """))
        
        for row in result:
            print(f"  • {row[0]}: {row[1]} {'NULL' if row[2] == 'YES' else 'NOT NULL'}")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()
