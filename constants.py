import os

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_PATH = os.path.join(BASE_DIR, 'data', 'memory')
LOG_PATH = os.path.join(BASE_DIR, 'data', 'logs')
METRICS_PATH = os.path.join(BASE_DIR, 'data', 'metrics')

# Configuración de la IA
AI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Configuración de memoria
MAX_MEMORY_ITEMS = 1000
MEMORY_RELEVANCE_THRESHOLD = 0.7

# Configuración de personalidad
EMOTION_DECAY_RATE = 0.1
MAX_EMOTION_INTENSITY = 1.0
MIN_EMOTION_INTENSITY = 0.0

# Configuración de conversación
MAX_CONVERSATION_HISTORY = 10
MAX_SUMMARY_LENGTH = 200 