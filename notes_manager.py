import os
import json
import re
from datetime import datetime
import constants

class NotesManager:
    def __init__(self):
        self.notes_dir = os.path.join(constants.MEMORY_PATH, 'notes')
        os.makedirs(self.notes_dir, exist_ok=True)
        self.notes_file = os.path.join(self.notes_dir, 'notes.json')
        self._load_notes()

    def _load_notes(self):
        """Carga las notas desde el archivo"""
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                self.notes = json.load(f)
        else:
            self.notes = {}

    def _save_notes(self):
        """Guarda las notas en el archivo"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def process_note_request(self, text):
        """Procesa una solicitud de nota desde la IA"""
        try:
            # Detectar tipo de operación
            if self._is_create_note(text):
                return self._create_note(text)
            elif self._is_read_note(text):
                return self._read_note(text)
            elif self._is_delete_note(text):
                return self._delete_note(text)
            else:
                return "No pude entender qué querías hacer con las notas."

        except Exception as e:
            print(f"Error al procesar nota: {str(e)}")
            return "Hubo un error al procesar la nota."

    def _is_create_note(self, text):
        """Detecta si el texto es una solicitud para crear una nota"""
        patterns = [
            r'crea\s+(?:una\s+)?nota\s+(?:que\s+diga\s+)?["\']?([^"\']+)["\']?\s+(?:como|con\s+el\s+título|titulada)\s+["\']?([^"\']+)["\']?',
            r'guarda\s+(?:una\s+)?nota\s+(?:que\s+diga\s+)?["\']?([^"\']+)["\']?\s+(?:como|con\s+el\s+título|titulada)\s+["\']?([^"\']+)["\']?',
        ]
        return any(re.search(pattern, text.lower()) for pattern in patterns)

    def _is_read_note(self, text):
        """Detecta si el texto es una solicitud para leer una nota"""
        patterns = [
            r'lee\s+(?:la\s+)?nota\s+["\']?([^"\']+)["\']?',
            r'muestra\s+(?:la\s+)?nota\s+["\']?([^"\']+)["\']?',
            r'qué\s+dice\s+(?:la\s+)?nota\s+["\']?([^"\']+)["\']?',
        ]
        return any(re.search(pattern, text.lower()) for pattern in patterns)

    def _is_delete_note(self, text):
        """Detecta si el texto es una solicitud para eliminar una nota"""
        patterns = [
            r'borra\s+(?:la\s+)?nota\s+["\']?([^"\']+)["\']?',
            r'elimina\s+(?:la\s+)?nota\s+["\']?([^"\']+)["\']?',
        ]
        return any(re.search(pattern, text.lower()) for pattern in patterns)

    def _create_note(self, text):
        """Crea una nueva nota"""
        pattern = r'["\']?([^"\']+)["\']?\s+(?:como|con\s+el\s+título|titulada)\s+["\']?([^"\']+)["\']?'
        match = re.search(pattern, text.lower())
        
        if match:
            content = match.group(1)
            title = match.group(2)
            
            self.notes[title] = {
                'content': content,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self._save_notes()
            return f"Nota '{title}' creada correctamente."
        
        return "No pude entender el contenido o el título de la nota."

    def _read_note(self, text):
        """Lee una nota existente"""
        pattern = r'["\']?([^"\']+)["\']?'
        match = re.search(pattern, text.lower())
        
        if match:
            title = match.group(1)
            if title in self.notes:
                return f"Nota '{title}':\n{self.notes[title]['content']}"
            return f"No encontré la nota '{title}'."
        
        return "No pude entender el título de la nota."

    def _delete_note(self, text):
        """Elimina una nota existente"""
        pattern = r'["\']?([^"\']+)["\']?'
        match = re.search(pattern, text.lower())
        
        if match:
            title = match.group(1)
            if title in self.notes:
                del self.notes[title]
                self._save_notes()
                return f"Nota '{title}' eliminada correctamente."
            return f"No encontré la nota '{title}'."
        
        return "No pude entender el título de la nota."

    def list_notes(self):
        """Lista todas las notas disponibles"""
        if not self.notes:
            return "No hay notas guardadas."
        
        notes_list = "Notas disponibles:\n\n"
        for title, note in self.notes.items():
            notes_list += f"- {title}\n"
        
        return notes_list 