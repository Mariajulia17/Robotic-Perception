"""Filtro de mediana con cola FIFO de cinco lecturas, basado en C2.2."""
from collections import deque
from statistics import median

class FiltroFIFO:
    def __init__(self, tamano=5):
        self.tamano = tamano
        self.readings = deque(maxlen=tamano)

    def actualizar(self, nuevaLectura):
        if nuevaLectura is None:
            return None  # No inventar lecturas si un sensor no esta disponible.
        self.readings.append(float(nuevaLectura))
        if len(self.readings) < self.tamano:
            return None  # FIFO todavia incompleta
        return float(median(self.readings))
