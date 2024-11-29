import os
import re
from pydub import AudioSegment
import pandas as pd

hablantes = []

def extract_info_from_filename(filename):
    pattern = r'transcripcion(?:_denoised)?_Grabacion1_Punto(\d+)_TomadaEnPunto(\d+)_(\w+)(?:_amplificado)?\.txt$'
    match = re.match(pattern, filename)
    
    
    if match:
        punto_x = int(match.group(1))
        punto_y = int(match.group(2))
        hablante = match.group(3)
        # Si el hablante tiene el sufijo '_amplificado', lo eliminamos
        if hablante.endswith('_amplificado'):
            hablante = hablante.replace('_amplificado', '')
        if hablante not in hablantes:  # Evitamos duplicados
            hablantes.append(hablante)
           
        return {"punto_x": punto_x, "punto_y": punto_y, "hablante": hablante}
    return None

def calcular_velocidad_lectura(audio_path, transcripcion):
    audio = AudioSegment.from_file(audio_path)
    duracion_minutos = len(audio) / 60000.0
    num_palabras = len(transcripcion.split())
    wpm = num_palabras / duracion_minutos if duracion_minutos > 0 else 0
    return wpm

def calcular_distancia(posicion_grabada, posicion_grabacion):
    if posicion_grabada == posicion_grabacion:
        return 0
    elif posicion_grabada in [1, 2]:
        return 5.38
    elif posicion_grabada in [3, 4]:
        return 3.40
    elif posicion_grabada == 5:
        return 1.50
    elif posicion_grabada == 6:
        return 1.47
    elif posicion_grabada == 8:
        return 1.57
    return None

def actualizar_csv_con_velocidad(grabaciones_dir, transcripciones_dir, output_csv):
    if os.path.exists(output_csv):
        df_resultados = pd.read_csv(output_csv)
    else:
        df_resultados = pd.DataFrame(columns=["Nombre Grabación", "Speed Rate (wpm)", "Posición Grabada", "Posición de Grabación", "Hablante", "Distancia (m)"])

    velocidades_dict = {}
    velocidades_hablante0_dict = {}
    velocidades_hablante1_dict = {}
    total_velocidad_hablante0 = 0
    total_velocidad_hablante1 = 0
    total_grabaciones_hablante_0 = 0
    total_grabaciones_hablante_1 = 0

    for filename in os.listdir(grabaciones_dir):
        if filename.endswith(".mp3"):
            audio_path = os.path.join(grabaciones_dir, filename)
            
            # Extraer información del nombre del archivo .mp3
            pattern = r'^(?:denoised_)?Grabacion1_Punto(\d+)_TomadaEnPunto(\d+)_(\w+)(?:_amplificado)?\.mp3$'
            match = re.match(pattern, filename)
            if match:
                posicion_grabada = int(match.group(1))
                posicion_grabacion = int(match.group(2))
                hablante = match.group(3)
                nombre_grabacion = filename
            else:
                print(f"Nombre de archivo no coincide con el patrón esperado: {filename}")
                continue

            transcripcion = None
            for transcripcion_file in os.listdir(transcripciones_dir):
                info = extract_info_from_filename(transcripcion_file)
                if info and info["punto_x"] == posicion_grabada and info["punto_y"] == posicion_grabacion and info["hablante"] == hablante:

                    with open(os.path.join(transcripciones_dir, transcripcion_file), 'r', encoding='utf-8') as file:
                        transcripcion = file.read()
                    break

            # Se toman solo las grabaciones de cerca para no repetir
            if transcripcion and posicion_grabacion != 7 and hablante == str(hablantes[0]):
                wpm = calcular_velocidad_lectura(audio_path, transcripcion)
                velocidades_hablante0_dict[nombre_grabacion] = wpm
                total_velocidad_hablante0 += wpm
                total_grabaciones_hablante_0 += 1

            elif transcripcion and posicion_grabacion != 7 and hablante == str(hablantes[1]):
                # Se toman solo las grabaciones de cerca para no repetir
                wpm = calcular_velocidad_lectura(audio_path, transcripcion)
                velocidades_hablante1_dict[nombre_grabacion] = wpm
                total_velocidad_hablante1 += wpm
                total_grabaciones_hablante_1 += 1
                    
            else:    
                print(f"Archivo: {filename} es de lejos por lo que no se analizará")
            

    if total_grabaciones_hablante_0 > 0:
        velocidad_promedio = total_velocidad_hablante0 / total_grabaciones_hablante_0
        print(f'Velocidad promedio de habla para {hablantes[0]}: {velocidad_promedio} wpm')
        
        # Calcular la varianza
        varianza = sum([(wpm - velocidad_promedio) ** 2 for wpm in velocidades_hablante0_dict.values()]) / total_grabaciones_hablante_0
        print(f'Varianza de la velocidad del habla para {hablantes[0]}: {varianza}')
    else:
        print('No se pudo calcular la velocidad promedio y la varianza porque no se procesaron grabaciones.')

    if total_grabaciones_hablante_1 > 0:
        velocidad_promedio = total_velocidad_hablante1 / total_grabaciones_hablante_1
        print(f'Velocidad promedio de habla para {hablantes[1]}: {velocidad_promedio} wpm')
        
        # Calcular la varianza
        varianza = sum([(wpm - velocidad_promedio) ** 2 for wpm in velocidades_hablante1_dict.values()]) / total_grabaciones_hablante_1
        print(f'Varianza de la velocidad del habla para {hablantes[1]}: {varianza}')
    else:
        print('No se pudo calcular la velocidad promedio y la varianza porque no se procesaron grabaciones.')

    # Verificar si la columna 'Speed Rate (wpm)' existe, y agregarla si no
    if 'Speed Rate (wpm)' not in df_resultados.columns:
        df_resultados['Speed Rate (wpm)'] = None

    # Unir los diccionarios
    velocidades_dict.update(velocidades_hablante0_dict)
    velocidades_dict.update(velocidades_hablante1_dict)

    for index, row in df_resultados.iterrows():
        nombre_grabacion = row['Nombre Grabación']
        if nombre_grabacion in velocidades_dict:
            df_resultados.at[index, 'Speed Rate (wpm)'] = velocidades_dict[nombre_grabacion]
            print(f'Actualizado: {nombre_grabacion} con velocidad: {velocidades_dict[nombre_grabacion]}')

    df_resultados.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"Archivo {output_csv} actualizado con éxito.")
