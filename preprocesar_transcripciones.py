import os
import re
from unidecode import unidecode

def preprocess_text(text):
    # Convertir a minúsculas
    text = text.lower()

    # Normalizar la puntuación: eliminar caracteres especiales y dejar solo letras, números y espacios
    text = re.sub(r'[^\w\s]', '', text)  # Esto elimina todo excepto letras, números y espacios

    # Reemplazar caracteres acentuados por no acentuados
    text = unidecode(text)

    # Reemplazar múltiples espacios con un solo espacio
    text = re.sub(r'\s+', ' ', text)

    # Eliminar espacios al principio y al final
    text = text.strip()

    return text

def preprocess_single_file(input_file, output_file):
    try:
        # Leer el contenido del archivo
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Procesar el texto
        processed_text = preprocess_text(text)

        # Guardar el texto procesado en el archivo de salida
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(processed_text)

        print(f"Archivo procesado y guardado como: {output_file}")
    except Exception as e:
        print(f"Error procesando {input_file}: {e}")


def preprocess_files(input_directory, output_directory):
    # Crear el directorio de salida si no existe
    os.makedirs(output_directory, exist_ok=True)

    # Recorrer todos los archivos en el directorio de entrada
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):  # Filtrar solo archivos .txt
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)

            # Leer el contenido del archivo
            with open(input_path, 'r', encoding='utf-8') as file:
                text = file.read()

            # Procesar el texto
            processed_text = preprocess_text(text)

            # Guardar el texto procesado en el archivo de salida
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(processed_text)

            print(f"Archivo procesado y guardado: {output_path}")
