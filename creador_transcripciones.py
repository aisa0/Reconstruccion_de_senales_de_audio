import os
import json
import pandas as pd
import re
from deepgram import DeepgramClient, PrerecordedOptions
from config import api_key

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

# Función principal para transcribir y guardar resultados
def transcribir_y_guardar(input_dir, output_dir, nombre_archivo_csv):
    os.makedirs(output_dir, exist_ok=True)
    deepgram = DeepgramClient(api_key)

    # Inicializar una lista para almacenar resultados
    resultados = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.mp3'):
            path_to_file = os.path.join(input_dir, filename)

            # Transcribir el archivo de audio
            with open(path_to_file, 'rb') as buffer_data:
                payload = {'buffer': buffer_data}
                options = PrerecordedOptions(punctuate=True, model="enhanced", language="es-419")
                response = deepgram.listen.rest.v('1').transcribe_file(payload, options)
                json_response = response.to_json()
                data = json.loads(json_response)

                # Obtener transcripción y confianza
                transcript = data['results']['channels'][0]['alternatives'][0]['transcript']
                confidence = data['results']['channels'][0]['alternatives'][0]['confidence']

                # Extraer información del nombre del archivo
                posicion_grabada, posicion_grabacion, hablante = extraer_info(filename)

                # Almacenar resultados
                resultados.append({
                    "Nombre Grabación": filename,
                    "Confiabilidad (Deepgram)": confidence,
                    "Distancia (m)": calcular_distancia(posicion_grabada, posicion_grabacion),
                    "Posición Grabada": posicion_grabada,
                    "Posición de Grabación": posicion_grabacion,
                    "Hablante": hablante
                })

                # Guardar la transcripción
                output_path = os.path.join(output_dir, f'transcripcion_{os.path.splitext(filename)[0]}.txt')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print(f"Transcripción guardada en: {output_path}")

    # Convertir los resultados a un DataFrame y guardar en CSV
    df_resultados = pd.DataFrame(resultados)
    ruta_csv = os.path.join(output_dir, nombre_archivo_csv)

    # Ordenar el DataFrame por la columna 'Distancia' de menor a mayor
    df_resultados = df_resultados.sort_values(by='Distancia (m)')
    
    df_resultados.to_csv(ruta_csv, index=False, encoding='utf-8-sig')
    print(f'Archivo CSV creado y guardado como {ruta_csv}')

# Función para calcular la distancia basada en la posición
def calcular_distancia(posicion_grabada, posicion_grabacion):
    if posicion_grabada == posicion_grabacion:
        return 0
    elif posicion_grabada in ['1', '2']:
        return 5.38
    elif posicion_grabada in ['3', '4']:
        return 3.40
    elif posicion_grabada == '5':
        return 1.50
    elif posicion_grabada == '6':
        return 1.47
    elif posicion_grabada == '8':
        return 1.57
    else:
        return None