import os
import shutil
import subprocess
import pandas as pd
from pathlib import Path
from preprocesar_transcripciones import preprocess_single_file, preprocess_files
from determinador_WER import calcular_WER, process_wer_files, insertar_columna_wer  # Asegúrate de que estas funciones estén definidas
from identificador_hablante_grabaciones import identificador_hablante
from calculador_SNR import agregar_snr_a_csv  # Asegúrate de que esta función esté definida
from calculadora_speed_rate import actualizar_csv_con_velocidad  # Asegúrate de que esta función esté definida
from calculadora_frecuencia_fundamental import actualizar_csv_con_frecuencia  # Asegúrate de que esta función esté definida

# Verificar si cada script existe en el directorio actual

def check_scripts():
    scripts = {
        "wer.py": "/content/wer.py",
        "preprocesar_transcripciones": "/content/preprocesar_transcripciones.py",
        "determinador_WER": "/content/determinador_WER.py",
        "calculador_SNR": "/content/calculador_SNR.py",
        "calculadora_speed_rate": "/content/calculadora_speed_rate.py",
        "calculadora_frecuencia_fundamental": "/content/calculadora_frecuencia_fundamental.py",
    }
    for name, path in scripts.items():
        if not Path(path).is_file():
            raise FileNotFoundError(f"{path} no encontrado. Asegúrate de que todos los scripts estén en el directorio.")
        
def reescribir_transcripciones():
    print("Preprocesando las transcripciones...")

    # Preprocesar texto_referencia.txt
    input_directory_reference_text = '/content/Texto_Referencia.txt'
    output_directory_reference_text = '/content/Texto_Referencia_preprocesado.txt'

    preprocess_single_file(input_directory_reference_text, output_directory_reference_text)

    # Preprocesar transcripciones sin denoiser aplicado
    input_directory_without_denoiser = '/content/Transcripciones_sin_denoiser'
    output_directory_without_denoiser = '/content/Transcripciones_sin_denoiser_preprocesadas'

    preprocess_files(input_directory_without_denoiser, output_directory_without_denoiser)

    # Preprocesar transcripciones con denoiser aplicado
    input_directory_denoised = '/content/Transcripciones_con_denoiser_ResembleAI_RK4'
    output_directory_denoised = '/content/Transcripciones_con_denoiser_ResembleAI_RK4_preprocesadas'

    preprocess_files(input_directory_denoised, output_directory_denoised)
    print("Transcripciones preprocesadas exitosamente.")

# Obtener resultados
def medir_SNR():
    carpeta_entrada_sin_denoiser = '/content/Grabaciones_pre_denoiser'
    nombre_archivo_csv_sin_denoiser ='Parametros_sin_denoiser.csv'

    agregar_snr_a_csv(carpeta_entrada_sin_denoiser, '/content', nombre_archivo_csv_sin_denoiser)

    # Medir SNR con denoiser
    carpeta_entrada_con_denoiser = '/content/Audio_denoised_ResembleAI_rk4'
    nombre_archivo_csv_con_denoiser = 'Parametros_con_denoiser_ResembleAI_RK4.csv'

    agregar_snr_a_csv(carpeta_entrada_con_denoiser, '/content', nombre_archivo_csv_con_denoiser)
    print("Medición de SNR completada.")

