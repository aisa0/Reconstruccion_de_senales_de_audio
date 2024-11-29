import os
import pandas as pd
import re
import subprocess

def ejecutar_wer(archivo_wer, archivo_referencia, archivo_hipotesis, carpeta_salida):
    resultado = subprocess.run(
        ['python', archivo_wer, archivo_referencia, archivo_hipotesis],
        capture_output=True, text=True
    )

    # Obtener el nombre del archivo de hipótesis sin la extensión
    nombre_hipotesis = os.path.splitext(os.path.basename(archivo_hipotesis))[0]
    archivo_salida = os.path.join(carpeta_salida, f'WER_{nombre_hipotesis}.txt')

    # Guardar el resultado en un archivo de salida
    with open(archivo_salida, 'w', encoding='utf-8') as file:
        file.write(resultado.stdout)

def calcular_WER(archivo_wer, archivo_referencia, carpeta_hipotesis, carpeta_salida):
    os.makedirs(carpeta_salida, exist_ok=True)  # Crear carpeta de salida si no existe

    for nombre_archivo in os.listdir(carpeta_hipotesis):
        if nombre_archivo.startswith('transcripcion_') and nombre_archivo.endswith('.txt'):
            archivo_hipotesis = os.path.join(carpeta_hipotesis, nombre_archivo)
            ejecutar_wer(archivo_wer, archivo_referencia, archivo_hipotesis, carpeta_salida)

def extract_info_from_filename(filename):
    # Expresión regular actualizada para capturar los nombres de archivo
    pattern = r'WER_transcripcion(?:_denoised)?_Grabacion1_Punto(\d+)_TomadaEnPunto(\d+)_(.+?)(?:_amplificado)?\.txt'
    match = re.match(pattern, filename)
    if match:
        punto_x = match.group(1)
        tomada_en_punto_y = match.group(2)
        hablante = match.group(3)
        return punto_x, tomada_en_punto_y, hablante
    else:
        return None, None, None

def extract_wer_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        match = re.search(r'WER:\s*(\d+\.\d+)%', content)
        if match:
            return match.group(1)
        else:
            return None

def process_wer_files(folder):
    data = {}
    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder, filename)
            punto_x, tomada_en_punto_y, hablante = extract_info_from_filename(filename)
            wer = extract_wer_from_file(file_path)
            if punto_x is not None and tomada_en_punto_y is not None and wer is not None:
                nombre_grabacion = f'Grabacion1_Punto{punto_x}_TomadaEnPunto{tomada_en_punto_y}_{hablante}'
                data[nombre_grabacion] = wer
                print(f'Extraído: {nombre_grabacion} con WER: {wer}')
    return data

def insertar_columna_wer(df_resultados, wer_data):
    # Si la columna WER (%) ya existe, eliminarla para evitar duplicados
    if 'WER (%)' in df_resultados.columns:
        df_resultados.drop(columns=['WER (%)'], inplace=True)

    # Agregar la columna WER (%) con valores iniciales como NaN
    df_resultados['WER (%)'] = None

    # Actualizar el DataFrame con los datos de WER
    for index, row in df_resultados.iterrows():
        nombre_grabacion = row['Nombre Grabación']
        for key in wer_data.keys():
            if key in nombre_grabacion:
                df_resultados.at[index, 'WER (%)'] = wer_data[key]
                print(f'Actualizado: {nombre_grabacion} con WER: {wer_data[key]}')
                break

    # Reorganizar las columnas para que 'WER (%)' sea la segunda
    columns = df_resultados.columns.tolist()
    if 'WER (%)' in columns:
        columns.remove('WER (%)')
    columns.insert(1, 'WER (%)')
    df_resultados = df_resultados[columns]

    return df_resultados
