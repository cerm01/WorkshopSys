"""
Predictor de Precios con Machine Learning
Algoritmo: Regresión Lineal con One-Hot Encoding
"""
import pandas as pd
import pickle
import os

class PredictorML:
    def __init__(self):
        self.modelo = None
        self.columnas = None
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
                    self.metricas = data['metricas']
                    self.entrenado = True
                print("✅ Modelo ML cargado correctamente")
            except Exception as e:
                print(f"⚠️  Error cargando modelo: {e}")
                self.entrenado = False
    
    def predecir(self, servicio, tipo_cliente, mes=None):
        """
        Predecir precio de un servicio
        
        Args:
            servicio (str): Nombre del servicio (ej: "afinacion", "frenos delanteros")
            tipo_cliente (str): Tipo de cliente ("Particular" o "Empresa")
            mes (int, opcional): Mes del año (1-12). No se usa actualmente pero se mantiene por compatibilidad.
        
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
        
        # Normalizar inputs
        servicio = servicio.lower().strip()
        tipo_cliente = tipo_cliente.lower().strip()
        
        # Crear DataFrame con las mismas columnas del entrenamiento
        input_data = pd.DataFrame([[servicio, tipo_cliente]], 
                                  columns=['servicio', 'tipo_cliente'])
        
        # One-Hot Encoding
        input_encoded = pd.get_dummies(input_data, drop_first=False)
        
        # Asegurar que tenga TODAS las columnas del entrenamiento
        for col in self.columnas:
            if col not in input_encoded.columns:
                input_encoded[col] = 0
        
        # Mantener solo las columnas del modelo (en el mismo orden)
        input_encoded = input_encoded[self.columnas]
        
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
