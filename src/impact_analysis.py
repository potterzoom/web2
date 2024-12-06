import subprocess
import platform
import logging
import pandas as pd
import matplotlib

# Forzar el uso del backend sin interfaz gráfica para evitar el error con Tkinter
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ErrorHandler:
    @staticmethod
    def handle_error(e, host):
        logging.error(f"Error en {host}: {e}")
        return {
            "promedio": float('inf'),  # Valor más adecuado para latencia no válida
            "perdida": 100,  # Pérdida del 100% si hay error
        }

class ImpactAnalysis:
    def __init__(self, servers):
        self.servers = servers
        self.latencies = []
        self.packet_loss = {}

    def obtener_latencia(self, host):
        try:
            logging.info(f"Ejecutando ping a {host}...")
            if platform.system() == "Windows":
                command = f"ping -n 4 {host}"
            else:
                command = f"ping -c 4 {host}"

            resultado = subprocess.check_output(command, shell=True, text=True)

            for linea in resultado.splitlines():
                if "Promedio" in linea or "Average" in linea:  # Windows
                    partes = linea.split('=')[-1].strip().split()
                    return float(partes[0])
                if "rtt min/avg/max/mdev" in linea:  # Linux/Mac
                    partes = linea.split('=')[1].strip().split('/')
                    return float(partes[1])  # Media de RTT

            raise ValueError("No se pudo analizar la latencia.")

        except Exception as e:
            logging.warning(f"No se encontró latencia válida para {host}. Usando valores predeterminados.")
            return ErrorHandler.handle_error(e, host)["promedio"]

    def analyze_latencies(self):
        logging.info("Analizando latencias...")
        for server in self.servers:
            latencia = self.obtener_latencia(server)
            self.latencies.append(latencia)
            self.packet_loss[server] = 100 if latencia == float('inf') else 0
        logging.info(f"Latencias analizadas: {self.latencies}")
        logging.info(f"Pérdida de paquetes: {self.packet_loss}")

    def guardar_resultados(self, ruta_resultados):
        # Asegúrate de que el archivo CSV se guarde con los datos correctos
        datos = {
            "Servidor": self.servers,
            "Latencia Promedio (ms)": self.latencies,
            "Pérdida de Paquetes (%)": [self.packet_loss[server] for server in self.servers],
        }
        df = pd.DataFrame(datos)
        df.to_csv(ruta_resultados, index=False)
        logging.info(f"Resultados guardados en {ruta_resultados}")

    def plot_results(self, ruta_grafico):
        """
        Genera un gráfico para visualizar las latencias.
        """
        if all(lat == float('inf') for lat in self.latencies):
            logging.warning("No hay datos válidos para graficar.")
            return

        plt.figure(figsize=(10, 6))
        plt.bar(self.servers, self.latencies, color='blue')
        plt.xlabel('Servidores')
        plt.ylabel('Latencia Promedio (ms)')
        plt.title('Análisis de Latencia por Servidor')
    
        # Guardamos el gráfico directamente sin intentar mostrarlo.
        plt.savefig(ruta_grafico)
        plt.close()
        logging.info(f"Gráfico guardado en {ruta_grafico}")

    def run_analysis(self):
        logging.info("Ejecutando análisis de impacto...")
        self.analyze_latencies()

        if all(lat == float('inf') for lat in self.latencies):
            logging.warning("No se pudieron obtener latencias de ningún servidor.")
            return

        ruta_resultados = "D:/proyecto_algoritmos/resultados/impact_results.csv"
        ruta_grafico = "D:/proyecto_algoritmos/resultados/latency_analysis.png"

        self.guardar_resultados(ruta_resultados)
        self.plot_results(ruta_grafico)  
        logging.info("Análisis de impacto completado.")


if __name__ == "__main__":
    servers = ["google.com", "example.com", "localhost"]
    impact_analyzer = ImpactAnalysis(servers)
    impact_analyzer.run_analysis()












































