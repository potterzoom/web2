import psutil
import subprocess  # Para medir latencias
import pandas as pd
import matplotlib.pyplot as plt
from src.round_robin import RoundRobin
from src.least_connections import LeastConnections
from src.tcp_vegas import TCPVegas

class LoadSimulation:
    def __init__(self, servers):
        """
        Inicializa la clase con los servidores y parámetros de simulación.
        :param servers: Lista de servidores.
        """
        self.servers = servers
        self.results = pd.DataFrame(columns=['server', 'cpu', 'memory', 'disk', 'latency', 'response_time'])

    def obtener_latencias(self):
        """
        Obtiene las latencias para todos los servidores utilizando ping.
        """
        latencies = []
        for server in self.servers:
            try:
                resultado = subprocess.check_output(f"ping -c 4 {server}", shell=True, text=True)
                for linea in resultado.splitlines():
                    if "rtt min/avg/max/mdev" in linea:
                        latencia_promedio = float(linea.split('=')[1].split('/')[1])
                        latencies.append(latencia_promedio)
                        break
            except Exception as e:
                print(f"Error al obtener la latencia para {server}: {e}")
                latencies.append(float('inf'))  # Latencia infinita si falla
        return latencies

    def obtener_metricas_sistema(self):
        """
        Obtiene métricas del sistema en tiempo real.
        """
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, memory, disk

    def run_round_robin(self, latencies):
        """
        Ejecuta la simulación utilizando el algoritmo Round Robin.
        """
        rr = RoundRobin(self.servers)
        for i, server in enumerate(self.servers):
            cpu, memory, disk = self.obtener_metricas_sistema()
            response_time = latencies[i] * (1 + (cpu / 100))  # Ajustar tiempo según CPU
            self.results = self.results.append({
                'server': server,
                'cpu': cpu,
                'memory': memory,
                'disk': disk,
                'latency': latencies[i],
                'response_time': response_time
            }, ignore_index=True)

    def run_least_connections(self, latencies):
        """
        Ejecuta la simulación utilizando el algoritmo Least Connections.
        """
        lc = LeastConnections(self.servers)
        for i, server in enumerate(self.servers):
            cpu, memory, disk = self.obtener_metricas_sistema()
            response_time = latencies[i] * (1 + (disk / 100))  # Ajustar tiempo según disco
            self.results = self.results.append({
                'server': server,
                'cpu': cpu,
                'memory': memory,
                'disk': disk,
                'latency': latencies[i],
                'response_time': response_time
            }, ignore_index=True)

    def run_tcp_vegas(self, latencies):
        """
        Ejecuta la simulación utilizando el algoritmo TCP Vegas.
        """
        vegas = TCPVegas()
        for i, server in enumerate(self.servers):
            cpu, memory, disk = self.obtener_metricas_sistema()
            vegas.updateRTT(latencies[i])
            window_adjustment = vegas.adjustWindowSize()
            response_time = latencies[i] * (1 + (memory / 100))  # Ajustar tiempo según memoria
            self.results = self.results.append({
                'server': server,
                'cpu': cpu,
                'memory': memory,
                'disk': disk,
                'latency': latencies[i],
                'response_time': response_time
            }, ignore_index=True)

    def run_simulation(self):
        """
        Ejecuta todas las simulaciones y almacena los resultados.
        """
        latencies = self.obtener_latencias()
        self.run_round_robin(latencies)
        self.run_least_connections(latencies)
        self.run_tcp_vegas(latencies)

if __name__ == "__main__":
    servers = ["google.com", "example.com", "localhost"]  # Lista de servidores reales
    sim = LoadSimulation(servers)
    sim.run_simulation()
    print(sim.results)


