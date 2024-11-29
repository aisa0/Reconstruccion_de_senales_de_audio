import librosa
import numpy as np
import os
import pandas as pd
import re

# Función para calcular el SNR de un archivo
def calcular_snr(archivo_audio):
    # Cargar el archivo de audio
    y, sr = librosa.load(archivo_audio, sr=None)

    # Calcular la potencia de la señal
    signal_power = np.mean(y ** 2)

    # Estimar el ruido (suponiendo que es el complemento de la señal)
    noise_power = np.mean((y - librosa.effects.hpss(y)[0]) ** 2)

    # Calcular SNR
    snr = 10 * np.log10(signal_power / noise_power)

    return snr

# Función para extraer información del nombre del archivo
def extraer_info(nombre_archivo):
    # Definir el patrón para extraer Posición Grabada, Posición de Grabación y Hablante
    patron = r'_Punto(\d+)_TomadaEnPunto(\d+)_(\w+)'
    coincidencia = re.search(patron, nombre_archivo)

    if coincidencia:
        posicion_grabada = coincidencia.group(1)
        posicion_grabacion = coincidencia.group(2)
        hablante = coincidencia.group(3)

        # Eliminar '_amplificado' si está presente
        if "_amplificado" in hablante:
            hablante = hablante.replace("_amplificado", "")
    else:
        posicion_grabada = "Desconocido"
        posicion_grabacion = "Desconocido"
        hablante = "Desconocido"

    return posicion_grabada, posicion_grabacion, hablante

# Función para agregar SNR a un CSV existente y guardar el archivo en una nueva ubicación
def agregar_snr_a_csv(carpeta_entrada, carpeta_salida, nombre_archivo_csv):
    print("Calculando SNR para los archivos en:", carpeta_entrada)

    # Cargar el archivo CSV existente
    archivo_csv = os.path.join(carpeta_salida, nombre_archivo_csv)
    df = pd.read_csv(archivo_csv, encoding='utf-8')

    # Eliminar la columna SNR si existe
    if 'SNR (dB)' in df.columns:
        df.drop(columns=['SNR (dB)'], inplace=True)

    # Crear la columna SNR en el índice 1 (segunda columna)
    df.insert(1, 'SNR (dB)', np.nan)  # Insertar la columna SNR en el índice 1

    # Listar todos los archivos .mp3 en la carpeta de entrada
    mp3_files = [f for f in os.listdir(carpeta_entrada) if f.endswith('.mp3')]

    # Calcular el SNR y agregar a la DataFrame
    for archivo in mp3_files:
        # Ruta completa del archivo de audio
        ruta_audio = os.path.join(carpeta_entrada, archivo)

        # Calcular SNR
        snr = calcular_snr(ruta_audio)

        # Extraer información del nombre del archivo
        posicion_grabada, posicion_grabacion, hablante = extraer_info(archivo)

        # Verificar si el nombre de la grabación está en el DataFrame
        if archivo in df['Nombre Grabación'].values:
            # Actualizar la fila correspondiente en el DataFrame
            df.loc[df['Nombre Grabación'] == archivo, 'SNR (dB)'] = snr
            df.loc[df['Nombre Grabación'] == archivo, 'Posición Grabada'] = posicion_grabada
            df.loc[df['Nombre Grabación'] == archivo, 'Posición de Grabación'] = posicion_grabacion
            df.loc[df['Nombre Grabación'] == archivo, 'Hablante'] = hablante
            
            print(f"Actualizado SNR para {archivo}: {snr:.2f} dB")
        else:
            print(f"{archivo} no encontrado en el archivo CSV.")

    # Guardar el DataFrame actualizado en la ubicación especificada
    df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')

    print(f'Archivo CSV actualizado guardado como {archivo_csv}')
