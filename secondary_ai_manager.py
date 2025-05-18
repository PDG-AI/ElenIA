import openai
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import time
from .logger_manager import LoggerManager
from .metrics_manager import MetricsManager

class SecondaryAIManager:
    def __init__(self, log_path, metrics_path):
        load_dotenv()
        self.api_keys = {
            "emotion": os.getenv("OPENAI_API_KEY_S1"),
            "summarizer": os.getenv("OPENAI_API_KEY_S2"),
            "categorizer": os.getenv("OPENAI_API_KEY_S3")
        }
        
        # Inicializar logger y métricas
        self.logger = LoggerManager(log_path)
        self.metrics = MetricsManager(metrics_path)
        
        # Verificar que todas las API keys estén disponibles
        for service, key in self.api_keys.items():
            if not key:
                self.logger.log_error(service, "No se encontró la API key")
        
        self.models = {
            "emotion": "gpt-3.5-turbo",
            "summarizer": "gpt-3.5-turbo",
            "categorizer": "gpt-3.5-turbo"
        }
        
    def _get_api_key(self, service):
        """Obtiene la API key para un servicio específico"""
        key = self.api_keys.get(service)
        if not key:
            self.logger.log_error(service, "No se encontró la API key")
            # Si no hay key específica, usar la key principal como fallback
            return os.getenv("OPENAI_API_KEY")
        return key

    def analyze_emotion(self, text):
        """Analiza el texto para determinar emociones y sentimientos"""
        start_time = time.time()
        try:
            openai.api_key = self._get_api_key("emotion")
            self.metrics.record_request("emotion")
            
            response = openai.ChatCompletion.create(
                model=self.models["emotion"],
                messages=[
                    {"role": "system", "content": (
                        "Eres un analizador de emociones y sentimientos. "
                        "Analiza el texto y devuelve un JSON con: "
                        "1. La emoción principal (feliz, triste, enojado, sorprendido, neutral) "
                        "2. La intensidad (0.0 a 1.0) "
                        "3. Palabras clave que indican la emoción "
                        "4. Contexto emocional "
                        "Responde SOLO con el JSON, sin texto adicional."
                    )},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Registrar métricas
            self.metrics.record_api_usage("emotion", response.usage.total_tokens)
            self.metrics.record_response_time("emotion", (time.time() - start_time) * 1000)
            self.metrics.record_emotion(result['emotion'])
            
            # Registrar en logs
            self.logger.log_emotion_analysis(text, result)
            
            return result
        except Exception as e:
            self.metrics.record_error("emotion")
            self.logger.log_error("emotion", str(e))
            return {
                "emotion": "neutral",
                "intensity": 0.5,
                "keywords": [],
                "context": "neutral"
            }

    def summarize_conversation(self, conversations, max_length=200):
        """Resume una serie de conversaciones"""
        start_time = time.time()
        try:
            openai.api_key = self._get_api_key("summarizer")
            self.metrics.record_request("summarizer")
            
            # Preparar el contexto de las conversaciones
            conversation_text = "\n".join([
                f"Usuario: {conv['user_input']}\nBot: {conv['bot_response']}"
                for conv in conversations
            ])
            
            response = openai.ChatCompletion.create(
                model=self.models["summarizer"],
                messages=[
                    {"role": "system", "content": (
                        "Eres un resumidor de conversaciones. "
                        "Crea un resumen conciso y relevante de la conversación, "
                        "manteniendo los puntos más importantes y el contexto emocional. "
                        f"El resumen no debe exceder {max_length} caracteres."
                    )},
                    {"role": "user", "content": conversation_text}
                ],
                temperature=0.5
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Registrar métricas
            self.metrics.record_api_usage("summarizer", response.usage.total_tokens)
            self.metrics.record_response_time("summarizer", (time.time() - start_time) * 1000)
            
            # Registrar en logs
            self.logger.log_summarization(conversations, summary)
            
            return summary
        except Exception as e:
            self.metrics.record_error("summarizer")
            self.logger.log_error("summarizer", str(e))
            return ""

    def categorize_memory(self, text, response):
        """Categoriza una memoria basada en su contenido"""
        start_time = time.time()
        try:
            openai.api_key = self._get_api_key("categorizer")
            self.metrics.record_request("categorizer")
            
            response = openai.ChatCompletion.create(
                model=self.models["categorizer"],
                messages=[
                    {"role": "system", "content": (
                        "Eres un categorizador de memorias. "
                        "Analiza el texto y devuelve un JSON con: "
                        "1. Categoría principal (personal, temporal, importante) "
                        "2. Importancia (0.0 a 1.0) "
                        "3. Etiquetas relevantes "
                        "4. Razón de la categorización "
                        "Responde SOLO con el JSON, sin texto adicional."
                    )},
                    {"role": "user", "content": f"Usuario: {text}\nBot: {response}"}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Registrar métricas
            self.metrics.record_api_usage("categorizer", response.usage.total_tokens)
            self.metrics.record_response_time("categorizer", (time.time() - start_time) * 1000)
            self.metrics.record_memory_operation("categorization")
            
            # Registrar en logs
            self.logger.log_categorization(text, response, result)
            
            return result
        except Exception as e:
            self.metrics.record_error("categorizer")
            self.logger.log_error("categorizer", str(e))
            return {
                "category": "temporal",
                "importance": 0.5,
                "tags": [],
                "reason": "Error en categorización"
            }

    def analyze_context(self, text, recent_memories):
        """Analiza el contexto completo de una interacción"""
        start_time = time.time()
        try:
            openai.api_key = self._get_api_key("emotion")
            self.metrics.record_request("context")
            
            # Preparar el contexto
            context = "\n".join([
                f"Memoria {i+1}: {mem['text']} -> {mem['response']}"
                for i, mem in enumerate(recent_memories)
            ])
            
            response = openai.ChatCompletion.create(
                model=self.models["emotion"],
                messages=[
                    {"role": "system", "content": (
                        "Eres un analizador de contexto. "
                        "Analiza el texto y el contexto histórico, y devuelve un JSON con: "
                        "1. Tema principal de la conversación "
                        "2. Estado emocional del usuario "
                        "3. Patrones de interacción "
                        "4. Sugerencias de respuesta "
                        "Responde SOLO con el JSON, sin texto adicional."
                    )},
                    {"role": "user", "content": f"Contexto:\n{context}\n\nMensaje actual: {text}"}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Registrar métricas
            self.metrics.record_api_usage("context", response.usage.total_tokens)
            self.metrics.record_response_time("context", (time.time() - start_time) * 1000)
            
            # Registrar en logs
            self.logger.log_context_analysis(text, recent_memories, result)
            
            return result
        except Exception as e:
            self.metrics.record_error("context")
            self.logger.log_error("context", str(e))
            return {
                "topic": "general",
                "user_emotion": "neutral",
                "patterns": [],
                "suggestions": []
            } 