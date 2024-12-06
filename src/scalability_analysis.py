import psutil
import pandas as pd
import matplotlib.pyplot as plt
import os
from ping3 import ping
import socket
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from matplotlib.backends.backend_pdf import PdfPages

class ScalabilityAnalysis:
    def __init__(self, servers):
        """
        Inicializa la clase con la lista de servidores.
        :param servers: Lista de servidores.
        """
        self.servers = servers

    def obtener_latencia(self, host):
        """
        Obtiene la latencia de un servidor usando ping3.
        :param host: Dirección del servidor.
        :return: Latencia promedio en milisegundos o float('inf') si falla.
        """
        try:
            latencia = ping(host, timeout=4)  # Timeout de 4 segundos
            if latencia is None:
                print(f"No se pudo alcanzar el host {host}.")
                return float('inf')
            return latencia * 1000  # Convertir a milisegundos
        except Exception as e:
            print(f"Error al medir latencia para {host}: {e}")
            return float('inf')

    def diagnosticar_host(self, host):
        """
        Diagnostica la conectividad de un host.
        :param host: Dirección del servidor.
        :return: Resultado del diagnóstico DNS.
        """
        try:
            ip = socket.gethostbyname(host)
            return f"Resolución exitosa: {ip}"
        except socket.gaierror:
            return "Error de resolución DNS"

    def obtener_metricas_sistema(self):
        """
        Obtiene métricas del sistema en tiempo real.
        :return: Uso de CPU, memoria y disco.
        """
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, memory, disk

    def analyze_scalability(self, request_ranges):
        """
        Analiza la escalabilidad de los servidores para diferentes rangos de solicitudes.
        :param request_ranges: Rango de números de solicitudes para analizar.
        :return: DataFrame con los resultados de análisis.
        """
        results = []

        for num_requests in request_ranges:
            server_metrics = {}
            for server in self.servers:
                cpu, memory, disk = self.obtener_metricas_sistema()
                latencia = self.obtener_latencia(server)
                dns_status = self.diagnosticar_host(server)

                # Validar la latencia antes de calcular el tiempo de respuesta
                if latencia == float('inf'):
                    print(f"Advertencia: Latencia inválida para {server}. Usando valor predeterminado.")
                    response_time = float('inf')
                    server_metrics[f"{server}_status"] = "Error de conectividad"
                else:
                    response_time = latencia * (1 + (cpu / 100))
                    server_metrics[f"{server}_status"] = "Conectividad OK"

                server_metrics[server] = response_time
                server_metrics[f"{server}_dns_status"] = dns_status

            results.append({'num_requests': num_requests, **server_metrics})

        return pd.DataFrame(results)

    def guardar_resultados(self, df, ruta_resultados):
        """
        Guarda los resultados del análisis en un archivo CSV.
        :param df: DataFrame con los resultados.
        :param ruta_resultados: Ruta donde se guardará el archivo CSV.
        """
        os.makedirs(os.path.dirname(ruta_resultados), exist_ok=True)
        df.to_csv(ruta_resultados, index=False)
        print(f"Resultados guardados en {ruta_resultados}")

    def plot_results(self, df):
        """
        Grafica los resultados del análisis de escalabilidad.
        :param df: DataFrame con los resultados.
        """
        plt.figure(figsize=(12, 6))
        for server in self.servers:
            plt.plot(df['num_requests'], df[server], marker='o', label=server)
        plt.title('Análisis de Escalabilidad de Servidores')
        plt.xlabel('Número de Solicitudes')
        plt.ylabel('Tiempo de Respuesta Promedio (ms)')
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    def generar_informe_pdf(self, df, ruta_pdf):
        """
        Genera un informe PDF con gráficos y resultados.
        :param df: DataFrame con los resultados.
        :param ruta_pdf: Ruta donde se guardará el archivo PDF.
        """
        # Crear el PDF
        c = canvas.Canvas(ruta_pdf, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(30, 750, "Informe de Análisis de Escalabilidad")
        c.setFont("Helvetica", 10)
        c.drawString(30, 730, "Este informe contiene los resultados del análisis de latencia y conectividad para los servidores seleccionados.")
        
        # Resumen General
        c.drawString(30, 710, f"Total de solicitudes analizadas: {len(df)}")
        servidores = ", ".join([col.split('_status')[0] for col in df.columns if '_status' in col])
        c.drawString(30, 690, f"Servidores analizados: {servidores}")

        # Detalle por servidor
        y = 670
        for server in [col.split('_status')[0] for col in df.columns if '_status' in col]:
            latencias = df[server].replace(float('inf'), 0).tolist()  # Reemplaza infinito por 0 para gráficos
            promedio = sum(latencias) / len(latencias)
            c.drawString(30, y, f"Servidor {server}: Latencia Promedio: {promedio:.2f} ms")
            y -= 20

        c.drawString(30, y - 10, "Gráficos detallados se encuentran al final del informe.")

        # Guardar el texto principal
        c.showPage()

        # Agregar los gráficos al PDF
        pdf_pages = PdfPages(ruta_pdf)
        for server in [col.split('_status')[0] for col in df.columns if '_status' in col]:
            plt.figure(figsize=(10, 6))
            plt.plot(df['num_requests'], df[server], marker='o', label=server)
            plt.title(f"Latencias para {server}")
            plt.xlabel("Número de Solicitudes")
            plt.ylabel("Latencia (ms)")
            plt.legend()
            plt.grid()
            pdf_pages.savefig()
            plt.close()
        pdf_pages.close()
        print(f"Informe PDF generado en {ruta_pdf}")

if __name__ == "__main__":
    try:
        servers = ["google.com", "example.com", "localhost"]
        scalability_analysis = ScalabilityAnalysis(servers)
        request_ranges = [10, 20, 30, 40, 50]
        results_df = scalability_analysis.analyze_scalability(request_ranges)
        print(results_df)

        # Guardar resultados en CSV
        ruta_resultados = "D:/proyecto_algoritmos/resultados/scalability_results.csv"
        scalability_analysis.guardar_resultados(results_df, ruta_resultados)

        # Generar el informe PDF
        ruta_pdf = "D:/proyecto_algoritmos/resultados/informe_escalabilidad.pdf"
        scalability_analysis.generar_informe_pdf(results_df, ruta_pdf)

        # Graficar resultados
        scalability_analysis.plot_results(results_df)
    except Exception as e:
        print(f"Error en el análisis de escalabilidad: {e}")








