import time
import functools
from opentelemetry import trace
from backend.observability.telemetry.metrics import prediction_counter, prediction_latency, model_drift_gauge

tracer = trace.get_tracer(__name__)

def instrument_model_inference(model_name: str, family: str):
    """
    Decorator to automatically trace and collect metrics for any AI model inference call.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Start OTel Span
            with tracer.start_as_current_span(f"inference_{model_name}") as span:
                span.set_attribute("model.name", model_name)
                span.set_attribute("model.family", family)
                
                start_time = time.time()
                try:
                    # Execute Inference
                    result = func(*args, **kwargs)
                    
                    # Log metrics
                    latency_ms = (time.time() - start_time) * 1000
                    prediction_counter.add(1, {"model": model_name, "status": "success"})
                    prediction_latency.record(latency_ms, {"model": model_name})
                    
                    # Optional: capture confidence/probability if available
                    if isinstance(result, dict) and "probability" in result:
                        span.set_attribute("prediction.probability", float(result["probability"]))
                    
                    return result
                except Exception as e:
                    prediction_counter.add(1, {"model": model_name, "status": "error"})
                    span.record_exception(e)
                    span.set_status(trace.StatusCode.ERROR)
                    raise e
        return wrapper
    return decorator

class ExplainabilityMonitor:
    @staticmethod
    def track_contribution(model_contributions: dict):
        with tracer.start_as_current_span("explainability_contribution_analysis") as span:
            for family, score in model_contributions.items():
                span.set_attribute(f"contribution.{family}", score)

class DriftMonitor:
    @staticmethod
    def report_drift(score: float, feature_name: str = "global"):
        model_drift_gauge.set(score, {"feature": feature_name})
