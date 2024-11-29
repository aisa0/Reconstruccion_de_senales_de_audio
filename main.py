import os
import shutil
import subprocess
import pandas as pd
from pathlib import Path
from amplificador import amplificar_audios
from aplica_denoiser import aplica_denoiser
from creador_transcripciones import transcribir_y_guardar

# Verificar si cada script existe en el directorio actual
def check_scripts():
    scripts = {
        "amplificador": "/content/amplificador.py",
        "aplica_denoiser": "/content/aplica_denoiser.py",
        "creador_transcripciones": "/content/creador_transcripciones.py",
    }
    for name, path in scripts.items():
        if not Path(path).is_file():
            raise FileNotFoundError(f"{path} no encontrado. Asegúrate de que todos los scripts estén en el directorio.")

# Definir una función para ejecutar cada script
def ejecutar_amplificador():
    print("Amplificando audios...")

    # Directorios de entrada y salida
    input_directory = "/content/Grabaciones_de_lejos"
    output_directory = "/content/Grabaciones_amplificadas"

    # Llamada a la función amplificar_audios
    amplificar_audios(input_directory, output_directory)  # Llama a la función
    print("Grabaciones amplificadas exitosamente.")

def copiar_archivos_a_destino(carpeta_origen, carpeta_origen2, carpeta_destino):
    # Crear la carpeta de destino si no existe
    os.makedirs(carpeta_destino, exist_ok=True)

    # Copiar archivos de ambas carpetas de origen a la carpeta de destino
    for carpeta in [carpeta_origen, carpeta_origen2]:
        for archivo in os.listdir(carpeta):
            ruta_archivo_origen = os.path.join(carpeta, archivo)
            ruta_archivo_destino = os.path.join(carpeta_destino, archivo)

            # Verificar que sea un archivo (no una carpeta)
            if os.path.isfile(ruta_archivo_origen):
                shutil.copy(ruta_archivo_origen, ruta_archivo_destino)
        print(f"Todos los archivos de {carpeta} han sido copiados en {carpeta_destino}.")

def aplicar_denoiser():
    print("Aplicando denoiser a las grabaciones...")
    copiar_archivos_a_destino(
        '/content/Grabaciones_de_cerca/',
        '/content/Grabaciones_amplificadas/',
        '/content/Grabaciones_pre_denoiser/'
    )

    # Directorios de entrada y salida
    input_directory = '/content/Grabaciones_pre_denoiser'
    output_directory = '/content/Audio_denoised_ResembleAI_rk4'

    # Llamada a la función procesar_denoise
    aplica_denoiser(input_directory, output_directory)
    print("Denoiser aplicado.")

def crear_transcripciones():
    print("Creando transcripciones y obteniendo parámetros de confiabilidad...")

    # Transcripciones sin denoiser aplicado
    input_directory_without_denoiser = '/content/Grabaciones_pre_denoiser'
    output_directory_without_denoiser = '/content/Transcripciones_sin_denoiser'
    nombre_archivo_csv_without_denoiser = '/content/Parametros_sin_denoiser.csv'

    # Llamada a la función transcribir_y_actualizar_csv
    transcribir_y_guardar(input_directory_without_denoiser, output_directory_without_denoiser, nombre_archivo_csv_without_denoiser)

    # Transcripciones con denoiser aplicado
    input_directory_denoised = '/content/Audio_denoised_ResembleAI_rk4'
    output_directory_denoised = '/content/Transcripciones_con_denoiser_ResembleAI_RK4'
    nombre_archivo_csv_denoised = '/content/Parametros_con_denoiser_ResembleAI_RK4.csv'

    # Llamada a la función transcribir_y_actualizar_csv
    transcribir_y_guardar(input_directory_denoised, output_directory_denoised, nombre_archivo_csv_denoised)
    print("Transcripciones completadas.")

def main():
    try:
        check_scripts()
        ejecutar_amplificador()
        aplicar_denoiser()
        crear_transcripciones()
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
