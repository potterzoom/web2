import matplotlib
matplotlib.use('Agg')  

import pandas as pd
from fpdf import FPDF
import os
import matplotlib.pyplot as plt
import numpy as np

class ReportGenerator:
    def __init__(self, analysis_results, output_dir, metrics):
        """
        Inicializa la clase con resultados de análisis y directorio de salida.
        :param analysis_results: Resultados de análisis (diccionario).
        :param output_dir: Directorio donde se guardarán los reportes.
        :param metrics: Métricas adicionales como latencia y carga.
        """
        self.analysis_results = analysis_results
        self.output_dir = output_dir
        self.metrics = metrics  # Métricas adicionales (latencia, disponibilidad, carga)

    def create_graphs(self):
        """
        Genera gráficos a partir de los resultados de análisis.
        """
        for algorithm, results in self.analysis_results.items():
            servers = list(results.keys())
            response_times = list(results.values())
            latencies = [self.metrics[server]['latency'] for server in servers]
            server_loads = [self.metrics[server]['load'] for server in servers]

            fig, ax = plt.subplots(2, 1, figsize=(10, 12))

            # Gráfico de tiempos de respuesta
            ax[0].bar(servers, response_times, color='skyblue')
            ax[0].set_title(f'Tiempos de Respuesta para {algorithm}')
            ax[0].set_xlabel('Servidores')
            ax[0].set_ylabel('Tiempo de Respuesta Promedio (ms)')
            ax[0].grid(axis='y', linestyle='--', alpha=0.7)

            # Gráfico de latencia y carga
            ax[1].bar(servers, latencies, color='lightcoral', alpha=0.6, label="Latencia (ms)")
            ax[1].bar(servers, server_loads, color='yellowgreen', alpha=0.6, label="Carga del Servidor")
            ax[1].set_title(f'Latencia y Carga del Servidor para {algorithm}')
            ax[1].set_xlabel('Servidores')
            ax[1].set_ylabel('Valor')
            ax[1].legend()
            ax[1].grid(axis='y', linestyle='--', alpha=0.7)

            # Ajustar el diseño y guardar el gráfico en un archivo PNG
            graph_path = os.path.join(self.output_dir, f'{algorithm}_graph.png')
            plt.tight_layout()  # Asegura que los gráficos no se solapen
            plt.savefig(graph_path)  # Guardar el gráfico como imagen
            plt.close()  # Cerrar la figura para liberar recursos
            print(f"Gráfico generado para {algorithm}: {graph_path}")

    def create_pdf_report(self):
        """
        Crea un reporte en PDF con los resultados del análisis.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, 'Reporte de Análisis de Algoritmos de Balanceo de Carga', ln=True, align='C')
        pdf.ln(10)

        # Resultados de análisis
        pdf.set_font("Arial", size=12)
        for algorithm, results in self.analysis_results.items():
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, f'Algoritmo: {algorithm}', ln=True)
            pdf.set_font("Arial", size=12)
            for server, response_time in results.items():
                # Incluye latencia y carga
                latency = self.metrics[server]['latency']
                load = self.metrics[server]['load']
                pdf.cell(0, 10, f'Servidor: {server} - Tiempo de Respuesta: {response_time:.2f} ms - Latencia: {latency:.2f} ms - Carga: {load}%', ln=True)
            pdf.ln(5)

            # Incluir gráficos
            graph_path = os.path.join(self.output_dir, f'{algorithm}_graph.png')
            if os.path.exists(graph_path):
                pdf.image(graph_path, x=10, y=pdf.get_y(), w=180)
                pdf.ln(60)  # Espaciado después del gráfico

        # Guardar PDF
        pdf_output_path = os.path.join(self.output_dir, 'analisis_report.pdf')
        pdf.output(pdf_output_path)
        print(f"Reporte PDF guardado como: {pdf_output_path}")

    def create_html_report(self):
        """
        Crea un reporte en HTML con los resultados del análisis.
        """
        html_content = '<html><head><title>Reporte de Análisis</title></head><body>'
        html_content += '<h1>Reporte de Análisis de Algoritmos de Balanceo de Carga</h1>'

        for algorithm, results in self.analysis_results.items():
            html_content += f'<h2>Algoritmo: {algorithm}</h2>'
            html_content += '<table border="1" style="border-collapse: collapse; width: 50%;">'
            html_content += '<tr><th>Servidor</th><th>Tiempo de Respuesta Promedio (ms)</th><th>Latencia (ms)</th><th>Carga (%)</th></tr>'
            for server, response_time in results.items():
                latency = self.metrics[server]['latency']
                load = self.metrics[server]['load']
                html_content += f'<tr><td>{server}</td><td>{response_time:.2f}</td><td>{latency:.2f}</td><td>{load}</td></tr>'
            html_content += '</table>'

            # Incluir gráficos
            graph_path = f'{algorithm}_graph.png'
            if os.path.exists(os.path.join(self.output_dir, graph_path)):
                html_content += f'<img src="{graph_path}" alt="Gráfico {algorithm}" style="width:600px;"><br>'

        html_content += '</body></html>'

        # Guardar HTML
        html_output_path = os.path.join(self.output_dir, 'analisis_report.html')
        with open(html_output_path, 'w') as file:
            file.write(html_content)
        print(f"Reporte HTML guardado como: {html_output_path}")

if __name__ == "__main__":
    try:
        # Resultados de análisis con métricas reales
        analysis_results = {
            'Round Robin': {'Server1': 120.5, 'Server2': 130.2, 'Server3': 115.8},
            'Least Connections': {'Server1': 110.5, 'Server2': 105.2, 'Server3': 108.7},
            'TCP Vegas': {'Server1': 95.0, 'Server2': 102.4, 'Server3': 99.1},
        }

        # Métricas adicionales (latencia, carga)
        metrics = {
            'Server1': {'latency': 120, 'load': 60},
            'Server2': {'latency': 80, 'load': 75},
            'Server3': {'latency': 200, 'load': 50}
        }

        # Crear instancia de generador de reportes
        output_directory = 'D:/proyecto_algoritmos/resultados'
        os.makedirs(output_directory, exist_ok=True)
        report_generator = ReportGenerator(analysis_results, output_directory, metrics)

        # Generar gráficos y reportes
        report_generator.create_graphs()
        report_generator.create_pdf_report()
        report_generator.create_html_report()
    except Exception as e:
        print(f"Error al generar reportes: {e}")






