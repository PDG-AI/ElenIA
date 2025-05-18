import re
import constants

class Filtrador:
    def __init__(self):
        self.banned_words = set(constants.BANNED_WORDS)
        self.filter_phone_numbers = constants.FILTER_PHONE_NUMBERS
        self.filter_addresses = constants.FILTER_ADDRESSES

    def filter(self, text):
        """Filtra el texto según las reglas configuradas"""
        if not text:
            return text

        # Filtrar palabras prohibidas
        text = self._filter_banned_words(text)
        
        # Filtrar números de teléfono
        if self.filter_phone_numbers:
            text = self._filter_phone_numbers(text)
        
        # Filtrar direcciones
        if self.filter_addresses:
            text = self._filter_addresses(text)
        
        # Filtrar emojis y frases prohibidas
        text = self._filter_emojis_and_faces(text)
        
        return text

    def _filter_banned_words(self, text):
        """Filtra palabras prohibidas"""
        words = text.split()
        filtered_words = []
        
        for word in words:
            if word.lower() in self.banned_words:
                filtered_words.append('*' * len(word))
            else:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)

    def _filter_phone_numbers(self, text):
        """Filtra números de teléfono"""
        # Patrones comunes de números de teléfono
        patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{3}\b',  # 123-456-789
            r'\b\+?\d{1,3}[-.]?\d{2,3}[-.]?\d{2,3}[-.]?\d{2,3}\b',  # +34 123 456 789
            r'\b\d{9}\b'  # 123456789
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '[NÚMERO DE TELÉFONO]', text)
        
        return text

    def _filter_addresses(self, text):
        """Filtra direcciones"""
        # Patrones comunes de direcciones
        patterns = [
            r'\b(?:Calle|Avenida|Plaza|Paseo)\s+[A-Za-záéíóúÁÉÍÓÚñÑ\s]+\s+\d+\b',  # Calle Mayor 123
            r'\b\d+\s+(?:Calle|Avenida|Plaza|Paseo)\s+[A-Za-záéíóúÁÉÍÓÚñÑ\s]+\b',  # 123 Calle Mayor
            r'\b[A-Za-záéíóúÁÉÍÓÚñÑ\s]+\s+\d+\s+(?:1º|2º|3º|4º|5º|6º|7º|8º|9º|10º)\b'  # Mayor 123 1º
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '[DIRECCIÓN]', text)
        
        return text

    def _filter_emojis_and_faces(self, text):
        """Elimina emojis y frases como 'cara sonriente', 'carita feliz', etc."""
        # Eliminar emojis (unicode)
        emoji_pattern = re.compile("[\U00010000-\U0010ffff\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        # Eliminar frases típicas
        frases = [
            'cara sonriente', 'carita feliz', 'emoticono', 'guiño', 'risas', 'jaja', 'jeje', 'xd', 'xD', ':)', ':(', ';)', ':D', ':P', 'uwu', 'owo', 'n_n', '^-^', ':3', ':v', ':o', ':O', ':|', ':*', ':$', ':@', ':#', ':&', ':/', ':\\', ':]', ':[', ':>', ':<', ':}', ':{', ':]', ':[', ':-)', ':-(', ';-)', ':-D', ':-P', ':-o', ':-O', ':-|', ':-*', ':-$', ':-@', ':-#', ':-&', ':-/', ':-\\', 'nwn', 'TwT', 'T_T', 'u_u', 'UwU', 'OwO', 'n_n', '^-^', ':3', ':v', ':o', ':O', ':|', ':*', ':$', ':@', ':#', ':&', ':/', ':\\', ':]', ':[', ':>', ':<', ':}', ':{'
        ]
        for frase in frases:
            text = re.sub(rf'\b{re.escape(frase)}\b', '', text, flags=re.IGNORECASE)
        return text.strip()

    def add_banned_word(self, word):
        """Añade una palabra a la lista de prohibidas"""
        self.banned_words.add(word.lower())
        return True

    def remove_banned_word(self, word):
        """Elimina una palabra de la lista de prohibidas"""
        if word.lower() in self.banned_words:
            self.banned_words.remove(word.lower())
            return True
        return False

    def get_banned_words(self):
        """Obtiene la lista de palabras prohibidas"""
        return list(self.banned_words) 