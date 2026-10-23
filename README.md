# Sensor Data Processing for the Rover

Proyecto nuevo para Raspberry Pi 5 (servidor TCP) y Windows / PyCharm (cliente).

## Funciones
- Laptop envia `CAPTURE`.
- Raspberry captura una imagen USB y lee sensores reales.
- Laptop recibe imagen y mediciones; guarda JPG y CSV con el mismo timestamp.
- Cada canal numerico dispone de mediana FIFO de 5 lecturas. Antes de 5 lecturas el valor filtrado esta vacio.
- No hay simulacion ni datos ficticios.

## Hardware
- Camara USB, `cv2.VideoCapture(0)` (ajustar indice si es necesario).
- HC-SR04 #1: trigger=GPIO23, echo=GPIO24 con divisor de voltaje obligatorio para bajar ECHO 5 V a 3.3 V.
- HC-SR04 #2: habilitar en `Raspberry/sensores.py` tras conectar; pines sugeridos GPIO17 y GPIO27 requieren revision de cableado.
- LDR y temperatura requieren definir el circuito/modelo. Las lineas estan preparadas pero no activadas; retornan `None` hasta configurar hardware real. Pi 5 no tiene entrada ADC incorporada para leer LDR resistivo directamente.
- Nunca alimentar un GPIO con 5 V. Compartir tierra adecuadamente.

## Instalar en Raspberry Pi (preferir entorno virtual con paquetes apt o venv)
```bash
sudo apt update
sudo apt install -y python3-opencv python3-gpiozero python3-lgpio
```

## Servidor (en Raspberry)
```bash
cd Rover_Sensores_Real/Raspberry
python3 servidor.py
```

## Cliente (en Windows, desde la raiz del proyecto)
```powershell
python Laptop/cliente.py --ip IP_DE_LA_RASPBERRY --muestras 10 --intervalo 1
```

Los archivos se guardan bajo `Datos/` en Windows. Las lecturas sin dispositivo conectado se guardan vacias en CSV; no son resultados experimentales. Si se desconecta un sensor, hay que corregir el cableado y reiniciar el filtro para evitar ventanas inconsistentes.

## Pendientes para cumplir el enunciado al 100 %
Configurar LDR, temperatura y segundo ultrasonico con los modelos y conexiones reales. Capturar evidencia de hardware y validar mediciones. El FIFO se aplica en Laptop antes de usar valores numericos para decisiones; las columnas `_fifo` son las que deben usarse. Las columnas crudas son solo registro de diagnostico.
