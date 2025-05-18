import pyttsx3
import constants
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import tempfile
import os
from scipy import signal

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self._configure_engine()
        self.output_device = constants.OUTPUT_INDEX
        # Parámetros de procesamiento de audio estilo Neuro-sama
        self.pitch_shift = 1.05  # Pitch ligeramente más agudo
        self.smooth_factor = 0.6  # Suavizado moderado
        self.robot_factor = 0.0  # Sin efecto robótico
        self.formant_shift = 1.0  # Sin modificación de formantes
        self.reverb_factor = 0.05  # Reverb muy sutil

    def _configure_engine(self):
        """Configura el motor TTS con los parámetros especificados"""
        # Configurar voz
        voices = self.engine.getProperty('voices')
        # Intentar encontrar una voz suave y femenina
        soft_voice = None
        for voice in voices:
            if voice.gender == constants.TTS_VOICE:
                # Priorizar voces que contengan palabras clave de suavidad
                if any(keyword in voice.name.lower() for keyword in ['soft', 'gentle', 'suave', 'dulce', 'female', 'mujer']):
                    soft_voice = voice.id
                    break
                elif not soft_voice:  # Si no encontramos una voz suave, guardamos la primera que coincida con el género
                    soft_voice = voice.id
        
        if soft_voice:
            self.engine.setProperty('voice', soft_voice)

        # Configurar velocidad más lenta para sonar más suave
        self.engine.setProperty('rate', int(175 * constants.TTS_SPEED))
        
        # Configurar volumen más bajo para sonar más suave
        self.engine.setProperty('volume', 0.95)

    def _apply_robot_effect(self, audio_data, sample_rate):
        """Aplica un efecto robótico sutil al audio"""
        # Aplicar modulación de amplitud
        t = np.arange(len(audio_data)) / sample_rate
        carrier = np.sin(2 * np.pi * 5 * t)  # 5 Hz de modulación
        modulated = audio_data * (1 + self.robot_factor * carrier)
        return modulated

    def _apply_reverb(self, audio_data, sample_rate):
        """Aplica un reverb sutil"""
        # Crear un impulso de reverb simple
        reverb_length = int(0.1 * sample_rate)  # 100ms de reverb
        impulse = np.exp(-np.arange(reverb_length) / (0.05 * sample_rate))
        impulse = impulse / np.sum(impulse)
        
        # Aplicar convolución
        reverb = np.convolve(audio_data, impulse, mode='same')
        
        # Mezclar con el audio original
        return (1 - self.reverb_factor) * audio_data + self.reverb_factor * reverb

    def _process_audio(self, audio_data, sample_rate):
        """Procesa el audio para hacerlo más suave y similar a Neuro-sama"""
        # Convertir a float32 para procesamiento
        audio_float = audio_data.astype(np.float32)
        
        # Normalizar el audio
        audio_float = audio_float / np.max(np.abs(audio_float))
        
        # Aplicar suavizado usando filtro de media móvil
        window_size = int(sample_rate * 0.01)  # 10ms de ventana
        audio_smooth = np.convolve(audio_float, np.ones(window_size)/window_size, mode='same')
        
        # Mezclar el audio original con el suavizado
        audio_processed = (1 - self.smooth_factor) * audio_float + self.smooth_factor * audio_smooth
        
        # Aplicar efecto robótico sutil
        audio_processed = self._apply_robot_effect(audio_processed, sample_rate)
        
        # Aplicar reverb sutil
        audio_processed = self._apply_reverb(audio_processed, sample_rate)
        
        # Aplicar cambio de pitch usando resampling
        if self.pitch_shift != 1.0:
            # Calcular nueva longitud basada en el pitch shift
            new_length = int(len(audio_processed) / self.pitch_shift)
            # Resamplear el audio
            audio_processed = signal.resample(audio_processed, new_length)
        
        # Aplicar shift de formantes para sonar más femenino
        if self.formant_shift != 1.0:
            # Usar STFT para modificar formantes
            f, t, Zxx = signal.stft(audio_processed, sample_rate, nperseg=1024)
            # Shift de frecuencias
            f_shifted = f * self.formant_shift
            # Reconstruir señal
            _, audio_processed = signal.istft(Zxx, sample_rate, nperseg=1024)
        
        # Normalizar de nuevo
        audio_processed = audio_processed / np.max(np.abs(audio_processed))
        
        # Convertir de vuelta a int16
        return (audio_processed * 32767).astype(np.int16)

    def speak(self, text):
        """Convierte texto a voz y lo reproduce"""
        try:
            # Crear archivo temporal para el audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name

            # Generar audio
            self.engine.save_to_file(text, temp_filename)
            self.engine.runAndWait()

            # Procesar y reproducir audio
            self._play_audio(temp_filename)

            # Limpiar archivo temporal
            os.unlink(temp_filename)

        except Exception as e:
            print(f"Error en TTS: {str(e)}")

    def _play_audio(self, filename):
        """Reproduce el archivo de audio a través del dispositivo especificado"""
        try:
            # Cargar archivo de audio
            sample_rate, audio_data = wavfile.read(filename)
            
            # Procesar el audio
            processed_audio = self._process_audio(audio_data, sample_rate)
            
            # Reproducir audio procesado
            sd.play(processed_audio, sample_rate, device=self.output_device)
            sd.wait()  # Esperar a que termine la reproducción

        except Exception as e:
            print(f"Error al reproducir audio: {str(e)}")

    def set_voice(self, voice_id):
        """Cambia la voz del TTS"""
        self.engine.setProperty('voice', voice_id)
        self._configure_engine()

    def set_speed(self, speed):
        """Ajusta la velocidad de la voz"""
        self.engine.setProperty('rate', int(175 * speed))
        self._configure_engine()

    def set_pitch(self, pitch_factor):
        """Ajusta el pitch de la voz (0.5-2.0)"""
        self.pitch_shift = max(0.5, min(2.0, pitch_factor))

    def set_smoothness(self, smooth_factor):
        """Ajusta el factor de suavizado (0-1)"""
        self.smooth_factor = max(0.0, min(1.0, smooth_factor))

    def set_robot_factor(self, robot_factor):
        """Ajusta el factor de voz robótica (0-1)"""
        self.robot_factor = max(0.0, min(1.0, robot_factor))

    def set_formant_shift(self, formant_shift):
        """Ajusta el shift de formantes (0.8-1.5)"""
        self.formant_shift = max(0.8, min(1.5, formant_shift))

    def set_reverb(self, reverb_factor):
        """Ajusta el factor de reverb (0-1)"""
        self.reverb_factor = max(0.0, min(1.0, reverb_factor)) 