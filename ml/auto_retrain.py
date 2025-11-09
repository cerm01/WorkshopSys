import os
import pickle
from datetime import datetime
from server.database import SessionLocal
from server.models import Cotizacion

def debe_reentrenar():
    """Verificar si necesita reentrenamiento (SIMPLE)"""
    
    # Si no existe metadata, entrenar
    if not os.path.exists('modelo_metadata.pkl'):
        return True, "Primera vez"
    
    # Cargar datos previos
    try:
        with open('modelo_metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
        
        cot_previas = metadata.get('cotizaciones', 0)
        
        # Contar cotizaciones actuales
        db = SessionLocal()
        cot_actuales = db.query(Cotizacion).count()
        db.close()
        
        nuevas = cot_actuales - cot_previas
        
        # REGLA SIMPLE: Reentrenar cada 50 cotizaciones nuevas
        if nuevas >= 50:
            return True, f"{nuevas} nuevas cotizaciones"
        
        return False, f"Solo {nuevas} nuevas"
        
    except:
        return True, "Error leyendo metadata"


def reentrenar_silencioso():
    """Reentrenar sin mostrar mensajes (para background)"""
    
    try:
        # Importar función de entrenamiento
        import sys
        from io import StringIO
        
        # Capturar output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Ejecutar entrenamiento
        from entrenar_onehot import entrenar_modelo_correcto
        entrenar_modelo_correcto()
        
        # Restaurar output
        sys.stdout = old_stdout
        
        # Guardar metadata
        db = SessionLocal()
        total = db.query(Cotizacion).count()
        db.close()
        
        with open('modelo_metadata.pkl', 'wb') as f:
            pickle.dump({
                'cotizaciones': total,
                'fecha': datetime.now()
            }, f)
        
        return True
        
    except Exception as e:
        sys.stdout = old_stdout
        print(f"Error reentrenando: {e}")
        return False