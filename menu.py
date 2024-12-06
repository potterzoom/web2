from flask import Flask, render_template, jsonify, Response
import pandas as pd
import os
import psutil
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess
import time

# Ruta del archivo CSV para histórico
HISTORICO_PATH = "D:/proyecto_algoritmos/resultados/historico_latencias.csv"

# Inicialización de Flask
app = Flask(__name__)

# Función para validar o crear un archivo CSV vacío
def verificar_o_crear_csv(ruta, columnas):
    """
    Verifica si un archivo CSV existe y lo crea con columnas específicas si no.
    """
    if not os.path.exists(ruta):
        pd.DataFrame(columns=columnas).to_csv(ruta, index=False)
        print(f"Archivo creado: {ruta}")

# Función para obtener métricas del sistema
def obtener_metricas_sistema():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return {"cpu": cpu, "memory": memory, "disk": disk}

# Función para guardar datos en el histórico
def guardar_historico(latencia_promedio, perdida_paquetes):
    """
    Guarda datos de latencia y pérdida de paquetes en el archivo `historico_latencias.csv`.
    """
    verificar_o_crear_csv(HISTORICO_PATH, ["fecha", "latencia_promedio", "perdida_paquetes"])

    nuevos_datos = pd.DataFrame({
        "fecha": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
        "latencia_promedio": [latencia_promedio],
        "perdida_paquetes": [perdida_paquetes]
    })

    historico = pd.read_csv(HISTORICO_PATH)
    historico = pd.concat([historico, nuevos_datos], ignore_index=True)
    historico.to_csv(HISTORICO_PATH, index=False)
    print(f"Histórico actualizado en {HISTORICO_PATH}")

# Opciones del menú
opciones = [
    {"id": 1, "nombre": "Cargar Servidores"},
    {"id": 2, "nombre": "Medir Latencia"},
    {"id": 3, "nombre": "Gestión de Congestión"},
    {"id": 4, "nombre": "Alertas Predictivas"},
    {"id": 5, "nombre": "Tiempos de Respuesta"},
    {"id": 7, "nombre": "Asignación de Servidores"},
    {"id": 8, "nombre": "Rendimiento Global del Sistema"},
]

# Ruta principal que renderiza el menú
@app.route('/')
def index():
    return render_template('menu.html', opciones=opciones)

# Ruta para ejecutar cada funcionalidad según la opción seleccionada
@app.route('/funcion/<int:id>')
def ejecutar_funcion(id):
    funciones = {
        1: "Cargando servidores...",
        2: "Midiendo latencia...",
        3: "Gestionando congestión...",
        4: "Generando alertas predictivas...",
        5: "Calculando tiempos de respuesta...",
        7: "Asignando servidores...",
        8: "Evaluando rendimiento global del sistema...",
    }
    mensaje = funciones.get(id, "Opción no válida")
    return jsonify({"mensaje": mensaje})

@app.route('/api/historico', methods=['GET'])
def obtener_historico():
    """
    Devuelve el histórico de datos en formato JSON.
    """
    verificar_o_crear_csv(HISTORICO_PATH, ["fecha", "latencia_promedio", "perdida_paquetes"])
    df = pd.read_csv(HISTORICO_PATH)

    if df.empty:
        return jsonify({"error": "El archivo CSV está vacío."}), 404

    return jsonify(df.to_dict(orient="records"))


@app.route('/api/metrics', methods=['GET'])
def obtener_metrics():
    """
    Devuelve las métricas del sistema en tiempo real (CPU, memoria, disco).
    """
    metrics = obtener_metricas_sistema()
    guardar_historico(metrics["cpu"], metrics["memory"])  # Ejemplo: CPU y memoria como métricas
    return jsonify(metrics)

@app.route('/funcion/1')
def cargar_servidores():
    import src.scalability_analysis as sa
    servers = ["google.com", "example.com", "localhost"]
    analysis = sa.ScalabilityAnalysis(servers)
    results_df = analysis.analyze_scalability([10, 20, 30, 40, 50])
    ruta_resultados = "D:/proyecto_algoritmos/resultados/scalability_results.csv"
    analysis.guardar_resultados(results_df, ruta_resultados)

    for _, row in results_df.iterrows():
        latencia_promedio = (row['google.com'] + row['example.com'] + row['localhost']) / 3
        perdida_paquetes = 0
        guardar_historico(latencia_promedio, perdida_paquetes)

    return jsonify({"mensaje": "Análisis de escalabilidad completado y actualizado en el histórico."})

@app.route('/funcion/2')
def medir_latencia():
    """
    Mide la latencia de una lista de servidores y genera un análisis.
    """
    from src.impact_analysis import ImpactAnalysis

    servers = ["google.com", "example.com", "localhost"]  # Servidores a medir
    analyzer = ImpactAnalysis(servers)

    try:
        # Ejecutar análisis de latencia
        analyzer.run_analysis()

        # Guardar resultados en CSV
        result_path = "D:/proyecto_algoritmos/resultados/impact_results.csv"
        analyzer.guardar_resultados(result_path)

        # Generar gráfico
        graph_path = "D:/proyecto_algoritmos/resultados/latency_analysis.png"
        analyzer.plot_results(graph_path)  # Asegurándote de pasar la ruta aquí

        return jsonify({
            "mensaje": "Análisis de latencias completado. Resultados guardados.",
            "result_path": result_path,
            "graph_path": graph_path
        })

    except Exception as e:
        print(f"Error durante el análisis de latencias: {e}")
        return jsonify({"mensaje": f"Error: {str(e)}"}), 500


