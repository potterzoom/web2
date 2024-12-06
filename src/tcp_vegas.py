import time
import psutil
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class TCPVegas:
    """
    Clase que implementa el algoritmo TCP Vegas para el control de flujo en redes.
    """

    def __init__(self):
        self.baseRTT = float('inf')
        self.currentRTT = 0
        self.window_size = 1
        self.total_adjustments = 0
        self.adjustment_times = []
        self.history = []  # Para almacenar historial de ajustes

    def updateRTT(self, rtt):
        """
        Actualiza el RTT actual y el RTT base si el nuevo RTT es menor.
        """
        if not isinstance(rtt, (int, float)) or rtt <= 0:
            raise ValueError("El RTT debe ser un número positivo.")
        
        self.currentRTT = rtt
        self.baseRTT = min(self.baseRTT, rtt)

    def adjustWindowSize(self, cpu=None):
        """
        Ajusta el tamaño de la ventana basado en RTT y carga de CPU.
        """
        cpu_load = psutil.cpu_percent(interval=0.1) if cpu is None else cpu  # Si no se pasa `cpu`, se usa la carga real
        adjustment_start = time.time()

        if self.currentRTT > self.baseRTT or cpu_load > 80:
            self.window_size = max(1, self.window_size - 1)  # Reducir ventana
            reason = "Reducir ventana: RTT alto o CPU sobrecargada"
        else:
            self.window_size += 1  # Incrementar ventana
            reason = "Incrementar ventana: RTT bajo y CPU estable"

        adjustment_end = time.time()
        self.adjustment_times.append(adjustment_end - adjustment_start)
        self.total_adjustments += 1

        # Guardar historial
        self.history.append({
            "current_rtt": self.currentRTT,
            "base_rtt": self.baseRTT,
            "window_size": self.window_size,
            "cpu_load": cpu_load,
            "reason": reason
        })

        return self.window_size

    def get_metrics(self):
        """
        Devuelve métricas actuales del algoritmo.
        """
        avg_adjustment_time = (
            sum(self.adjustment_times) / len(self.adjustment_times)
            if self.adjustment_times else 0
        )

        return {
            "current_rtt": self.currentRTT,
            "base_rtt": self.baseRTT,
            "window_size": self.window_size,
            "total_adjustments": self.total_adjustments,
            "average_adjustment_time": avg_adjustment_time,
        }

    def simulate_rtt_adjustments(self, num_iterations=20):
        """
        Simula ajustes de ventana modificando dinámicamente el RTT.
        :param num_iterations: Número de iteraciones de simulación.
        """
        print("Simulando ajustes de ventana...")
        for _ in range(num_iterations):
            simulated_rtt = self.baseRTT + (10 - self.window_size) * 2  # RTT dinámico
            self.updateRTT(simulated_rtt)
            self.adjustWindowSize()
        print("Simulación completada.")

    def plot_history(self):
        """
        Grafica la evolución del RTT, baseRTT y tamaño de la ventana.
        """
        rtts = [entry["current_rtt"] for entry in self.history]
        base_rtts = [entry["base_rtt"] for entry in self.history]
        window_sizes = [entry["window_size"] for entry in self.history]

        plt.figure(figsize=(12, 6))
        plt.plot(rtts, label="RTT Actual", marker="o")
        plt.plot(base_rtts, label="RTT Base", linestyle="--")
        plt.plot(window_sizes, label="Tamaño de Ventana", marker="x")
        plt.title("Evolución de RTT y Tamaño de Ventana")
        plt.xlabel("Iteración")
        plt.ylabel("Valor")
        plt.legend()
        plt.grid()
        plt.show()


