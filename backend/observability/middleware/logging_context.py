import logging
import json
from opentelemetry import trace

class OpenTelemetryLogFilter(logging.Filter):
    """
    Injects OpenTelemetry trace_id and span_id into log records for structured JSON logging.
    """
    def filter(self, record):
        span = trace.get_current_span()
        if span.is_recording():
            ctx = span.get_span_context()
            record.trace_id = format(ctx.trace_id, '032x')
            record.span_id = format(ctx.span_id, '016x')
        else:
            record.trace_id = None
            record.span_id = None
        return True

class JSONFormatter(logging.Formatter):
    """
    Formats standard logs as JSON objects for SigNoz ingestion.
    """
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "trace_id": getattr(record, "trace_id", None),
            "span_id": getattr(record, "span_id", None)
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_structured_logging():
    logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    handler.addFilter(OpenTelemetryLogFilter())
    
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
