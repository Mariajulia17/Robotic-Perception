"""Servidor TCP para Raspberry Pi 5 y sensores reales."""
import argparse
import json
import socket
import struct
import threading
import time

from sensores import Sensores


def recibir_exacto(conexion, total):
    datos = b''
    while len(datos) < total:
        bloque = conexion.recv(total - len(datos))
        if not bloque:
            raise ConnectionError('Conexion cerrada')
        datos += bloque
    return datos


def enviar_paquete(conexion, metadatos, imagen):
    cabecera = json.dumps(metadatos).encode('utf-8')
    conexion.sendall(struct.pack('!I', len(cabecera)))
    conexion.sendall(cabecera)
    conexion.sendall(struct.pack('!I', len(imagen)))
    conexion.sendall(imagen)


class CamaraUSB:
    def __init__(self):
        self.camara = None
        self.lock = threading.Lock()
        import cv2
        self.camara = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if not self.camara.isOpened():
            raise RuntimeError('No se detecto camara USB en /dev/video0')
        self.camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def capturar(self):
        import cv2
        import numpy as np
        with self.lock:
            ok, frame = self.camara.read()
            if not ok:
                raise RuntimeError('Fallo al capturar imagen USB')
            alto, ancho = frame.shape[:2]
            ok, buffer = cv2.imencode('.jpg', frame)
            if not ok:
                raise RuntimeError('Fallo al codificar JPEG')
            return buffer.tobytes(), ancho, alto

    def cerrar(self):
        if self.camara:
            self.camara.release()


def iniciar(host, puerto):
    sensores = Sensores()
    camara = CamaraUSB()
    print('Servidor TCP activo en {}:{}'.format(host, puerto))
    for aviso in sensores.avisos:
        print('AVISO:', aviso)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((host, puerto))
            servidor.listen(3)
            while True:
                conexion, direccion = servidor.accept()
                with conexion:
                    conexion.settimeout(10)
                    try:
                        solicitud = recibir_exacto(conexion, 7)
                        if solicitud != b'CAPTURE':
                            print('Solicitud no reconocida', direccion)
                            continue
                        imagen, ancho, alto = camara.capturar()
                        mediciones = sensores.medir()
                        enviar_paquete(conexion, {
                            'image_width': ancho, 'image_height': alto,
                            'mediciones': mediciones,
                            'status': 'ok',
                        }, imagen)
                        print('Captura enviada a', direccion[0])
                    except (OSError, ValueError, RuntimeError) as error:
                        print('Error de captura:', error)
    finally:
        sensores.cerrar()
        camara.cerrar()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--puerto', type=int, default=5050)
    args = parser.parse_args()
    iniciar(args.host, args.puerto)
