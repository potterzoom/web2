class LeastConnections:
    """
    Implementa el algoritmo de Least Connections para el balanceo de carga.
    """

    def __init__(self, servers):
        self.servers = {server: 0 for server in servers}
        self.availability = {server: True for server in servers}  # Agregado para disponibilidad

    def assign_request(self, consider_latency=False, latencies=None, availability=None):
        """
        Asigna una solicitud al servidor con menor carga o menor latencia.
        :param consider_latency: Si True, asigna basado en latencia.
        :param latencies: Lista de latencias de los servidores.
        :param availability: Lista de disponibilidad de los servidores (True si disponible, False si no).
        :return: El servidor asignado.
        """
        if consider_latency and latencies:
            # Selecciona el servidor con la menor latencia y menor carga
            if availability:
                # Considera disponibilidad de los servidores
                available_servers = [s for s in self.servers if availability[list(self.servers.keys()).index(s)]]
                latencies = [latencies[list(self.servers.keys()).index(s)] for s in available_servers]
                least_loaded_server = min(available_servers, key=lambda s: (latencies[list(self.servers.keys()).index(s)], self.servers[s]))
            else:
                least_loaded_server = min(
                    self.servers,
                    key=lambda s: (latencies[list(self.servers.keys()).index(s)], self.servers[s])
                )
        else:
            # Selecciona el servidor con el menor número de conexiones
            least_loaded_server = min(self.servers, key=self.servers.get)

        # Incrementa la carga del servidor seleccionado
        self.servers[least_loaded_server] += 1
        return least_loaded_server

    def release_request(self, server):
        """
        Libera una conexión del servidor especificado.
        :param server: Servidor a liberar.
        """
        if server not in self.servers:
            raise ValueError("El servidor especificado no existe.")
        
        if self.servers[server] == 0:
            raise ValueError("El servidor no tiene conexiones activas para liberar.")
        
        self.servers[server] -= 1

    def get_server_loads(self):
        """
        Devuelve el estado actual de carga de los servidores.
        """
        return self.servers




