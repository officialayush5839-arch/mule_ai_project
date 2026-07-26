import time
import os
from typing import Dict, Any

class MetricsStore:
    """
    In-memory singleton store for admin dashboard metrics.
    Works alongside OpenTelemetry to provide immediate API responses.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsStore, cls).__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        # Demo initialization if OBSERVABILITY_DEMO_MODE is true
        is_demo = os.getenv("OBSERVABILITY_DEMO_MODE", "false").lower() == "true"
        
        self.api_requests = 125400 if is_demo else 0
        self.api_errors = 25 if is_demo else 0
        self.api_total_latency = 10784400 if is_demo else 0 # Avg ~86ms
        
        self.ai_predictions = 98500 if is_demo else 0
        self.ai_errors = 197 if is_demo else 0
        self.ai_total_inference_time = 9062000 if is_demo else 0 # Avg ~92ms
        
        self.security_suspicious = 340 if is_demo else 0
        self.security_high_risk = 55 if is_demo else 0
        self.security_blocked = 20 if is_demo else 0

    def increment_api_request(self, latency_ms: float, error: bool = False):
        self.api_requests += 1
        self.api_total_latency += latency_ms
        if error:
            self.api_errors += 1

    def increment_ai_prediction(self, latency_ms: float, error: bool = False):
        self.ai_predictions += 1
        self.ai_total_inference_time += latency_ms
        if error:
            self.ai_errors += 1

    def increment_security_event(self, event_type: str):
        if event_type == "suspicious":
            self.security_suspicious += 1
        elif event_type == "high_risk":
            self.security_high_risk += 1
        elif event_type == "blocked":
            self.security_blocked += 1

    def get_metrics(self) -> Dict[str, Any]:
        api_avg_latency = (self.api_total_latency / self.api_requests) if self.api_requests > 0 else 0
        api_error_rate = (self.api_errors / self.api_requests * 100) if self.api_requests > 0 else 0
        
        ai_avg_latency = (self.ai_total_inference_time / self.ai_predictions) if self.ai_predictions > 0 else 0
        ai_success_rate = ((self.ai_predictions - self.ai_errors) / self.ai_predictions * 100) if self.ai_predictions > 0 else 100

        return {
            "api": {
                "requests": self.api_requests,
                "latency": round(api_avg_latency),
                "errors": round(api_error_rate, 2)
            },
            "ai": {
                "predictions": self.ai_predictions,
                "inference_time": round(ai_avg_latency),
                "success_rate": round(ai_success_rate, 1)
            },
            "security": {
                "suspicious": self.security_suspicious,
                "high_risk": self.security_high_risk,
                "blocked": self.security_blocked
            },
            "infrastructure": {
                "cpu_usage": 42, # Mocked for hardware constraint reasons
                "memory_usage": 61,
                "database_connections": 24
            }
        }

metrics_store = MetricsStore()
