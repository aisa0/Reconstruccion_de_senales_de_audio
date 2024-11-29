import torchaudio
from speechbrain.pretrained import EncoderClassifier
import numpy as np
import os
import re

# Cargar el modelo de identificación de hablante
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec")

# Obtener embedding del audio
def obtener_embedding(audio_path):
    try:
        audio, sr = torchaudio.load(audio_path)
        embedding = classifier.encode_batch(audio)
        return embedding.squeeze().numpy()  # Convertir a numpy array para facilitar la comparación
    except Exception as e:
        print(f"Error al cargar el audio {audio_path}: {e}")
        return None  # Devolver None si hay un error

# Función para extraer el nombre del hablante del nombre del archivo
def extraer_hablante(nombre_archivo):
    # Suponiendo que el formato puede variar, buscamos el nombre del hablante
    patron = r"(?:denoised_)?(?:.*?[_-])?(Coto|Isabel|Marvin|Ana)(?:[_-]|\.|$)"  # Modifica según los nombres de los hablantes
    match = re.search(patron, nombre_archivo)
    return match.group(1) if match else None  # Devolver el nombre del hablante

# Comparar con los embeddings de nuevos audios
def identificar_hablante_en_archivo(embedding_nuevo, embeddings_referencia):
    distancias = {}
    for hablante, embedding_ref in embeddings_referencia.items():
        distancia = np.linalg.norm(embedding_nuevo - embedding_ref)  # Distancia Euclidiana
        distancias[hablante] = distancia
    return min(distancias, key=distancias.get)  # Devuelve el hablante con la menor distancia

# Función principal
def identificador_hablante(referencias, carpeta_audios):
    # Crear embeddings de referencia para cada hablante
    embeddings_referencia = {hablante: obtener_embedding(ruta) for hablante, ruta in referencias.items()}
    
    # Verificar que no haya errores en los embeddings de referencia
    if any(embedding is None for embedding in embeddings_referencia.values()):
        print("Error al cargar los embeddings de referencia. Verifica los archivos de referencia.")
        return
    
    # Inicializar conteo de aciertos
    total_archivos = 0
    aciertos = 0

    # Identificar hablantes en todas las grabaciones de la carpeta
    for archivo in os.listdir(carpeta_audios):
        if archivo.endswith(".mp3"):  # Asegúrate de procesar solo archivos mp3
            ruta_audio = os.path.join(carpeta_audios, archivo)
            embedding_nuevo = obtener_embedding(ruta_audio)

            if embedding_nuevo is not None:  # Verifica que el embedding no sea None
                # Extraer el nombre del hablante del nombre del archivo
                hablante_real = extraer_hablante(archivo)

                # Identificar el hablante
                hablante_identificado = identificar_hablante_en_archivo(embedding_nuevo, embeddings_referencia)

                # Contar aciertos
                total_archivos += 1
                if hablante_real is not None:  # Solo contamos si el hablante real se extrajo correctamente
                    aciertos += 1 if hablante_identificado == hablante_real else 0
                print(f"El hablante identificado en {archivo} es: {hablante_identificado}. Hablante real: {hablante_real}")
            else:
                print(f"No se pudo obtener el embedding para {archivo}.")

    # Calcular y mostrar el porcentaje de aciertos
    if total_archivos > 0:
        porcentaje_aciertos = (aciertos / total_archivos) * 100
        print(f"Porcentaje de aciertos: {porcentaje_aciertos:.2f}%")
    else:
        print("No se procesaron archivos.")

