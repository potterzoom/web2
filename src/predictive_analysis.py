import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import argparse
import subprocess
import psutil
import os

class PredictiveAnalysis:
    """
    Clase para realizar el análisis predictivo de latencias y cargas, con alertas predictivas.
    """

    def __init__(self, data_path=None):
        """
        Inicializa la clase con los datos cargados desde un archivo CSV o genera datos simulados.
        """
        if data_path and os.path.exists(data_path):
            try:
                self.data = pd.read_csv(data_path)
                print(f"Datos cargados desde {data_path}.")
            except Exception as e:
                raise FileNotFoundError(f"Error al cargar los datos: {e}")
        else:
            print("Archivo no encontrado. Cargando datos simulados.")
            # Si no hay archivo, podemos generar datos de latencia real
            self.servers = ['8.8.8.8', '93.184.215.14', '127.0.0.1']  # Usando direcciones IP directamente
            self.latencies = [self.obtener_latencia(server) for server in self.servers]
            self.data = pd.DataFrame({
                'request_time': np.random.randint(100, 200, size=3),  # Simulando tiempos de solicitud
                'arrival_time': np.random.randint(200, 300, size=3),  # Simulando tiempos de llegada
                'status': [1, 1, 0],  # Simulando estado
                'latency': self.latencies  # Usando latencia real
            })

        self.model = None
        self.features = None
        self.target = None
        self.threshold = 400  # Umbral crítico para alertas (en ms)

    def obtener_latencia(self, host):
        """
        Obtiene la latencia a un host usando ping.
        :param host: Dirección del servidor.
        :return: Latencia en ms.
        """
        try:
            resultado = subprocess.check_output(f"ping -c 4 {host}", shell=True, text=True)
            for linea in resultado.splitlines():
                if "rtt min/avg/max/mdev" in linea:
                    partes = linea.split('=')[1].strip().split('/')
                    return float(partes[1])  # Retorna la latencia promedio
        except Exception as e:
            print(f"Error al obtener la latencia para {host}: {e}")
            return float('inf')  # Retorna latencia infinita en caso de error

    def preprocess_data(self):
        """
        Preprocesa los datos y define características y objetivo.
        """
        required_columns = ['request_time', 'arrival_time', 'status', 'latency']  # Ajustar según datos
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError("Faltan columnas necesarias en los datos.")

        # Reemplazar latencias infinitas con un valor grande, por ejemplo, 1000 ms
        self.data['latency'] = self.data['latency'].replace([float('inf')], 1000)

        # Eliminar filas con NaN (en caso de que haya valores faltantes)
        self.data.dropna(inplace=True)

        # Ajustar la forma de los datos si es necesario (dependiendo de la variabilidad de latencias)
        self.features = self.data[['request_time', 'arrival_time', 'status']]
        self.target = self.data['latency']  # Usamos la latencia real como variable objetivo

        X_train, X_test, y_train, y_test = train_test_split(
            self.features, self.target, test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test

    def train_model(self, model_type='linear'):
        """
        Entrena el modelo de predicción.
        """
        X_train, X_test, y_train, y_test = self.preprocess_data()

        if model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor()
        else:
            raise ValueError("Tipo de modelo no reconocido. Usa 'linear' o 'random_forest'.")

        self.model.fit(X_train, y_train)
        print(f"Modelo {model_type} entrenado correctamente.")

        predictions = self.model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f"Error Cuadrático Medio (MSE): {mse}")

    def predict_latency(self, new_data):
        """
        Realiza predicciones de latencia.
        """
        if self.model is None:
            raise Exception("El modelo no está entrenado. Entrena el modelo primero con train_model().")

        predictions = self.model.predict(new_data)
        return predictions

    def generate_alerts(self, predictions):
        """
        Genera alertas si las predicciones superan el umbral crítico.
        """
        alerts = predictions[predictions > self.threshold]
        if not alerts.empty:
            print("¡ALERTAS GENERADAS!")
            for index, value in alerts.items():
                print(f"Alerta: Latencia predicha {value:.2f} ms en el índice {index}.")
        else:
            print("No se generaron alertas.")
        return alerts

    def visualize_alerts(self, predictions):
        """
        Visualiza las predicciones y destaca las alertas.
        """
        plt.figure(figsize=(12, 6))
        plt.plot(predictions, label="Predicciones", marker="o")
        plt.axhline(y=self.threshold, color="red", linestyle="--", label="Umbral Crítico")
        plt.title("Predicciones de Latencia con Umbral Crítico")
        plt.xlabel("Índice")
        plt.ylabel("Latencia (ms)")
        plt.legend()
        plt.grid()

        # Guardar gráfico en lugar de mostrarlo
        plt.savefig("alertas_predictivas.png")
        print("Gráfico guardado como alertas_predictivas.png")

    def save_alerts(self, alerts, output_path):
        """
        Guarda las alertas en un archivo CSV.
        """
        alerts.to_csv(output_path, index=True)
        print(f"Alertas guardadas en {output_path}.")

    def run_analysis(self):
        """
        Ejecuta el análisis completo con alertas predictivas.
        """
        print("Iniciando análisis predictivo...")
        X_train, X_test, _, _ = self.preprocess_data()
        self.train_model(model_type="random_forest")

        # Realizar predicciones
        predictions = pd.Series(self.predict_latency(X_test), index=X_test.index)

        # Generar alertas
        alerts = self.generate_alerts(predictions)

        # Visualizar resultados
        self.visualize_alerts(predictions)

        # Guardar alertas
        output_path = "alertas_predictivas.csv"
        self.save_alerts(alerts, output_path)
        print("Análisis completado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis predictivo con alertas.")
    parser.add_argument("data_path", type=str, help="Ruta al archivo CSV de datos.")
    args = parser.parse_args()

    analysis = PredictiveAnalysis(args.data_path)  # Si no se pasa `data_path`, usará datos simulados
    analysis.run_analysis()











