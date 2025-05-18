import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, memory_path):
        self.memory_path = memory_path
        self.memory_file = os.path.join(memory_path, "memory.json")
        self.memory = self._load_memory()

    def _load_memory(self):
        """Carga la memoria desde el archivo JSON"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {
                    "conversations": [],
                    "facts": {},
                    "preferences": {},
                    "categories": {
                        "personal": [],
                        "temporal": [],
                        "importante": []
                    }
                }
        return {
            "conversations": [],
            "facts": {},
            "preferences": {},
            "categories": {
                "personal": [],
                "temporal": [],
                "importante": []
            }
        }

    def _save_memory(self):
        """Guarda la memoria en el archivo JSON"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def add_conversation(self, user_input, bot_response, category="temporal", importance=0.5):
        """Añade una conversación a la memoria con categoría e importancia"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response,
            "category": category,
            "importance": importance
        }
        
        # Añadir a la categoría correspondiente
        if category in self.memory["categories"]:
            self.memory["categories"][category].append(conversation)
            # Mantener solo las últimas 50 conversaciones por categoría
            if len(self.memory["categories"][category]) > 50:
                self.memory["categories"][category] = self.memory["categories"][category][-50:]
        
        # Añadir también a conversaciones generales
        self.memory["conversations"].append(conversation)
        if len(self.memory["conversations"]) > 50:
            self.memory["conversations"] = self.memory["conversations"][-50:]
            
        self._save_memory()

    def add_fact(self, key, value, category="temporal", importance=0.5):
        """Añade un hecho a la memoria con categoría e importancia"""
        fact = {
            "value": value,
            "category": category,
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["facts"][key] = fact
        self._save_memory()

    def add_preference(self, key, value):
        """Añade una preferencia del usuario"""
        self.memory["preferences"][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save_memory()

    def get_recent_conversations(self, limit=5, category=None):
        """Obtiene las conversaciones más recientes, opcionalmente filtradas por categoría"""
        if category and category in self.memory["categories"]:
            return self.memory["categories"][category][-limit:]
        return self.memory["conversations"][-limit:]

    def get_fact(self, key):
        """Obtiene un hecho específico"""
        return self.memory["facts"].get(key)

    def get_all_facts(self, category=None):
        """Obtiene todos los hechos, opcionalmente filtrados por categoría"""
        if category:
            return {k: v for k, v in self.memory["facts"].items() if v["category"] == category}
        return self.memory["facts"]

    def get_preference(self, key):
        """Obtiene una preferencia específica del usuario"""
        return self.memory["preferences"].get(key)

    def get_important_memories(self, limit=5):
        """Obtiene las memorias más importantes"""
        all_memories = []
        
        # Recopilar conversaciones importantes
        for category in self.memory["categories"].values():
            all_memories.extend(category)
        
        # Ordenar por importancia
        all_memories.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return all_memories[:limit]

    def update_importance(self, memory_id, new_importance):
        """Actualiza la importancia de una memoria"""
        for category in self.memory["categories"].values():
            for memory in category:
                if memory.get("timestamp") == memory_id:
                    memory["importance"] = new_importance
                    self._save_memory()
                    return True
        return False 