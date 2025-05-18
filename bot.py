import os
import time
import re
import signal
import sys
from dotenv import load_dotenv
from modulos.stt import SpeechToText
from modulos.tts import TextToSpeech
from modulos.ai_manager import AIManager
from modulos.timer_manager import TimerManager
from modulos.searchs_manager import SearchManager
from modulos.notes_manager import NotesManager
from modulos.filtrador import Filtrador
from modulos.memory_manager import MemoryManager
from modulos.personality_manager import PersonalityManager
from modulos.logger_manager import LoggerManager
from modulos.metrics_manager import MetricsManager
import constants

class Bot:
    def __init__(self):
        # Cargar variables de entorno
        load_dotenv()
        
        # Inicializar logger y métricas
        self.logger = LoggerManager(constants.LOG_PATH)
        self.metrics = MetricsManager(constants.METRICS_PATH)
        
        # Inicializar componentes
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.ai_manager = AIManager()
        self.timer_manager = TimerManager()
        self.search_manager = SearchManager()
        self.notes_manager = NotesManager()
        self.filtrador = Filtrador()
        self.memory_manager = MemoryManager(constants.MEMORY_PATH)
        self.personality_manager = PersonalityManager(constants.MEMORY_PATH)
        
        # Flag para controlar el bucle principal
        self.running = False
        
        # Tiempo de inicio
        self.start_time = time.time()
        
        self.logger.logger.info("Bot inicializado")

    def cleanup(self):
        """Limpia recursos antes de terminar"""
        try:
            self.logger.logger.info("Limpiando recursos...")
            
            # Guardar métricas finales
            self.metrics.record_memory_operation("shutdown")
            
            # Cerrar temporizadores activos
            self.timer_manager.cleanup()
            
            # Guardar notas pendientes
            self.notes_manager.save_notes()
            
            # Guardar estado de la memoria
            self.memory_manager.save_memory()
            
            self.logger.logger.info("Recursos limpiados correctamente")
        except Exception as e:
            self.logger.log_error("cleanup", str(e))

    def signal_handler(self, signum, frame):
        """Maneja señales de sistema"""
        self.logger.logger.info(f"Recibida señal {signum}")
        self.running = False

    def _is_directed_to_bot(self, text):
        """Determina si el mensaje está dirigido al bot basado en contexto y patrones"""
        texto_minus = text.lower()
        
        # Patrones de dirección directa
        direct_patterns = [
            r"^(elenia|elena|elen|nena|helen|hellen|ellen)[\s,:.-]+",
            r"^(oye|hey|eh|hola|buenas)[\s,:.-]+(elenia|elena|elen|nena|helen|hellen|ellen)[\s,:.-]+",
            r"^(disculpa|perdón|perdon|por favor)[\s,:.-]+(elenia|elena|elen|nena|helen|hellen|ellen)[\s,:.-]+"
        ]
        
        # Verificar patrones directos
        for pattern in direct_patterns:
            if re.search(pattern, texto_minus):
                return True
        
        # Verificar contexto de conversación
        context_indicators = [
            "puedes", "podrías", "ayúdame", "ayuda", "necesito", "quiero",
            "dime", "cuéntame", "explícame", "sabes", "conoces"
        ]
        
        # Si hay indicadores de contexto y no hay otro nombre mencionado
        has_context = any(indicator in texto_minus for indicator in context_indicators)
        other_names = ["alexa", "siri", "google", "cortana", "ok google", "hey siri"]
        no_other_names = not any(name in texto_minus for name in other_names)
        
        return has_context and no_other_names

    def process_audio(self, audio_data):
        """Procesa audio y genera una respuesta"""
        try:
            # Convertir audio a texto
            text = self.stt.transcribe(audio_data)
            if not text:
                return
            
            self.logger.logger.info(f"Audio transcrito: {text}")

            # Verificar si el mensaje está dirigido al bot
            if not self._is_directed_to_bot(text):
                return

            # Limpiar el texto de nombres y patrones de dirección
            cleaned_text = text
            for pattern in [
                r"^(elenia|elena|elen|nena|helen|hellen|ellen)[\s,:.-]+",
                r"^(oye|hey|eh|hola|buenas)[\s,:.-]+(elenia|elena|elen|nena|helen|hellen|ellen)[\s,:.-]+",
                r"^(disculpa|perdón|perdon|por favor)[\s,:.-]+(elenia|elena|elen|nena|helen|hellen|ellen)[\s,:.-]+"
            ]:
                cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)
            
            cleaned_text = cleaned_text.strip()

            # Filtrar contenido sensible
            filtered_text = self.filtrador.filter(cleaned_text)
            
            # Obtener contexto de conversaciones recientes
            recent_conversations = self.memory_manager.get_recent_conversations()
            
            # Si hay muchas conversaciones, resumirlas
            if len(recent_conversations) > 5:
                summary = self.ai_manager.secondary_ai.summarize_conversation(recent_conversations)
                context = f"Resumen de conversaciones anteriores:\n{summary}\n\nConversaciones recientes:\n"
                context += "\n".join([f"Usuario: {conv['user_input']}\nBot: {conv['bot_response']}" 
                                    for conv in recent_conversations[-3:]])
            else:
                context = "\n".join([f"Usuario: {conv['user_input']}\nBot: {conv['bot_response']}" 
                                   for conv in recent_conversations])
            
            # Obtener respuesta de la IA con contexto
            response = self.ai_manager.get_response(filtered_text, context)
            
            # Solo procesar y hablar si hay una respuesta
            if response and response.strip():
                # Guardar la conversación en la memoria
                self.memory_manager.add_conversation(filtered_text, response)
                
                # Procesar comandos implícitos en la respuesta
                self._process_implicit_commands(response)
                
                # Convertir respuesta a audio
                self.tts.speak(response)
                
                # Registrar la conversación
                self.logger.log_conversation(filtered_text, response)
                
        except Exception as e:
            self.logger.log_error("audio_processing", str(e))

    def _process_implicit_commands(self, response):
        """Procesa comandos implícitos en la respuesta"""
        try:
            # La IA puede haber incluido comandos implícitos en su respuesta
            # que necesitan ser procesados
            if "temporizador" in response.lower():
                self.timer_manager.process_timer_request(response)
                self.logger.logger.info("Procesando comando de temporizador")
            
            if "buscar" in response.lower():
                self.search_manager.process_search_request(response)
                self.logger.logger.info("Procesando comando de búsqueda")
                
            if "nota" in response.lower():
                self.notes_manager.process_note_request(response)
                self.logger.logger.info("Procesando comando de notas")
        except Exception as e:
            self.logger.log_error("command_processing", str(e))

    def start_listening(self):
        """Inicia el bucle de escucha de audio"""
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.running = True
        self.logger.logger.info("Iniciando escucha de audio...")
        
        try:
            while self.running:
                try:
                    # Obtener audio de Voicemeeter
                    audio_data = self.stt.listen()
                    if audio_data:
                        self.process_audio(audio_data)
                except Exception as e:
                    self.logger.log_error("main_loop", str(e))
                    time.sleep(1)
        finally:
            self.cleanup()

    def get_system_status(self):
        """Obtiene el estado actual del sistema"""
        try:
            status = {
                'memory': {
                    'total_items': len(self.memory_manager.get_recent_conversations()),
                    'last_updated': self.memory_manager.get_last_update()
                },
                'metrics': {
                    'api_usage': self.metrics.get_service_stats('main'),
                    'emotion_stats': self.metrics.get_emotion_stats(),
                    'memory_ops': self.metrics.get_memory_stats()
                },
                'personality': {
                    'current_emotion': self.personality_manager.get_current_emotion(),
                    'emotion_intensity': self.personality_manager.get_emotion_intensity()
                },
                'active_timers': self.timer_manager.get_active_timers(),
                'pending_notes': self.notes_manager.get_pending_notes(),
                'system_uptime': time.time() - self.start_time
            }
            
            self.logger.logger.info("Estado del sistema obtenido correctamente")
            return status
        except Exception as e:
            self.logger.log_error("system_status", str(e))
            return None

def main():
    # Crear directorios necesarios
    os.makedirs(constants.MEMORY_PATH, exist_ok=True)
    os.makedirs(constants.LOG_PATH, exist_ok=True)
    os.makedirs(constants.METRICS_PATH, exist_ok=True)
    
    # Inicializar y ejecutar el bot
    bot = Bot()
    bot.start_listening()

if __name__ == "__main__":
    main() 