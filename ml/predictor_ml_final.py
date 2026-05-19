"""
Predictor de Precios con Machine Learning - 5 VARIABLES
Algoritmo: Regresión Lineal con One-Hot Encoding
Variables: servicio, tipo_cliente, mes, historial, dias_inactivo
"""
import pandas as pd
import pickle
import os
import re
import unicodedata
from datetime import datetime


def normalizar_servicio(texto):
    """
    Normaliza nombres de servicios (debe ser idéntica a la de entrenar_onehot.py)
    """
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

class PredictorML:
    def __init__(self):
        self.modelo = None
        self.columnas = None
        self.scaler = None
        self.metricas = {'mae': 0, 'mape': 0, 'r2': 0, 'n_datos': 0}
        self.entrenado = False
        self.cargar_modelo()

    def cargar_modelo(self):
        """Cargar modelo entrenado"""
        if os.path.exists('modelo_ml_onehot.pkl'):
            try:
                with open('modelo_ml_onehot.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.modelo = data['modelo']
                    self.columnas = data['columnas']
                    self.scaler = data.get('scaler', None)
                    self.metricas = data['metricas']
                    self.entrenado = True
                print("✅ Modelo ML cargado correctamente")
            except Exception as e:
                print(f"⚠️  Error cargando modelo: {e}")
                self.entrenado = False
    
    def predecir(self, servicio, tipo_cliente, mes=None, historial=0, dias_inactivo=0):
        """
        Predecir precio de un servicio con 5 variables
        
        Args:
            servicio (str): Nombre del servicio (ej: "afinacion", "frenos delanteros")
            tipo_cliente (str): Tipo de cliente ("Particular" o "Empresa")
            mes (int, opcional): Mes del año (1-12). Si None, usa mes actual
            historial (int): Número de servicios previos del cliente (0-50)
            dias_inactivo (int): Días desde última visita (0-730)
        
        Returns:
            dict: {
                'precio': float,
                'minimo': float,
                'maximo': float,
                'confianza': float
            }
        """
        if not self.entrenado:
            raise ValueError(
                "❌ Modelo no entrenado.\n"
                "Ejecuta: python entrenar_onehot.py"
            )
        
        # Si no se especifica mes, usar el actual
        if mes is None:
            mes = datetime.now().month

        # Normalizar inputs (misma función que en entrenamiento)
        servicio = normalizar_servicio(servicio)
        tipo_cliente = tipo_cliente.lower().strip()
        
        # Crear DataFrame con las 5 variables
        input_data = pd.DataFrame([[servicio, tipo_cliente, mes, historial, dias_inactivo]], 
                                  columns=['servicio', 'tipo_cliente', 'mes', 'historial', 'dias_inactivo'])
        
        # One-Hot Encoding solo para categóricas
        input_encoded = pd.get_dummies(input_data[['servicio', 'tipo_cliente']], drop_first=False)
        
        # Agregar variables numéricas
        input_encoded['mes'] = mes
        input_encoded['historial'] = historial
        input_encoded['dias_inactivo'] = dias_inactivo
        
        # Asegurar que tenga TODAS las columnas del entrenamiento
        for col in self.columnas:
            if col not in input_encoded.columns:
                input_encoded[col] = 0
        
        # Mantener solo las columnas del modelo (en el mismo orden)
        input_encoded = input_encoded[self.columnas]

        # Aplicar el mismo escalado que se usó en el entrenamiento
        if self.scaler is not None:
            cols_numericas = ['mes', 'historial', 'dias_inactivo']
            input_encoded = input_encoded.copy()
            input_encoded[cols_numericas] = self.scaler.transform(
                input_encoded[cols_numericas]
            )

        # Predecir
        precio = self.modelo.predict(input_encoded)[0]
        
        # Asegurar precio mínimo
        precio = max(precio, 100)
        
        # Calcular rango de confianza
        margen = self.metricas['mae']
        
        return {
            'precio': round(precio, 2),
            'minimo': round(max(precio - margen, 50), 2),
            'maximo': round(precio + margen, 2),
            'confianza': round((1 - self.metricas['mape']/100) * 100, 1)
        }
    
    def get_metricas(self):
        """Obtener métricas del modelo"""
        return self.metricas

# Instancia global
predictor_ml = PredictorML()