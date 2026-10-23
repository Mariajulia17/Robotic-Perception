"""Cliente Windows: solicita datos, aplica FIFO y guarda CSV + imagen."""
import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import socket
import struct
import time

from filtroFIFO import FiltroFIFO

CAMPOS_SENSOR = ['light_level', 'temperature_c', 'ultrasonicSensor1_cm', 'ultrasonicSensor2_cm']
CAMPOS_CSV = ['timestamp', 'image_name', 'image_width', 'image_height',
              'light_level', 'temperature_c', 'ultrasonicSensor1_cm', 'ultrasonicSensor2_cm',
              'light_level_fifo', 'temperature_c_fifo',
              'ultrasonicSensor1_cm_fifo', 'ultrasonicSensor2_cm_fifo']


def recibir_exacto(conexion, total):
    datos = bytearray()
    while len(datos) < total:
        bloque = conexion.recv(total - len(datos))
        if not bloque:
            raise ConnectionError('Conexion terminada antes de completar el paquete')
        datos.extend(bloque)
    return bytes(datos)


def recibir_muestra(ip, puerto):
    with socket.create_connection((ip, puerto), timeout=10) as conexion:
        conexion.settimeout(10)
        conexion.sendall(b'CAPTURE')
        longitud = struct.unpack('!I', recibir_exacto(conexion, 4))[0]
        if longitud > 100000:
            raise ValueError('Cabecera demasiado grande')
        datos = json.loads(recibir_exacto(conexion, longitud).decode('utf-8'))
        tamano = struct.unpack('!I', recibir_exacto(conexion, 4))[0]
        if tamano > 15000000:
            raise ValueError('Imagen demasiado grande')
        imagen = recibir_exacto(conexion, tamano)
        return datos, imagen


def ejecutar(ip, puerto, muestras, intervalo, carpeta):
    carpeta = Path(carpeta)
    imagenes = carpeta / 'imagenes'
    imagenes.mkdir(parents=True, exist_ok=True)
    archivo_csv = carpeta / 'sensores.csv'
    archivo_nuevo = not archivo_csv.exists() or archivo_csv.stat().st_size == 0
    filtros = {campo: FiltroFIFO(5) for campo in CAMPOS_SENSOR}
    print('Cliente activo | Servidor {}:{} | muestras {}'.format(ip, puerto, muestras))
    with archivo_csv.open('a', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS_CSV)
        if archivo_nuevo:
            escritor.writeheader()
        for numero in range(muestras):
            try:
                respuesta, imagen = recibir_muestra(ip, puerto)
                if respuesta.get('status') != 'ok':
                    raise ValueError('Respuesta no valida del servidor')
                # Timestamp unico: esta misma cadena va al CSV y al nombre del JPG.
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                nombreImagen = 'arm_camera_{}.jpg'.format(timestamp)
                # Solo guardar el CSV si tambien se pudo guardar la imagen.
                (imagenes / nombreImagen).write_bytes(imagen)
                fila = {
                    'timestamp': timestamp, 'image_name': nombreImagen,
                    'image_width': respuesta['image_width'],
                    'image_height': respuesta['image_height'],
                }
                mediciones = respuesta.get('mediciones', {})
                for campo in CAMPOS_SENSOR:
                    lectura = mediciones.get(campo)
                    fila[campo] = lectura
                    fila[campo + '_fifo'] = filtros[campo].actualizar(lectura)
                escritor.writerow(fila)
                archivo.flush()
                print('Muestra {} | {} | ultrasonico1 filtrado: {}'.format(
                    numero + 1, timestamp, fila['ultrasonicSensor1_cm_fifo']))
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
                print('No se guardo esta muestra:', error)
            if numero < muestras - 1:
                time.sleep(intervalo)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1')
    parser.add_argument('--puerto', type=int, default=5050)
    parser.add_argument('--muestras', type=int, default=10)
    parser.add_argument('--intervalo', type=float, default=1)
    parser.add_argument('--datos', default=str(Path(__file__).resolve().parents[1] / 'Datos'))
    args = parser.parse_args()
    ejecutar(args.ip, args.puerto, args.muestras, args.intervalo, args.datos)
