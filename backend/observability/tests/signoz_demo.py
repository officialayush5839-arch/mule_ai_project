import logging
import time
from backend.observability.telemetry.tracing import ObservabilityManager
from backend.observability.telemetry.metrics import MetricsManager
from backend.observability.middleware.logging_context import setup_structured_logging
from backend.observability.monitoring.security_metrics import SecurityMonitor
from opentelemetry import trace

logger = logging.getLogger(__name__)

def simulate_hackathon_demo():
    print("Starting SigNoz Observability Demo...")
    setup_structured_logging()
    ObservabilityManager.initialize_telemetry()
    MetricsManager.initialize_metrics()

    tracer = trace.get_tracer(__name__)

    # Simulate an incoming API request
    with tracer.start_as_current_span("POST /api/v1/predict") as root_span:
        root_span.set_attribute("http.method", "POST")
        root_span.set_attribute("http.url", "/api/v1/predict")
        
        logger.info("Received prediction request from client.")
        
        # Simulate Authentication
        with tracer.start_as_current_span("authentication") as auth_span:
            time.sleep(0.05)
            SecurityMonitor.log_auth_failure("unknown_user@mule.ai")
            logger.info("Authentication processed.")

        # Simulate Security Rules Engine
        with tracer.start_as_current_span("security_engine") as sec_span:
            time.sleep(0.02)
            SecurityMonitor.log_blocked_request("Invalid API Key signature", "192.168.1.5")
            SecurityMonitor.log_suspicious_activity("Multiple Failed Logins", "acc_12345")

        # Simulate Model Inference
        with tracer.start_as_current_span("hybrid_ai_inference") as ai_span:
            time.sleep(0.1)
            SecurityMonitor.log_high_risk_prediction("Hybrid-Ensemble-v1", 0.98)
            logger.warning("High risk transaction detected during inference.")
            
    print("Demo traces, metrics, and logs have been sent to SigNoz.")
    
if __name__ == "__main__":
    simulate_hackathon_demo()
