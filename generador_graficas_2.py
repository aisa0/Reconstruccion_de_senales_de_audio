import os
import numpy as np
import matplotlib.pyplot as plt

# Función para leer y procesar el archivo
def procesar_archivo(archivo):
    metricas = {
        'Omnidireccional': {},
        'Cardioide': {}
    }
    current_position = None
    current_hablante = None

    with open(archivo, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith("Posición de Grabación ="):
                if "Micrófono omnidireccional" in line:
                    current_position = 'Omnidireccional'
                elif "Micrófono cardioide" in line:
                    current_position = 'Cardioide'

            elif line.startswith("Hablante:"):
                current_hablante = line.split(":")[1].strip()

            elif line.startswith("Speed Rate (wpm):"):
                speed = line.split(":")[1].strip()
                speed = float(speed) if speed != 'nan' else np.nan

            elif line.startswith("Frecuencia Fundamental Promedio (Hz):"):
                freq = line.split(":")[1].strip()
                freq = float(freq) if freq != 'nan' else np.nan

                if current_position and current_hablante:
                    if current_hablante not in metricas[current_position]:
                        metricas[current_position][current_hablante] = {}
                    metricas[current_position][current_hablante]['Speed Rate'] = speed
                    metricas[current_position][current_hablante]['Frecuencia Fundamental'] = freq

    return metricas

# Procesar el archivo
metricas_sin_denoiser = procesar_archivo('/content/promedios_sin_denoiser.txt')

# Verificar la estructura del diccionario
print("Estructura de los datos procesados:")
print(metricas_sin_denoiser)

# Función para graficar los datos
def graficar_todo_en_una(metricas_sin_denoiser):
    # Obtener los hablantes de las posiciones con datos
    hablantes = []
    for posicion in metricas_sin_denoiser.values():
        hablantes.extend(posicion.keys())

    hablantes = list(set(hablantes))  # Eliminar duplicados

    ancho_barras = 0.5
    x = np.arange(len(hablantes))

    # Calcular datos para Speed Rate y Frecuencia Fundamental
    speed_sin_denoiser = [
        np.nanmean([metricas_sin_denoiser[posicion][h].get('Speed Rate', 0) or 0 for posicion in metricas_sin_denoiser.keys() if h in metricas_sin_denoiser[posicion]])
        for h in hablantes
    ]
    freq_sin_denoiser = [
        np.nanmean([metricas_sin_denoiser[posicion][h].get('Frecuencia Fundamental', 0) or 0 for posicion in metricas_sin_denoiser.keys() if h in metricas_sin_denoiser[posicion]])
        for h in hablantes
    ]

    # Crear figura y ejes (ahora horizontales)
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Gráfica 1: Velocidad
    axes[0].barh(x, speed_sin_denoiser, ancho_barras, color='skyblue')
    axes[0].set_title("Velocidad")
    axes[0].set_xlabel("(wpm)")
    axes[0].set_yticks(x)
    axes[0].set_yticklabels(hablantes)

    # Gráfica 2: Frecuencia
    axes[1].barh(x, freq_sin_denoiser, ancho_barras, color='orange')
    axes[1].set_title("Frecuencia Fundamental")
    axes[1].set_xlabel("(Hz)")
    axes[1].set_yticks(x)
    axes[1].set_yticklabels(hablantes)

    # Ajustar diseño
    plt.tight_layout()

    # Directorios para los gráficos
    directorio_pdf = "/content/Resultados_Graficas/Frecuencia_y_Velocidad/PDFs"
    directorio_png = "/content/Resultados_Graficas/Frecuencia_y_Velocidad/PNGs"
    os.makedirs(directorio_pdf, exist_ok=True)
    os.makedirs(directorio_png, exist_ok=True)

    # Guardar la gráfica en PDF y PNG
    nombre_archivo = f"f0_y_sr"
    plt.savefig(f"{directorio_pdf}/{nombre_archivo}.pdf", format="pdf")
    plt.savefig(f"{directorio_png}/{nombre_archivo}.png", format="png")

    plt.show()

    

# Llamada a la función para generar las gráficas
graficar_todo_en_una(metricas_sin_denoiser)
