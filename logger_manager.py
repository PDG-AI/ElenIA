import logging
import os
from datetime import datetime

class LoggerManager:
    def __init__(self, log_path):
        self.log_path = log_path
        self._setup_logging()

    def _setup_logging(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        # Configurar formato de logs
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Configurar logger principal
        self.logger = logging.getLogger('Elenia')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para archivo
        log_file = os.path.join(self.log_path, f'elenia_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format, date_format))
        
        # Añadir handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_emotion_analysis(self, text, result):
        """Registra el análisis de emociones"""
        self.logger.debug(f"Análisis de emociones - Texto: {text}")
        self.logger.debug(f"Resultado: {result}")

    def log_summarization(self, conversations, summary):
        """Registra el resumen de conversaciones"""
        self.logger.debug(f"Resumen de {len(conversations)} conversaciones")
        self.logger.debug(f"Resumen generado: {summary}")

    def log_categorization(self, text, response, result):
        """Registra la categorización de memoria"""
        self.logger.debug(f"Categorización - Texto: {text}")
        self.logger.debug(f"Respuesta: {response}")
        self.logger.debug(f"Resultado: {result}")

    def log_context_analysis(self, text, memories, result):
        """Registra el análisis de contexto"""
        self.logger.debug(f"Análisis de contexto - Texto: {text}")
        self.logger.debug(f"Memorias analizadas: {len(memories)}")
        self.logger.debug(f"Resultado: {result}")

    def log_error(self, service, error):
        """Registra errores"""
        self.logger.error(f"Error en {service}: {str(error)}")

    def log_api_usage(self, service, tokens_used):
        """Registra el uso de la API"""
        self.logger.info(f"Uso de API {service}: {tokens_used} tokens")

    def log_memory_operation(self, operation, details):
        """Registra operaciones de memoria"""
        self.logger.debug(f"Operación de memoria - {operation}: {details}")

    def log_personality_change(self, emotion, value):
        """Registra cambios en la personalidad"""
        self.logger.debug(f"Cambio de personalidad - Emoción: {emotion}, Valor: {value}")

    def log_conversation(self, user_input, bot_response):
        """Registra una conversación"""
        self.logger.info(f"Usuario: {user_input}")
        self.logger.info(f"Bot: {bot_response}") 