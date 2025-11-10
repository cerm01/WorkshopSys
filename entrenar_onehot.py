"""
Modelo ML con 5 VARIABLES
Variables: servicio, tipo_cliente, mes, historial, dias_inactivo
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
from datetime import datetime
import random

def entrenar_modelo_correcto():
    print("=" * 60)
    print("🤖 MODELO ML CON 5 VARIABLES")
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
            
            # Calcular variables del cliente
            cot_fecha = cot.created_at if hasattr(cot, 'created_at') else datetime.now()
            mes = cot_fecha.month
            
            # Contar servicios previos del cliente (historial)
            historial = db.query(Cotizacion).filter(
                Cotizacion.cliente_id == cliente.id,
                Cotizacion.id < cot.id
            ).count()
            
            # Calcular días de inactividad (última cotización anterior)
            cot_anterior = db.query(Cotizacion).filter(
                Cotizacion.cliente_id == cliente.id,
                Cotizacion.id < cot.id
            ).order_by(Cotizacion.id.desc()).first()
            
            if cot_anterior:
                dias_inactivo = (cot_fecha - cot_anterior.created_at).days
                # Evitar días negativos (error de orden)
                dias_inactivo = max(dias_inactivo, 0)
            else:
                dias_inactivo = 0  # Cliente nuevo
            
            # Limitar dias_inactivo a valores razonables
            dias_inactivo = min(dias_inactivo, 730)  # Max 2 años
            
            for item in cot.items:
                if item.precio_unitario > 0:
                    data.append({
                        'servicio': item.descripcion.lower().strip(),
                        'tipo_cliente': cliente.tipo.lower().strip(),
                        'mes': mes,
                        'historial': historial,
                        'dias_inactivo': dias_inactivo,
                        'precio': float(item.precio_unitario)
                    })
        
        if len(data) < 30:
            print(f"❌ Datos insuficientes: {len(data)}")
            print(f"   Se necesitan al menos 30 registros, tienes {len(data)}")
            return
        
        print(f"✅ {len(data)} registros extraídos")
        
        df = pd.DataFrame(data)
        
        print(f"\n📈 Distribución de datos:")
        print(f"   • Servicios únicos: {df['servicio'].nunique()}")
        print(f"   • Tipos cliente: {df['tipo_cliente'].nunique()}")
        print(f"   • Rango meses: {df['mes'].min()}-{df['mes'].max()}")
        print(f"   • Historial promedio: {df['historial'].mean():.1f} servicios")
        print(f"   • Inactividad promedio: {df['dias_inactivo'].mean():.0f} días")
        print(f"   • Precio promedio: ${df['precio'].mean():.2f}")
        
        # ONE-HOT ENCODING para variables categóricas
        df_encoded = pd.get_dummies(df[['servicio', 'tipo_cliente']], drop_first=False)
        
        # Agregar variables numéricas
        df_encoded['mes'] = df['mes']
        df_encoded['historial'] = df['historial']
        df_encoded['dias_inactivo'] = df['dias_inactivo']
        
        X = df_encoded
        y = df['precio']
        
        print(f"\n🔧 Features creadas: {X.shape[1]}")
        print(f"   • One-hot (servicio + cliente): {len([c for c in X.columns if 'servicio_' in c or 'tipo_cliente_' in c])}")
        print(f"   • Numéricas (mes, historial, días): 3")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"\n🔄 Entrenando...")
        print(f"   • Entrenamiento: {len(X_train)} registros")
        print(f"   • Prueba: {len(X_test)} registros")
        
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
        print(f"✅ MODELO ENTRENADO CON 5 VARIABLES")
        print(f"=" * 60)
        print(f"\n📊 MÉTRICAS:")
        print(f"   • MAE: ${mae:.2f}")
        print(f"   • MAPE: {mape:.2f}%")
        print(f"   • R²: {r2:.4f} ({r2*100:.1f}% precisión)")
        
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
            mes = df.loc[idx, 'mes']
            hist = df.loc[idx, 'historial']
            dias = df.loc[idx, 'dias_inactivo']
            print(f"   {servicio:20s} (M:{mes:2d} H:{hist:2d} D:{dias:3d}) | Real: ${real:7.2f} | Pred: ${pred:7.2f} | Error: {error:5.1f}%")
        
        # Guardar modelo y columnas
        print(f"\n💾 Guardando modelo...")
        with open('modelo_ml_onehot.pkl', 'wb') as f:
            pickle.dump({
                'modelo': modelo,
                'columnas': list(X.columns),
                'metricas': {
                    'mae': round(mae, 2),
                    'mape': round(mape, 2),
                    'r2': round(r2, 4),
                    'n_datos': len(data)
                }
            }, f)
        
        print(f"✅ Modelo guardado en: modelo_ml_onehot.pkl")
        
        # Evaluación
        print(f"\n🎯 EVALUACIÓN:")
        if r2 >= 0.9:
            print(f"   ✅ R² EXCELENTE ({r2:.4f})")
        elif r2 >= 0.8:
            print(f"   ✅ R² MUY BUENO ({r2:.4f})")
        elif r2 >= 0.7:
            print(f"   ✅ R² BUENO ({r2:.4f})")
        elif r2 >= 0.5:
            print(f"   ⚠️  R² ACEPTABLE ({r2:.4f})")
        else:
            print(f"   ❌ R² BAJO ({r2:.4f})")
        
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
        
        print(f"\n✅ Variables implementadas:")
        print(f"   1. Servicio (one-hot)")
        print(f"   2. Tipo Cliente (one-hot)")
        print(f"   3. Mes (numérica)")
        print(f"   4. Historial (numérica)")
        print(f"   5. Días Inactivo (numérica)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    entrenar_modelo_correcto()