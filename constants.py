# Configuración de audio
INPUT_INDEX = 5  # Índice del dispositivo de entrada (Voicemeeter)
OUTPUT_INDEX = 20  # Índice del dispositivo de salida

# Configuración de TTS
TTS_LANGUAGE = "es-ES"
TTS_VOICE = "female"  # Voz femenina
TTS_SPEED = 1.0
TTS_ENGINE = "pyttsx3"  # Motor TTS por defecto

# Configuración de OpenAI
AI_MODEL = "gpt-4o-mini"  # Modelo por defecto
MAX_TOKENS = 150  # Límite de tokens por respuesta

# Configuración de memoria
MEMORY_PATH = "memorias/"
USE_EMBEDDINGS = True
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modelo ligero para embeddings

# Configuración de STT
STT_LANGUAGE = "es-ES"
STT_TIMEOUT = 0.5  # Tiempo de espera para detección de silencio
NOISE_THRESHOLD = 0.1  # Umbral de ruido

# Configuración de búsqueda
SEARCH_ENGINE = "google"  # Motor de búsqueda por defecto

# Configuración de filtrado
BANNED_WORDS = []  # Lista de palabras prohibidas
FILTER_PHONE_NUMBERS = True
FILTER_ADDRESSES = True

# Configuración de temporizadores
TIMER_CHECK_INTERVAL = 1  # Intervalo de verificación de temporizadores en segundos 