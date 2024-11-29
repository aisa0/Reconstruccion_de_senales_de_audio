# Importar las bibliotecas
import librosa
import soundfile as sf
import numpy as np
import os

def amplificar_audios(carpeta_audios, carpeta_salida):

    # Crear la carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Iterar sobre todos los archivos en la carpeta
    for archivo in os.listdir(carpeta_audios):
        if archivo.endswith(".mp3"):
            # Ruta completa del archivo de audio
            audio_path = os.path.join(carpeta_audios, archivo)

            # Cargar el archivo de audio
            y, sr = librosa.load(audio_path, sr=None)

            # Calcular el nivel máximo de la señal
            max_amplitude = np.max(np.abs(y))

            # Calcular el factor de amplificación para llevar el pico a 0 dB
            if max_amplitude > 0:
                target_amplitude = 1.0  # Amplitud en escala de -1 a 1
                amplification_factor = target_amplitude / max_amplitude

                # Amplificar la señal
                y_amplificado = y * amplification_factor

                # Obtener el nombre del archivo sin la extensión
                base_name = os.path.splitext(archivo)[0]

                # Guardar el audio amplificado con el nuevo nombre
                output_path = os.path.join(carpeta_salida, f"{base_name}_amplificado.mp3")  # Nombre del archivo de salida
                sf.write(output_path, y_amplificado, sr)

                print(f"Archivo amplificado guardado como {output_path}")

            else:
                print(f"El audio {archivo} está vacío o no tiene amplitud.")
