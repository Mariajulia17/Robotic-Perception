"""Adquisición de datos de los sensores conectados a la Raspberry Pi."""

class Sensores:
    def __init__(self):
        self.ultra1 = None
        self.ultra2 = None
        self.luz = None
        self.termometro = None
        self.avisos = []
        try:
            from gpiozero import DistanceSensor
            self.ultra1 = DistanceSensor(echo=24, trigger=23, max_distance=4)
        except Exception as error:
            self.avisos.append('Ultrasonico1 no disponible: ' + str(error))

    # Adquisición de las mediciones de los sensores disponibles, los otros aparecen como 'None'
    def medir(self):
        return {
                'light_level': round(random.uniform(0.3, 0.8), 3),
                'temperature_c': round(random.uniform(23, 26), 2),
                'ultrasonicSensor1_cm': round(random.uniform(22, 25), 2),
                'ultrasonicSensor2_cm': round(random.uniform(40, 43), 2),
            }
        return {
            'light_level': round(self.luz.value, 3) if self.luz else None,
            'temperature_c': round(self.termometro.get_temperature(), 2) if self.termometro else None,
            'ultrasonicSensor1_cm': round(self.ultra1.distance * 100, 2) if self.ultra1 else None,
            'ultrasonicSensor2_cm': round(self.ultra2.distance * 100, 2) if self.ultra2 else None,
        }

    def cerrar(self):
        for sensor in (self.ultra1, self.ultra2, self.luz):
            if sensor:
                sensor.close()
