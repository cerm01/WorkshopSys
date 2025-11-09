"""
Modelo ML CORRECTO con One-Hot Encoding
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.database import SessionLocal
from server.models import Cotizacion, CotizacionItem, Cliente
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd
import numpy as np
import pickle

def entrenar_modelo_correcto():
    print("=" * 60)
    print("🤖 MODELO ML CORRECTO (One-Hot Encoding)")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Extraer datos
        print("\n📊 Extrayendo datos...")
        cotizaciones = db.query(Cotizacion).all()
        
        data = []
        for cot in cotizaciones:
            cliente = db.query(Cliente).filter_by(id=cot.cliente_id).first()
            if not cliente:
                continue
            
            for item in cot.items:
                if item.precio_unitario > 0:
                    data.append({
                        'servicio': item.descripcion.lower().strip(),
                        'tipo_cliente': cliente.tipo.lower().strip(),
                        'precio': float(item.precio_unitario)
                    })
        
        if len(data) < 30:
            print(f"❌ Datos insuficientes: {len(data)}")
            return
        
        print(f"✅ {len(data)} registros extraídos")
        
        df = pd.DataFrame(data)
        
        print(f"\n📈 Distribución:")
        print(f"   • Servicios únicos: {df['servicio'].nunique()}")
        print(f"   • Tipos cliente: {df['tipo_cliente'].nunique()}")
        print(f"   • Precio promedio: ${df['precio'].mean():.2f}")
        
        # ONE-HOT ENCODING (correcto para variables categóricas)
        df_encoded = pd.get_dummies(df[['servicio', 'tipo_cliente']], drop_first=False)
        
        X = df_encoded
        y = df['precio']
        
        print(f"\n🔧 Features creadas: {X.shape[1]}")
        print(f"   Columnas: {list(X.columns[:5])}...")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n🔄 Entrenando...")
        print(f"   • Entrenamiento: {len(X_train)}")
        print(f"   • Prueba: {len(X_test)}")
        
        # Entrenar
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        # Evaluar
        y_pred_test = modelo.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred_test)
        r2 = r2_score(y_test, y_pred_test)
        
        # MAPE
        mask = y_test > 100
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_test[mask] - y_pred_test[mask]) / y_test[mask])) * 100
        else:
            mape = 999
        
        print(f"\n" + "=" * 60)
        print(f"✅ MODELO ENTRENADO")
        print(f"=" * 60)
        print(f"\n📊 MÉTRICAS:")
        print(f"   • MAE: ${mae:.2f}")
        print(f"   • MAPE: {mape:.2f}%")
        print(f"   • R²: {r2:.3f}")
        
        # Análisis detallado
        print(f"\n🔍 ANÁLISIS DE PREDICCIONES:")
        errores = np.abs(y_test.values - y_pred_test)
        errores_pct = (errores / y_test.values) * 100
        
        print(f"   • Error < 10%: {(errores_pct < 10).sum()} de {len(errores_pct)} ({(errores_pct < 10).sum()/len(errores_pct)*100:.1f}%)")
        print(f"   • Error 10-20%: {((errores_pct >= 10) & (errores_pct < 20)).sum()}")
        print(f"   • Error > 20%: {(errores_pct >= 20).sum()}")
        
        # Mostrar ejemplos
        print(f"\n📋 EJEMPLOS DE PREDICCIÓN:")
        indices = list(y_test.index)[:10]
        for idx in indices:
            real = y_test.loc[idx]
            pred_idx = list(y_test.index).index(idx)
            pred = y_pred_test[pred_idx]
            error = abs(real - pred) / real * 100 if real > 0 else 0
            servicio = df.loc[idx, 'servicio'][:20]
            print(f"   {servicio:20s} | Real: ${real:7.2f} | Pred: ${pred:7.2f} | Error: {error:5.1f}%")
        
        # Guardar modelo y columnas
        print(f"\n💾 Guardando modelo...")
        with open('modelo_ml_onehot.pkl', 'wb') as f:
            pickle.dump({
                'modelo': modelo,
                'columnas': list(X.columns),  # IMPORTANTE: guardar orden de columnas
                'metricas': {
                    'mae': round(mae, 2),
                    'mape': round(mape, 2),
                    'r2': round(r2, 3),
                    'n_datos': len(data)
                }
            }, f)
        
        print(f"✅ Modelo guardado en: modelo_ml_onehot.pkl")
        
        # Evaluación
        print(f"\n🎯 EVALUACIÓN:")
        if r2 >= 0.8:
            print(f"   ✅ R² EXCELENTE ({r2:.3f})")
        elif r2 >= 0.7:
            print(f"   ✅ R² BUENO ({r2:.3f})")
        elif r2 >= 0.5:
            print(f"   ⚠️  R² ACEPTABLE ({r2:.3f})")
        else:
            print(f"   ❌ R² BAJO ({r2:.3f})")
        
        if mape <= 10:
            print(f"   ✅ MAPE EXCELENTE ({mape:.2f}%)")
        elif mape <= 15:
            print(f"   ✅ MAPE BUENO ({mape:.2f}%)")
        elif mape <= 25:
            print(f"   ⚠️  MAPE ACEPTABLE ({mape:.2f}%)")
        else:
            print(f"   ❌ MAPE ALTO ({mape:.2f}%)")
        
        print(f"\n💡 INTERPRETACIÓN:")
        print(f"   El modelo puede predecir precios con ±${mae:.0f} de error")
        print(f"   en el {(errores_pct < 20).sum()/len(errores_pct)*100:.0f}% de los casos")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    entrenar_modelo_correcto()
