import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# from calculo_promedios import calcular_promedios

# Configuración de estilo para los gráficos
sns.set(style="whitegrid", context="talk", palette="bright")

# Listado de métricas a graficar
metricas = {
    'WER (%)': 'WER',
    'Confiabilidad (Deepgram)': 'Confiabilidad'
}

# Lista de archivos con sus etiquetas correspondientes
archivos = {
    '/content/Parametros_sin_denoiser.csv': 'Sin Denoiser',
    '/content/Parametros_con_denoiser_ResembleAI_RK4.csv': 'Denoiser Resemble AI - RK4'
}

# Cargar y combinar los datos
def cargar_datos_combinados():
    dataframes = []
    for archivo, etiqueta in archivos.items():
        df = pd.read_csv(archivo)
        df['Modo Denoiser'] = etiqueta  # Añadir columna de identificación
        dataframes.append(df)
    datos_combinados = pd.concat(dataframes, ignore_index=True)
    return datos_combinados

# Función para generar gráficos comparativos en una sola imagen para cada hablante
def graficar_comparacion_por_hablante(datos_combinados, metric, nombre_metric, directorio_pdf, directorio_png):
    for hablante in datos_combinados['Hablante'].unique():
        datos_hablante = datos_combinados[datos_combinados['Hablante'] == hablante]

        plt.figure(figsize=(12, 8))
        sns.lineplot(
            data=datos_hablante, x='Distancia (m)', y=metric, hue='Modo Denoiser', 
            style='Tipo Micrófono', markers=True, dashes=False, errorbar=None
        )

        # Títulos y etiquetas
        plt.title(f"Comparación de {nombre_metric} para el hablante {hablante}")
        plt.xlabel("Distancia (m)")
        plt.ylabel(metric)
        plt.legend(title="Modo Denoiser / Tipo Micrófono")
        plt.grid(True)

        # Guardar la gráfica en PDF y PNG
        nombre_archivo = f"comparacion_{hablante}_{metric.replace(' ', '_')}"
        plt.savefig(f"{directorio_pdf}/{nombre_archivo}.pdf", format="pdf")
        plt.savefig(f"{directorio_png}/{nombre_archivo}.png", format="png")

        plt.show()

# Función principal para generar gráficos y calcular promedios
def generar_graficas():
    print("Generando gráficas...")

    # Cargar todos los datos
    datos_combinados = cargar_datos_combinados()
    datos_combinados['Tipo Micrófono'] = datos_combinados['Posición de Grabación'].apply(lambda x: 'Omnidireccional' if x == 7 else 'Cardiode')

    # Directorios para los gráficos
    directorio_pdf = "/content/Resultados_Graficas/Comparacion_Denoisers/PDFs"
    directorio_png = "/content/Resultados_Graficas/Comparacion_Denoisers/PNGs"
    os.makedirs(directorio_pdf, exist_ok=True)
    os.makedirs(directorio_png, exist_ok=True)

    # Generar gráficos comparativos para cada métrica y hablante
    for metric, nombre_metric in metricas.items():
        graficar_comparacion_por_hablante(datos_combinados, metric, nombre_metric, directorio_pdf, directorio_png)

    print("Gráficas generadas.")

# Función para calcular y guardar los promedios en un archivo de texto
def calcular_promedios(archivo_csv, archivo_salida):
    try:
        # Cargar los datos del archivo CSV
        datos = pd.read_csv(archivo_csv)
        
        # Lista de columnas numéricas requeridas
        columnas_requeridas = ['Speed Rate (wpm)', 'WER (%)', 'Confiabilidad (Deepgram)',
                               'Frecuencia Fundamental Promedio (Hz)', 'Varianza f0 (Hz^2)']
        
        # Determinar qué columnas están disponibles
        columnas_disponibles = [col for col in columnas_requeridas if col in datos.columns]
        columnas_faltantes = set(columnas_requeridas) - set(columnas_disponibles)
        
        if not columnas_disponibles:
            print(f"El archivo {archivo_csv} no contiene ninguna de las columnas requeridas. Se omite.")
            return
        
        if columnas_faltantes:
            print(f"Advertencia: El archivo {archivo_csv} no tiene las columnas {', '.join(columnas_faltantes)}.")

        # Filtrar datos según micrófono y posición
        with open(archivo_salida, 'w') as f:
            for posicion, microfono in [(7, "omnidireccional"), (None, "cardioide")]:
                if posicion is not None:
                    datos_filtrados = datos[datos['Posición de Grabación'] == posicion]
                    descripcion_posicion = "Posición de Grabación = 7"
                else:
                    datos_filtrados = datos[datos['Posición de Grabación'] != 7]
                    descripcion_posicion = "Posición de Grabación != 7"
                
                f.write(f"{descripcion_posicion} (Micrófono {microfono}):\n")
                
                for hablante in datos_filtrados['Hablante'].unique():
                    datos_hablante = datos_filtrados[datos_filtrados['Hablante'] == hablante]
                    promedios = datos_hablante[columnas_disponibles].mean()
                    
                    f.write(f"  Hablante: {hablante}\n")
                    for columna, promedio in promedios.items():
                        f.write(f"    {columna}: {promedio:.2f}\n")
                    f.write("\n")
                    
    except Exception as e:
        print(f"Error procesando {archivo_csv}: {e}")

# Función para calcular los promedios
def calcula_promedios():
    print("Calculando promedios...")

    # Procesar cada archivo y guardar en archivos de texto de promedios
    for archivo, etiqueta in archivos.items():
        salida_promedios = f"/content/promedios_{etiqueta.replace(' ', '_').lower()}.txt"
        calcular_promedios(archivo, salida_promedios)

    print("Promedios generados.")

# Función principal
def main():
    try:
        generar_graficas()
        calcula_promedios()
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()