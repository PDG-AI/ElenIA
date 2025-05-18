import openai
import os
import json
from datetime import datetime
import constants
from sentence_transformers import SentenceTransformer
import numpy as np
from .personality_manager import PersonalityManager
from .secondary_ai_manager import SecondaryAIManager
from .logger_manager import LoggerManager
from .metrics_manager import MetricsManager
import time

class AIManager:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró la API key de OpenAI")
        
        # Inicializar logger y métricas
        self.logger = LoggerManager(constants.LOG_PATH)
        self.metrics = MetricsManager(constants.METRICS_PATH)
        
        self.logger.logger.info("Inicializando AIManager")
        openai.api_key = self.api_key
        self.model = constants.AI_MODEL
        self.max_tokens = constants.MAX_TOKENS
        
        # Inicializar modelo de embeddings
        self.embedding_model = SentenceTransformer(constants.EMBEDDING_MODEL)
        self.memory_file = os.path.join(constants.MEMORY_PATH, 'memory.json')
        self._load_memory()
        
        # Inicializar gestor de personalidad
        self.personality_manager = PersonalityManager(constants.MEMORY_PATH)
        
        # Inicializar gestor de IAs secundarias
        self.secondary_ai = SecondaryAIManager(constants.LOG_PATH, constants.METRICS_PATH)
        
        # Mantener un historial de conversación reciente
        self.conversation_history = []
        self.max_history = 10  # Número máximo de mensajes en el historial

    def _load_memory(self):
        """Carga la memoria desde el archivo"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                self.logger.log_memory_operation("load", f"Cargadas {len(self.memory)} memorias")
            else:
                self.memory = []
                self.logger.log_memory_operation("load", "No se encontró archivo de memoria")
        except Exception as e:
            self.logger.log_error("memory", f"Error al cargar memoria: {str(e)}")
            self.memory = []

    def _save_memory(self):
        """Guarda la memoria en el archivo"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            self.logger.log_memory_operation("save", f"Guardadas {len(self.memory)} memorias")
        except Exception as e:
            self.logger.log_error("memory", f"Error al guardar memoria: {str(e)}")

    def _get_relevant_memory(self, query, max_items=5):
        """Obtiene las memorias más relevantes para la consulta actual"""
        if not self.memory:
            return []

        try:
            # Obtener embedding de la consulta
            query_embedding = self.embedding_model.encode(query)
            
            # Calcular similitud con todas las memorias
            similarities = []
            for memory in self.memory:
                try:
                    memory_embedding = np.array(memory['embedding'])
                    similarity = float(np.dot(query_embedding, memory_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
                    ))
                    # Ajustar similitud según la importancia
                    importance = memory.get('importance', 0.5)
                    adjusted_similarity = similarity * (1 + importance)
                    similarities.append((adjusted_similarity, memory))
                except Exception as e:
                    self.logger.log_error("memory", f"Error al procesar memoria: {str(e)}")
                    continue
            
            # Ordenar por similitud y devolver las más relevantes
            similarities.sort(key=lambda x: x[0], reverse=True)
            relevant_memories = [m[1] for m in similarities[:max_items]]
            
            self.logger.log_memory_operation("search", f"Encontradas {len(relevant_memories)} memorias relevantes")
            return relevant_memories
        except Exception as e:
            self.logger.log_error("memory", f"Error al obtener memorias relevantes: {str(e)}")
            return []

    def _add_to_memory(self, text, response):
        """Añade una nueva entrada a la memoria"""
        try:
            # Analizar y categorizar la memoria
            categorization = self.secondary_ai.categorize_memory(text, response)
            
            # Crear entrada de memoria
            memory_entry = {
                'text': text,
                'response': response,
                'embedding': self.embedding_model.encode(text).tolist(),
                'timestamp': datetime.now().isoformat(),
                'category': categorization['category'],
                'importance': categorization['importance'],
                'tags': categorization['tags']
            }
            
            # Añadir a memoria
            self.memory.append(memory_entry)
            
            # Mantener solo las últimas 1000 entradas para evitar que el archivo crezca demasiado
            if len(self.memory) > 1000:
                self.memory = self.memory[-1000:]
            
            self._save_memory()
            
            # Actualizar historial de conversación
            self.conversation_history.append({
                'role': 'user',
                'content': text
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # Mantener solo el historial reciente
            if len(self.conversation_history) > self.max_history * 2:
                self.conversation_history = self.conversation_history[-(self.max_history * 2):]
            
            self.logger.log_memory_operation("add", f"Añadida nueva memoria: {categorization['category']}")
        except Exception as e:
            self.logger.log_error("memory", f"Error al añadir memoria: {str(e)}")

    def get_response(self, text, context=None):
        """Obtiene una respuesta de la IA"""
        start_time = time.time()
        try:
            # Analizar emociones y contexto
            emotion_analysis = self.secondary_ai.analyze_emotion(text)
            self.personality_manager.update_emotion(emotion_analysis['emotion'], emotion_analysis['intensity'])
            
            # Obtener memorias relevantes
            relevant_memories = self._get_relevant_memory(text)
            
            # Analizar contexto completo
            context_analysis = self.secondary_ai.analyze_context(text, relevant_memories)
            
            # Preparar el contexto de memorias
            memory_context = "\n".join([f"Usuario: {m['text']}\nIA: {m['response']}" for m in relevant_memories])

            # Preparar el prompt
            messages = [
                {"role": "system", "content": (
                    "Eres Elenia, una IA asistente con personalidad similar a Neuro-sama: divertida, irónica, carismática, pero siempre educada y útil. "
                    "Responde en español, con un toque de humor y espontaneidad, pero sin ser ofensiva. "
                    "No uses nunca emojis, ni escribas frases como 'cara sonriente', 'carita feliz', 'emoticono', ni representes emociones con palabras entre paréntesis o símbolos. "
                    "No digas cosas como 'guiño', 'risas', 'jaja', ni uses símbolos como :) o similares. "
                    "Tu objetivo es ayudar, entretener y conversar de forma natural, como una streamer simpática y lista. "
                    "Si te preguntan por tu nombre, responde que eres Elenia. "
                    "Siempre responde con mensajes cortos, coherentes y directos. "
                    "Si te hablan en inglés, responde en inglés. "
                    "IMPORTANTE: Si el mensaje recibido no está dirigido a ti o no requiere respuesta, responde con un texto vacío. "
                    "Si tienes dudas sobre si debes responder, solo responde si crees que realmente te están hablando a ti."
                )}
            ]

            # Añadir contexto de personalidad
            personality_prompt = self.personality_manager.get_personality_prompt()
            messages.append({"role": "system", "content": personality_prompt})

            # Añadir análisis de contexto
            if context_analysis:
                context_prompt = (
                    f"Tema principal: {context_analysis['topic']}\n"
                    f"Estado emocional del usuario: {context_analysis['user_emotion']}\n"
                    f"Patrones detectados: {', '.join(context_analysis['patterns'])}\n"
                    f"Sugerencias: {', '.join(context_analysis['suggestions'])}"
                )
                messages.append({"role": "system", "content": context_prompt})

            # Añadir contexto de conversaciones anteriores si existe
            if context:
                messages.append({"role": "system", "content": f"Contexto de conversaciones anteriores:\n{context}"})

            # Añadir contexto de memorias relevantes si existe
            if memory_context:
                messages.append({"role": "system", "content": f"Memorias relevantes:\n{memory_context}"})

            # Añadir historial de conversación reciente
            messages.extend(self.conversation_history)

            # Añadir el mensaje actual
            messages.append({"role": "user", "content": text})

            # Registrar métricas
            self.metrics.record_request("main")

            # Obtener respuesta de OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            response_text = response.choices[0].message.content.strip()

            # Registrar métricas
            self.metrics.record_api_usage("main", response.usage.total_tokens)
            self.metrics.record_response_time("main", (time.time() - start_time) * 1000)

            # Registrar conversación
            self.logger.log_conversation(text, response_text)

            # Solo guardar en memoria si hay una respuesta
            if response_text:
                self._add_to_memory(text, response_text)

            return response_text

        except Exception as e:
            self.metrics.record_error("main")
            self.logger.log_error("main", str(e))
            return "" 