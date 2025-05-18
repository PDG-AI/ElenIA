import speech_recognition as sr
import numpy as np
import sounddevice as sd
import constants
from scipy import signal

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = constants.NOISE_THRESHOLD
        self.recognizer.pause_threshold = constants.STT_TIMEOUT
        
        # Configuración del dispositivo de entrada
        self.input_device = constants.INPUT_INDEX
        
    def adjust_for_ambient_noise(self, duration=1):
        """Ajusta el umbral de ruido según el ambiente"""
        with sr.Microphone(device_index=self.input_device) as source:
            print("Ajustando al ruido ambiente...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print(f"Umbral de ruido ajustado a: {self.recognizer.energy_threshold}")

    def listen(self):
        """Escucha el audio y lo convierte a texto"""
        try:
            with sr.Microphone(device_index=self.input_device) as source:
                print("Escuchando...")
                audio = self.recognizer.listen(source)
                return audio
        except Exception as e:
            print(f"Error al escuchar: {str(e)}")
            return None

    def transcribe(self, audio):
        """Transcribe el audio a texto"""
        try:
            text = self.recognizer.recognize_google(audio, language=constants.STT_LANGUAGE)
            print(f"Texto reconocido: {text}")
            return text
        except sr.UnknownValueError:
            print("No se pudo entender el audio")
            return None
        except sr.RequestError as e:
            print(f"Error en la solicitud a Google Speech Recognition: {str(e)}")
            return None

    def get_audio_level(self):
        """Obtiene el nivel de audio actual para ajuste de ruido"""
        try:
            with sr.Microphone(device_index=self.input_device) as source:
                audio = self.recognizer.listen(source, timeout=0.5)
                data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                return np.abs(data).mean()
        except:
            return 0 