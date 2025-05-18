import json
import os
from datetime import datetime
from collections import defaultdict

class MetricsManager:
    def __init__(self, metrics_path):
        self.metrics_path = metrics_path
        self.metrics_file = os.path.join(metrics_path, 'metrics.json')
        self._load_metrics()

    def _load_metrics(self):
        """Carga las métricas desde el archivo"""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                self.metrics = json.load(f)
        else:
            self.metrics = {
                'api_usage': defaultdict(int),
                'response_times': defaultdict(list),
                'error_rates': defaultdict(int),
                'total_requests': defaultdict(int),
                'emotion_distribution': defaultdict(int),
                'memory_operations': defaultdict(int),
                'last_updated': datetime.now().isoformat()
            }
            self._save_metrics()

    def _save_metrics(self):
        """Guarda las métricas en el archivo"""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        self.metrics['last_updated'] = datetime.now().isoformat()
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=2)

    def record_api_usage(self, service, tokens_used):
        """Registra el uso de tokens de una API"""
        self.metrics['api_usage'][service] += tokens_used
        self._save_metrics()

    def record_response_time(self, service, time_ms):
        """Registra el tiempo de respuesta de un servicio"""
        self.metrics['response_times'][service].append(time_ms)
        # Mantener solo los últimos 1000 tiempos
        if len(self.metrics['response_times'][service]) > 1000:
            self.metrics['response_times'][service] = self.metrics['response_times'][service][-1000:]
        self._save_metrics()

    def record_error(self, service):
        """Registra un error en un servicio"""
        self.metrics['error_rates'][service] += 1
        self._save_metrics()

    def record_request(self, service):
        """Registra una petición a un servicio"""
        self.metrics['total_requests'][service] += 1
        self._save_metrics()

    def record_emotion(self, emotion):
        """Registra una emoción detectada"""
        self.metrics['emotion_distribution'][emotion] += 1
        self._save_metrics()

    def record_memory_operation(self, operation):
        """Registra una operación de memoria"""
        self.metrics['memory_operations'][operation] += 1
        self._save_metrics()

    def get_service_stats(self, service):
        """Obtiene estadísticas de un servicio"""
        stats = {
            'total_requests': self.metrics['total_requests'].get(service, 0),
            'total_tokens': self.metrics['api_usage'].get(service, 0),
            'error_rate': self.metrics['error_rates'].get(service, 0),
            'avg_response_time': 0
        }
        
        response_times = self.metrics['response_times'].get(service, [])
        if response_times:
            stats['avg_response_time'] = sum(response_times) / len(response_times)
        
        return stats

    def get_emotion_stats(self):
        """Obtiene estadísticas de distribución de emociones"""
        total = sum(self.metrics['emotion_distribution'].values())
        if total == 0:
            return {}
        
        return {
            emotion: (count / total) * 100
            for emotion, count in self.metrics['emotion_distribution'].items()
        }

    def get_memory_stats(self):
        """Obtiene estadísticas de operaciones de memoria"""
        return dict(self.metrics['memory_operations'])

    def reset_metrics(self):
        """Reinicia todas las métricas"""
        self.metrics = {
            'api_usage': defaultdict(int),
            'response_times': defaultdict(list),
            'error_rates': defaultdict(int),
            'total_requests': defaultdict(int),
            'emotion_distribution': defaultdict(int),
            'memory_operations': defaultdict(int),
            'last_updated': datetime.now().isoformat()
        }
        self._save_metrics() 