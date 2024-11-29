import os
import re
import numpy as np
import librosa
import pandas as pd

hablantes = []
frecuencias_hablante0 = {}
frecuencias_hablante1 = {}
frecuencias_fundamentales = {}

def extract_info_from_filename(filename):
    pattern = r'^(?:denoised_)?(Grabacion1)_Punto(\d+)_TomadaEnPunto(\d+)_([\w]+)(?:_amplificado)?\.mp3$'
    match = re.match(pattern, filename)
    
    if match:
        grabacion = match.group(1)  # 'Grabacion1'
        punto_x = int(match.group(2))   
        punto_y = int(match.group(3))   
        hablante = match.group(4)  

        # Si el hablante tiene el sufijo '_amplificado', lo eliminamos
        if hablante.endswith('_amplificado'):
            hablante = hablante.replace('_amplificado', '')
        if hablante not in hablantes:  # Evitamos duplicados
            hablantes.append(hablante)
        
        return {"grabacion": grabacion, "punto_x": punto_x, "punto_y": punto_y, "hablante": hablante}
    return None

def calcular_frecuencia_fundamental(audio_path):
    """
    Calcula la frecuencia fundamental promedio y la varianza para un archivo de audio.

    Parámetros:
    audio_path (str): Ruta al archivo de audio.

    Retorna:
    tuple: (frecuencia_promedio, varianza) o (None, None) si no se detectan frecuencias.
    """
    try:
        # Cargar el archivo de audio
        y, sr = librosa.load(audio_path, mono=True)  # Mono porque no separamos por canal
        
        # Calcular la frecuencia fundamental utilizando PYIN
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, 
            fmin=librosa.note_to_hz('E2'),  # 80 Hz (~E2)
            fmax=librosa.note_to_hz('F4')   # 350 Hz (~F4)
        )
        # Filtrar solo las frecuencias fundamentales válidas (donde voiced_flag es True)
        valid_frequencies = f0[voiced_flag]
        
        frecuencia_promedio = np.mean(valid_frequencies)
        varianza = np.var(valid_frequencies)

        return frecuencia_promedio, varianza

    except Exception as e:
        print(f"Error al procesar el archivo {audio_path}: {e}")
        return None, None

def actualizar_csv_con_frecuencia(grabaciones_dir, output_csv):
    """
    Calcula la frecuencia fundamental para cada hablante y actualiza un archivo CSV.

    Parámetros:
    grabaciones_dir (str): Directorio donde se encuentran los archivos de audio.
    output_csv (str): Ruta al archivo CSV donde se guardarán los resultados.
    """
    # Leer el CSV de resultados o crear uno nuevo
    if os.path.exists(output_csv):
        df_resultados = pd.read_csv(output_csv)
    else:
        df_resultados = pd.DataFrame(columns=["Nombre Grabación", "Hablante", 
                                              "Frecuencia Fundamental Promedio (Hz)", 
                                              "Varianza (Hz^2)", 
                                              "Posición Grabada", 
                                              "Posición de Grabación"])

    for filename in os.listdir(grabaciones_dir):
        if filename.endswith(".mp3"):
            audio_path = os.path.join(grabaciones_dir, filename)

            # Extraer información del nombre del archivo
            info = extract_info_from_filename(filename)
            if not info:
                print(f"Nombre de archivo no coincide con el patrón esperado: {filename}")
                continue

            posicion_grabada = info["punto_x"]
            posicion_grabacion = info["punto_y"]
            hablante = info["hablante"]
            nombre_grabacion = filename
            
            # Calcular la frecuencia fundamental solo si el hablante coincide
            if hablante == hablantes[0] and posicion_grabacion != 7:  # Hablante 1
                mean_freq, var_freq = calcular_frecuencia_fundamental(audio_path)
                if mean_freq is not None and var_freq is not None:
                    print(f"{filename}: {mean_freq:.2f} Hz, {var_freq:.2f} Hz^2")

            elif hablante == hablantes[1] and posicion_grabacion != 7:  # Hablante 2
                mean_freq, var_freq = calcular_frecuencia_fundamental(audio_path)
                if mean_freq is not None and var_freq is not None:
                    print(f"{filename}: {mean_freq:.2f} Hz, {var_freq:.2f} Hz^2")
            else:
                print(f"Hablante no reconocido en {filename}")
                continue

            # Crear columnas vacías para nuevas métricas si no existen
            if "Frecuencia Fundamental Promedio (Hz)" not in df_resultados.columns:
                df_resultados["Frecuencia Fundamental Promedio (Hz)"] = None
            if "Varianza f0 (Hz^2)" not in df_resultados.columns:
                df_resultados["Varianza f0 (Hz^2)"] = None
            
            frecuencias_fundamentales[filename] = {
                        "promedio": mean_freq,
                        "varianza": var_freq
                    }
            
            # Actualizar las columnas basándose en coincidencias de "Nombre Grabación"
            for index, row in df_resultados.iterrows():
                nombre_grabacion = row["Nombre Grabación"]
                if nombre_grabacion in frecuencias_fundamentales:
                    df_resultados.at[index, "Frecuencia Fundamental Promedio (Hz)"] = frecuencias_fundamentales[nombre_grabacion]["promedio"]
                    df_resultados.at[index, "Varianza f0 (Hz^2)"] = frecuencias_fundamentales[nombre_grabacion]["varianza"]

        
    # Guardar los resultados en el archivo CSV
    df_resultados.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"Archivo {output_csv} actualizado con éxito.")