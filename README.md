# Proyecto de Algoritmos de Balanceo de Carga

Este proyecto implementa tres algoritmos de balanceo de carga: **Round Robin**, **Least Connections** y **TCP Vegas**, diseñados para gestionar solicitudes en servidores de manera eficiente. El objetivo es distribuir las cargas de trabajo equitativamente entre los servidores disponibles para optimizar el rendimiento del sistema.

## **Estructura del Proyecto**

- **`datos/`**: Contiene los datos necesarios para las pruebas, incluyendo:
  - `requests.csv`: Archivo con datos simulados de solicitudes. Este archivo se utiliza para validar y analizar el rendimiento de los algoritmos.
  - `benchmarks.csv`: Benchmarks utilizados para comparar los resultados obtenidos.

- **`src/`**: Incluye los módulos principales del proyecto:
  - `tcp_vegas.py`: Implementación del algoritmo **TCP Vegas**.
  - `round_robin.py`: Implementación del algoritmo **Round Robin**.
  - `least_connections.py`: Implementación del algoritmo **Least Connections**.
  - `predictive_analysis.py`: Realiza análisis predictivos sobre la carga futura.
  - `simulations.py`: Ejecuta simulaciones de carga para evaluar los algoritmos.
  - `validation.py`: Valida el rendimiento de los algoritmos comparando resultados.
  - `impact_analysis.py`: Analiza el impacto de diferentes métricas, como congestión y latencia.
  - `report_generator.py`: Genera reportes automáticos en formatos PDF y HTML.
  - `scalability_analysis.py`: Analiza la escalabilidad bajo diferentes cargas.

- **`notebooks/`**: Incluye notebooks para visualización y análisis:
  - `analisis.ipynb`: Contiene gráficos y análisis avanzados de los resultados, incluyendo métricas como tiempos de respuesta, latencia y distribución de carga.

- **`resultados/`**: Carpeta para almacenar resultados y reportes generados:
  - `validation_results.csv`: Resultados de validación de los algoritmos.
  - `latency_validation.csv`: Latencias medidas por servidor.
  - Reportes en formato PDF y HTML.

## **Métricas de Latencia**

Este proyecto incluye la capacidad de medir latencias directamente desde el sistema local utilizando herramientas como **ping**. Las latencias obtenidas se integran en los análisis y simulaciones para evaluar su impacto en el rendimiento. Los datos de latencia están disponibles en el archivo `latency_validation.csv`.

### **Cómo se calculan las latencias**

1. Se utiliza el comando `ping` para medir el tiempo promedio de ida y vuelta (RTT) hacia cada servidor configurado.
2. Los valores obtenidos se almacenan y se utilizan para:
   - Comparar la eficiencia de los algoritmos.
   - Evaluar el impacto de la latencia en los tiempos de respuesta.

## **Cómo Usar**

### **1. Clonar el repositorio**

Clona el repositorio en tu máquina local:
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_PROYECTO>

