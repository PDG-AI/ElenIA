import requests
from bs4 import BeautifulSoup
import re
import constants

class SearchManager:
    def __init__(self):
        self.search_engine = constants.SEARCH_ENGINE
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def process_search_request(self, text):
        """Procesa una solicitud de búsqueda desde la IA"""
        try:
            # Extraer la consulta de búsqueda
            query = self._extract_search_query(text)
            if not query:
                return "No pude entender qué querías buscar."

            # Realizar la búsqueda
            results = self._search(query)
            if not results:
                return "No encontré resultados para tu búsqueda."

            # Formatear resultados
            formatted_results = self._format_results(results)
            return formatted_results

        except Exception as e:
            print(f"Error al procesar búsqueda: {str(e)}")
            return "Hubo un error al realizar la búsqueda."

    def _extract_search_query(self, text):
        """Extrae la consulta de búsqueda del texto"""
        # Patrones comunes para extraer consultas
        patterns = [
            r'busca\s+(?:sobre|acerca de|información sobre)?\s*["\']?([^"\']+)["\']?',
            r'encuentra\s+(?:información sobre)?\s*["\']?([^"\']+)["\']?',
            r'qué es\s+["\']?([^"\']+)["\']?',
            r'quién es\s+["\']?([^"\']+)["\']?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()

        return None

    def _search(self, query):
        """Realiza la búsqueda según el motor configurado"""
        if self.search_engine == "google":
            return self._google_search(query)
        else:
            return self._google_search(query)  # Por defecto usa Google

    def _google_search(self, query):
        """Realiza una búsqueda en Google"""
        try:
            url = f"https://www.google.com/search?q={query}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            # Extraer resultados principales
            for result in soup.select('div.g'):
                title_elem = result.select_one('h3')
                link_elem = result.select_one('a')
                snippet_elem = result.select_one('div.VwiC3b')

                if title_elem and link_elem and snippet_elem:
                    results.append({
                        'title': title_elem.text,
                        'link': link_elem['href'],
                        'snippet': snippet_elem.text
                    })

                if len(results) >= 3:  # Limitar a 3 resultados
                    break

            return results

        except Exception as e:
            print(f"Error en búsqueda de Google: {str(e)}")
            return []

    def _format_results(self, results):
        """Formatea los resultados de búsqueda"""
        if not results:
            return "No encontré resultados."

        formatted = "Aquí están los resultados más relevantes:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n\n"

        return formatted

    def set_search_engine(self, engine):
        """Cambia el motor de búsqueda"""
        if engine in ["google", "bing", "duckduckgo"]:
            self.search_engine = engine
            return True
        return False 