def determinar_WER():
    print("Determinando WER de las transcripciones...")

    archivo_wer = '/content/wer.py'
    archivo_referencia = '/content/Texto_Referencia_preprocesado.txt'

    # WER sin denoiser
    carpeta_entrada_sin_denoiser = '/content/Transcripciones_sin_denoiser_preprocesadas'
    carpeta_salida_sin_denoiser = '/content/Resultados_WER_sin_denoiser'
    calcular_WER(archivo_wer, archivo_referencia, carpeta_entrada_sin_denoiser, carpeta_salida_sin_denoiser)

    # Procesar archivos WER
    wer_data = process_wer_files(carpeta_salida_sin_denoiser)

    # Cargar y actualizar CSV
    nombre_archivo_csv_sin_denoiser = '/content/Parametros_sin_denoiser.csv'
    df_resultados = pd.read_csv(nombre_archivo_csv_sin_denoiser, encoding='utf-8')
    df_resultados = insertar_columna_wer(df_resultados, wer_data)
    df_resultados.to_csv(nombre_archivo_csv_sin_denoiser, index=False, encoding='utf-8-sig')
    print(f"Archivo CSV '{nombre_archivo_csv_sin_denoiser}' actualizado con la columna WER (%).")

    # WER con denoiser
    carpeta_entrada_con_denoiser = '/content/Transcripciones_con_denoiser_ResembleAI_RK4_preprocesadas'
    carpeta_salida_con_denoiser = '/content/Resultados_WER_con_denoiser_ResembleAI_rk4'
    calcular_WER(archivo_wer, archivo_referencia, carpeta_entrada_con_denoiser, carpeta_salida_con_denoiser)

    # Procesar archivos WER
    wer_data = process_wer_files(carpeta_salida_con_denoiser)

    # Cargar y actualizar CSV
    nombre_archivo_csv_con_denoiser = '/content/Parametros_con_denoiser_ResembleAI_RK4.csv'
    df_resultados_denoiser = pd.read_csv(nombre_archivo_csv_con_denoiser, encoding='utf-8')
    df_resultados_denoiser = insertar_columna_wer(df_resultados_denoiser, wer_data)
    df_resultados_denoiser.to_csv(nombre_archivo_csv_con_denoiser, index=False, encoding='utf-8-sig')
    print(f"Archivo CSV '{nombre_archivo_csv_con_denoiser}' actualizado con la columna WER (%).")

def medir_velocidad():
    print("Midiendo velocidad de las grabaciones...")

    # Calcular velocidad sin denoiser
    transcripciones_dir_sin_denoiser = '/content/Transcripciones_sin_denoiser_preprocesadas'
    nombre_archivo_csv_sin_denoiser = '/content/Parametros_sin_denoiser.csv'
    actualizar_csv_con_velocidad('/content/Grabaciones_de_cerca', transcripciones_dir_sin_denoiser, nombre_archivo_csv_sin_denoiser)

    print("Medición de velocidad completada.")

def calcular_frecuencia_fundamental():
    print("Calculando frecuencia fundamental de las grabaciones...")

    # Frecuencia fundamental sin denoiser
    carpeta_entrada_sin_denoiser = '/content/Grabaciones_de_cerca'
    nombre_archivo_csv_sin_denoiser = '/content/Parametros_sin_denoiser.csv'
    actualizar_csv_con_frecuencia(carpeta_entrada_sin_denoiser, nombre_archivo_csv_sin_denoiser)

    print("Cálculo de frecuencia fundamental completado.")

def identificar_hablante():
    referencias = {
        "Isabel": "/content/Grabaciones_de_cerca/Grabacion1_Punto2_TomadaEnPunto2_Isabel.mp3",
        "Coto": "/content/Grabaciones_de_cerca/Grabacion1_Punto5_TomadaEnPunto5_Coto.mp3"
    }
    carpeta_audios = "/content/Grabaciones_pre_denoiser"  # Cambia esto a tu carpeta de audios
    identificador_hablante(referencias, carpeta_audios)

    referencias = {
        "Isabel": "/content/Grabaciones_de_cerca/Grabacion1_Punto2_TomadaEnPunto2_Isabel.mp3",
        "Coto": "/content/Grabaciones_de_cerca/Grabacion1_Punto5_TomadaEnPunto5_Coto.mp3"
    }
    carpeta_audios = "/content/Audio_denoised_ResembleAI_rk4"  # Cambia esto a tu carpeta de audios
    identificador_hablante(referencias, carpeta_audios)


def main():
    try:
        check_scripts()
        reescribir_transcripciones()
        # medir_SNR()
        determinar_WER()
        identificar_hablante()
        medir_velocidad()
        calcular_frecuencia_fundamental()
    except Exception as e:  
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
