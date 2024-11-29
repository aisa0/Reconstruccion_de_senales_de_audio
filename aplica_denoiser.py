import os
import torch
import torchaudio
from pydub import AudioSegment
from pathlib import Path
from resemble_enhance.enhancer.inference import denoise, enhance

# Verificar si hay una GPU disponible
device = "cuda" if torch.cuda.is_available() else "cpu"

# Parámetros del modelo CFM y RK4
solver = "rk4"  # Método de integración en minúsculas
nfe = 64  # Número de evaluaciones de la función
tau = 0.5  # Temperatura del prior
denoising = True  # Hacer denoising antes de la mejora

def process_audio_file(input_path, output_dir):
    """
    Procesa un archivo de audio con denoising y mejora, y guarda los resultados en formato .mp3.
    """
    try:
        # Cargar el archivo de audio .mp3
        dwav, sr = torchaudio.load(input_path, format="mp3")
        dwav = dwav.mean(dim=0)  # Convertir a mono si es estéreo

        # Aplicar el denoising
        wav1, new_sr = denoise(dwav, sr, device)

        # Aplicar la mejora
        # wav2, new_sr = enhance(dwav, sr, device, nfe=nfe, solver=solver, lambd=0.9 if denoising else 0.1, tau=tau)

        # Crear el directorio de salida si no existe
        output_path_denoised = output_dir / f"denoised_{input_path.stem}.wav"
        # output_path_enhanced = output_dir / f"enhanced_{input_path.stem}.wav"

        # Guardar los archivos procesados como WAV primero
        torchaudio.save(output_path_denoised, wav1.unsqueeze(0), new_sr)
        # torchaudio.save(output_path_enhanced, wav2.unsqueeze(0), new_sr)

        # Convertir los archivos WAV a MP3 usando pydub
        AudioSegment.from_wav(output_path_denoised).export(output_path_denoised.with_suffix('.mp3'), format="mp3")
        # AudioSegment.from_wav(output_path_enhanced).export(output_path_enhanced.with_suffix('.mp3'), format="mp3")

        # Eliminar los archivos WAV temporales
        os.remove(output_path_denoised)
        # os.remove(output_path_enhanced)

        # print(f"Archivo procesado y guardado: {output_path_denoised.with_suffix('.mp3')}, {output_path_enhanced.with_suffix('.mp3')}")
        print(f"Archivo procesado y guardado: {output_path_denoised.with_suffix('.mp3')}")
    except Exception as e:
        print(f"Error procesando {input_path}: {str(e)}")

def aplica_denoiser(input_folder, output_folder):
    """
    Procesa todos los archivos de audio en una carpeta y guarda los resultados en formato .mp3.
    """
    # Asegurarse de que el directorio de salida existe
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Procesar todos los archivos de audio en el directorio de entrada
    for audio_file in Path(input_folder).glob("*.mp3"):  # Se procesan archivos .mp3
        print(f"Procesando {audio_file}...")
        process_audio_file(audio_file, output_folder)