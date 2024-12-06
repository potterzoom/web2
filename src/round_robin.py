class RoundRobin:
    def __init__(self, servers):
        """
        Inicializa la clase con una lista de servidores.
        :param servers: Lista de servidores.
        """
        self.servers = servers
        self.current_index = 0

    def assign_request(self, consider_latency=False, latencies=None, availability=None):
        """
        Asigna una solicitud a un servidor usando Round Robin o basado en latencias.
        :param consider_latency: Si True, asigna basado en latencia.
        :param latencies: Lista de latencias de los servidores.
        :param availability: Lista de disponibilidad de los servidores (True si disponible, False si no).
        :return: El servidor asignado.
        """
        if consider_latency and latencies:
            # Asigna al servidor con menor latencia si está habilitado
            if availability:
                # Filtrar los servidores disponibles y sus latencias correspondientes
                available_servers = [i for i, available in enumerate(availability) if available]
                available_latencies = [latencies[i] for i in available_servers]

                if not available_latencies:
                    return None  # Si no hay servidores disponibles, retornar None

                # Asigna al servidor con la menor latencia de los disponibles
                selected_server = min(range(len(available_latencies)), key=lambda i: available_latencies[i])
                return self.servers[available_servers[selected_server]]
            else:
                # Si no se considera disponibilidad, asigna al servidor con la menor latencia
                selected_server = min(range(len(self.servers)), key=lambda i: latencies[i])
                return self.servers[selected_server]
        else:
            # Asigna usando Round Robin
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server