@app.route('/funcion/3')
def gestionar_congestion():
    from src.tcp_vegas import TCPVegas
    vegas = TCPVegas()
    vegas.simulate_rtt_adjustments(num_iterations=30)
    vegas.plot_history()
    return jsonify({"mensaje": "Simulación de gestión de congestión completada."})

@app.route('/funcion/4')
def alertas_predictivas():
    from src.predictive_analysis import PredictiveAnalysis
    analysis = PredictiveAnalysis("D:/proyecto_algoritmos/datos/requests.csv")
    analysis.run_analysis()
    return jsonify({"mensaje": "Análisis predictivo y generación de alertas completado."})

@app.route('/funcion/5')
def compare_algorithms_real():
    """
    Muestra el análisis de métricas del sistema sin medición de latencia.
    """
    # Obtener métricas del sistema
    system_metrics = obtener_metricas_sistema()

    # Datos de benchmark (ajustarlos según sea necesario)
    benchmarks = {"cpu": 75, "memory": 80, "disk": 10}  # Valores de referencia (en %)

    # Comparación con los benchmarks
    comparison = {}
    for metric, value in system_metrics.items():
        comparison[metric] = {
            "value": value,
            "benchmark_comparison": value - benchmarks[metric]
        }

    # Mostrar gráfico de las métricas
    labels = list(system_metrics.keys())
    values = list(system_metrics.values())

    plt.figure(figsize=(8, 5))  # Configurar tamaño del gráfico
    plt.bar(labels, values, color=['blue', 'green', 'red'])
    plt.axhline(y=benchmarks["cpu"], color="blue", linestyle="--", label="CPU Benchmark")
    plt.axhline(y=benchmarks["memory"], color="green", linestyle="--", label="Memory Benchmark")
    plt.axhline(y=benchmarks["disk"], color="red", linestyle="--", label="Disk Benchmark")
    plt.xlabel('Métricas')
    plt.ylabel('%')
    plt.title('Métricas del Sistema vs Benchmarks')
    plt.legend()
    plt.tight_layout()

    # Guardar gráfico
    plot_path = r"D:/proyecto_algoritmos/resultados/system_metrics.png"
    try:
        plt.savefig(plot_path)
        plt.close()
    except Exception as e:
        return jsonify({"error": f"Error al guardar el gráfico: {e}"}), 500

    # Crear PDF con las métricas
    pdf_path = r"D:/proyecto_algoritmos/resultados/system_metrics_report.pdf"
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, f"Reporte de Métricas del Sistema")
        y_position = 730

        for metric, value in system_metrics.items():
            c.drawString(100, y_position, f"{metric.capitalize()}: {value}%")
            y_position -= 20

        c.drawString(100, y_position, "Comparación con los Benchmarks:")
        y_position -= 20

        for metric, benchmark in benchmarks.items():
            comparison_value = system_metrics[metric]
            comparison_result = comparison[metric]["benchmark_comparison"]
            c.drawString(100, y_position, f"{metric.capitalize()}: {comparison_value}% (Benchmark {benchmark}%)")
            y_position -= 20

        c.showPage()
        c.save()
    except Exception as e:
        return jsonify({"error": f"Error al crear el PDF: {e}"}), 500

    # Devolver respuesta JSON con el mensaje
    return jsonify({
        "mensaje": "Análisis de métricas del sistema completado.",
        "system_metrics": system_metrics,
        "comparison": comparison,
        "pdf_report_path": pdf_path,
        "graph_path": plot_path
    })

@app.route('/funcion/7')
def rendimiento_global():
    from src.report_generator import ReportGenerator

    analysis_results = {
        'Round Robin': {'Server1': 120.5, 'Server2': 130.2, 'Server3': 115.8},
        'Least Connections': {'Server1': 110.5, 'Server2': 105.2, 'Server3': 108.7},
        'TCP Vegas': {'Server1': 95.0, 'Server2': 102.4, 'Server3': 99.1},
    }

    metrics = {
        'Server1': {'latency': 120, 'load': 60},
        'Server2': {'latency': 80, 'load': 75},
        'Server3': {'latency': 200, 'load': 50}
    }

    output_directory = 'D:/proyecto_algoritmos/resultados'
    os.makedirs(output_directory, exist_ok=True)
    report_generator = ReportGenerator(analysis_results, output_directory, metrics)

    # Generar gráficos y reportes
    try:
        report_generator.create_graphs()
    except Exception as e:
        print(f"Error al crear gráficos: {e}")

    try:
        report_generator.create_pdf_report()
    except Exception as e:
        print(f"Error al crear el reporte PDF: {e}")

    try:
        report_generator.create_html_report()
    except Exception as e:
        print(f"Error al crear el reporte HTML: {e}")

    return jsonify({"mensaje": "Reporte de rendimiento global generado."})


# Ejecutar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True, port=5000)




