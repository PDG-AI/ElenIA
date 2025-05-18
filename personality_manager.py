import json
import os
from datetime import datetime

class PersonalityManager:
    def __init__(self, memory_path):
        self.memory_path = memory_path
        self.personality_file = os.path.join(memory_path, "personality.json")
        self.emotions = {
            "feliz": 0.5,
            "triste": 0.0,
            "enojado": 0.0,
            "sorprendido": 0.0,
            "neutral": 0.5
        }
        self.personality_traits = {
            "humor": 0.7,
            "formalidad": 0.3,
            "energia": 0.6,
            "empatia": 0.8
        }
        self._load_personality()

    def _load_personality(self):
        """Carga la personalidad desde el archivo"""
        if os.path.exists(self.personality_file):
            try:
                with open(self.personality_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.emotions = data.get("emotions", self.emotions)
                    self.personality_traits = data.get("traits", self.personality_traits)
            except json.JSONDecodeError:
                self._save_personality()

    def _save_personality(self):
        """Guarda la personalidad en el archivo"""
        data = {
            "emotions": self.emotions,
            "traits": self.personality_traits,
            "last_update": datetime.now().isoformat()
        }
        with open(self.personality_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update_emotion(self, emotion, value):
        """Actualiza el valor de una emoción"""
        if emotion in self.emotions:
            self.emotions[emotion] = max(0.0, min(1.0, value))
            self._normalize_emotions()
            self._save_personality()

    def _normalize_emotions(self):
        """Normaliza las emociones para que sumen 1.0"""
        total = sum(self.emotions.values())
        if total > 0:
            for emotion in self.emotions:
                self.emotions[emotion] /= total

    def get_emotion_context(self):
        """Obtiene el contexto emocional actual"""
        dominant_emotion = max(self.emotions.items(), key=lambda x: x[1])[0]
        return {
            "dominant_emotion": dominant_emotion,
            "emotion_values": self.emotions,
            "personality_traits": self.personality_traits
        }

    def adjust_personality(self, trait, value):
        """Ajusta un rasgo de personalidad"""
        if trait in self.personality_traits:
            self.personality_traits[trait] = max(0.0, min(1.0, value))
            self._save_personality()

    def get_personality_prompt(self):
        """Genera un prompt basado en la personalidad actual"""
        context = self.get_emotion_context()
        dominant_emotion = context["dominant_emotion"]
        
        # Ajustar el tono según la emoción dominante
        tone_adjustments = {
            "feliz": "más entusiasta y positiva",
            "triste": "más empática y comprensiva",
            "enojado": "más directa y firme",
            "sorprendido": "más curiosa y expresiva",
            "neutral": "equilibrada y profesional"
        }
        
        # Ajustar el estilo según los rasgos de personalidad
        style_adjustments = []
        if self.personality_traits["humor"] > 0.6:
            style_adjustments.append("con un toque de humor")
        if self.personality_traits["formalidad"] > 0.6:
            style_adjustments.append("de manera más formal")
        if self.personality_traits["energia"] > 0.6:
            style_adjustments.append("con más energía")
        if self.personality_traits["empatia"] > 0.6:
            style_adjustments.append("mostrando más empatía")
        
        style = " y ".join(style_adjustments) if style_adjustments else "de manera natural"
        
        return f"Actualmente te sientes {tone_adjustments[dominant_emotion]}, responde {style}." 