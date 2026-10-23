
## Funciones
- Laptop envia `CAPTURE`.
- Raspberry captura una imagen USB y lee sensores reales.
- Laptop recibe imagen y mediciones; guarda JPG y CSV con el mismo timestamp.
- Cada canal numerico dispone de mediana FIFO de 5 lecturas. Antes de 5 lecturas el valor filtrado esta vacio.

## Hardware
- Camara USB, 'cv2.VideoCapture(0)' (ajustar indice si es necesario).
- HC-SR04 #1: trigger=GPIO23, echo=GPIO24 con divisor de voltaje obligatorio para bajar ECHO 5 V a 3.3 V.
- HC-SR04 #2: habilitar en 'Raspberry/sensores.py' tras conectar; pines  GPIO17 y GPIO27.
- **IMPORTANTEEEEEEEEE:** LDR y temperatura requieren definir el circuito/modelo. Las lineas estan preparadas pero no activadas; retornan `None` hasta configurar hardware real. 

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

Hay que ver que ondis primero con lo fisico para cambiar lo de el ldr y esoooooo
