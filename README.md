# ElenIA - Asistente de IA con Personalidad

ElenIA es un asistente de IA con personalidad similar a Neuro-sama, diseñado para ser utilizado en streams y como asistente personal. Utiliza reconocimiento de voz en tiempo real y síntesis de voz para una interacción natural.

## Características

- Reconocimiento de voz en tiempo real con ajuste automático de ruido
- Síntesis de voz con voz femenina
- Integración con OpenAI GPT
- Sistema de memoria con embeddings
- Gestión de temporizadores
- Sistema de búsqueda web
- Gestión de notas
- Filtrado de contenido sensible
- Personalidad amigable y graciosa

## Requisitos

- Python 3.11.9
- CUDA 11.8 (opcional, para aceleración GPU)
- Voicemeeter (para captura de audio)
- API Key de OpenAI

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/ElenIA.git
cd ElenIA
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Crea un archivo `.env` en la raíz del proyecto y añade tu API key de OpenAI:
```
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_API_KEY_S1=tu_api_key_aqui
OPENAI_API_KEY_S2=tu_api_key_aqui
OPENAI_API_KEY_S3=tu_api_key_aqui
```

5. Mueve los siguientes archivos a una carpeta llamada "modulos"
```
ai_manager.py
constants.py
filtrador.py
logger_manager.py
memory_manager.py
metrics_manager.py
notes_manager.py
personality_manager.py
searchs_manager.py
secondary_ai_manager.py
stt.py
timer_manager.py
tts.py
```

6. Configura las variables marcadas como #unicas de constants.py
```
```

## Configuración

1. Configura las preferencias de voz en `tts.py`:
```
puedes cambiar el pitch y demas
```

## Uso

1. Asegúrate de que Voicemeeter está configurado correctamente
2. Activa el entorno virtual si no está activado
3. Ejecuta el bot:
```
python bot.py
```

## Estructura del Proyecto

```
ElenIA/
├── bot.py              # Archivo principal
├── constants.py        # Configuraciones
├── requirements.txt    # Dependencias
├── .env               # Variables de entorno
├── modulos/           # Módulos del bot
│   ├── stt.py         # Reconocimiento de voz
│   ├── tts.py         # Síntesis de voz
│   ├── ai_manager.py  # Gestión de IA
│   ├── timer_manager.py # Temporizadores
│   ├── searchs_manager.py # Búsquedas
│   ├── notes_manager.py   # Notas
│   ├── filtrador.py   # Filtrado de contenido
|   └── ...
└── memorias/          # Almacenamiento de memoria
```

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir los cambios propuestos.

## Licencia

Este proyecto está bajo la Licencia MIT.
