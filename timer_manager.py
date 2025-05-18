import time
import threading
import re
from datetime import datetime, timedelta
import constants

class TimerManager:
    def __init__(self):
        self.timers = {}
        self.check_interval = constants.TIMER_CHECK_INTERVAL
        self._start_checker_thread()

    def _start_checker_thread(self):
        """Inicia el hilo que verifica los temporizadores"""
        def checker():
            while True:
                self._check_timers()
                time.sleep(self.check_interval)

        thread = threading.Thread(target=checker, daemon=True)
        thread.start()

    def _check_timers(self):
        """Verifica los temporizadores activos"""
        current_time = datetime.now()
        expired_timers = []

        for timer_id, timer_info in self.timers.items():
            if current_time >= timer_info['end_time']:
                expired_timers.append(timer_id)

        for timer_id in expired_timers:
            self._execute_timer_callback(timer_id)

    def _execute_timer_callback(self, timer_id):
        """Ejecuta el callback del temporizador y lo elimina"""
        if timer_id in self.timers:
            timer_info = self.timers[timer_id]
            if timer_info['callback']:
                timer_info['callback'](timer_info['message'])
            del self.timers[timer_id]

    def _parse_time(self, text):
        """Parsea el texto para extraer el tiempo del temporizador"""
        # Patrones comunes de tiempo
        patterns = {
            r'(\d+)\s*minutos?': lambda x: timedelta(minutes=int(x)),
            r'(\d+)\s*horas?': lambda x: timedelta(hours=int(x)),
            r'(\d+)\s*segundos?': lambda x: timedelta(seconds=int(x)),
        }

        for pattern, converter in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                return converter(match.group(1))

        return None

    def process_timer_request(self, text):
        """Procesa una solicitud de temporizador desde la IA"""
        try:
            # Extraer tiempo
            duration = self._parse_time(text)
            if not duration:
                return "No pude entender la duración del temporizador."

            # Crear mensaje para el temporizador
            message = f"¡Tiempo terminado! {text}"

            # Crear callback para el temporizador
            def timer_callback(msg):
                print(f"Temporizador: {msg}")

            # Añadir temporizador
            timer_id = f"timer_{len(self.timers)}"
            self.timers[timer_id] = {
                'end_time': datetime.now() + duration,
                'message': message,
                'callback': timer_callback
            }

            return f"Temporizador configurado para {duration.total_seconds()} segundos."

        except Exception as e:
            print(f"Error al procesar temporizador: {str(e)}")
            return "Hubo un error al configurar el temporizador."

    def cancel_timer(self, timer_id):
        """Cancela un temporizador específico"""
        if timer_id in self.timers:
            del self.timers[timer_id]
            return True
        return False

    def get_active_timers(self):
        """Obtiene la lista de temporizadores activos"""
        return {
            timer_id: {
                'remaining': (info['end_time'] - datetime.now()).total_seconds(),
                'message': info['message']
            }
            for timer_id, info in self.timers.items()
        } 