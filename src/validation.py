from flask import Flask, jsonify, request
import psutil  # Para métricas del sistema
import subprocess  # Para medir latencia
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    """Ruta principal para verificar si Flask está funcionando."""
    return "¡Validación basada en métricas del sistema funcionando!"

@app.route('/metrics', methods=['GET'])
def obtener_metrics():
    """Obtiene métricas del sistema en tiempo real."""
    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage('/')._asdict(),
        "network": psutil.net_io_counters()._asdict(),
    }
    return jsonify(metrics)

@app.route('/latency/<host>', methods=['GET'])
def medir_latencia(host):
    """Mide la latencia hacia un host especificado."""
    try:
        # Ejecuta un comando de ping al host
        resultado = subprocess.check_output(f"ping -c 4 {host}", shell=True, text=True)
        for linea in resultado.splitlines():
            if "rtt min/avg/max/mdev" in linea:
                latencia_promedio = float(linea.split('=')[1].split('/')[1])
                return jsonify({"host": host, "latencia_ms": latencia_promedio})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run_validation', methods=['GET'])
def run_validation():
    """Ejecuta una validación simple basada en métricas actuales."""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    validation_result = {
        "cpu_status": "Normal" if cpu < 75 else "Alto",
        "memory_status": "Normal" if memory < 80 else "Alto",
        "disk_status": "Normal" if disk < 90 else "Alto",
        "overall_status": "OK" if cpu < 75 and memory < 80 and disk < 90 else "Alerta",
    }
    return jsonify(validation_result)

@app.route('/compare_algorithms', methods=['POST'])
def compare_algorithms():
    """
    Compara tiempos de respuesta entre algoritmos y benchmarks.
    Los datos se esperan en formato JSON.
    """
    try:
        data = request.json
        algorithms = data['algorithms']  # Diccionario de algoritmos con tiempos
        benchmarks = data['benchmarks']  # Benchmarks de referencia

        # Convertir a DataFrame para análisis
        df = pd.DataFrame(algorithms)
        df['benchmark'] = benchmarks

        # Calcular diferencia con benchmark
        df['difference'] = df.mean(axis=1) - df['benchmark']

        # Guardar resultados
        results_path = "D:/proyecto_algoritmos/resultados/algorithm_comparison.csv"
        df.to_csv(results_path, index=False)
        print(f"Resultados guardados en {results_path}")

        # Visualizar comparación
        plt.figure(figsize=(10, 6))
        for col in df.columns[:-2]:  # Omitir columnas 'benchmark' y 'difference'
            plt.plot(df.index, df[col], marker='o', label=col)
        plt.plot(df.index, df['benchmark'], marker='x', linestyle='--', label='Benchmark', color='red')
        plt.title("Comparación de Tiempos de Respuesta")
        plt.xlabel("Muestras")
        plt.ylabel("Tiempo de Respuesta (ms)")
        plt.legend()
        plt.grid()
        plt.savefig("D:/proyecto_algoritmos/resultados/comparison_plot.png")
        plt.show()

        return jsonify({"mensaje": "Comparación completada. Resultados guardados y visualización generada."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ejecutar el servidor Flask
    app.run(debug=True, port=5000)
























