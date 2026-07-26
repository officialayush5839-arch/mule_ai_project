import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from backend.observability.config.otel_config import SigNozConfig
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

logger = logging.getLogger(__name__)

class ObservabilityManager:
    @staticmethod
    def initialize_telemetry(app=None):
        """
        Initializes OpenTelemetry Tracing with SigNoz exporter.
        Uses BatchSpanProcessor for asynchronous, non-blocking telemetry.
        """
        try:
            resource = Resource.create(attributes={
                SERVICE_NAME: SigNozConfig.get_service_name(),
                "environment": "production"
            })
            
            provider = TracerProvider(resource=resource)
            
            # Use gRPC Exporter
            otlp_exporter = OTLPSpanExporter(
                endpoint=SigNozConfig.get_otlp_endpoint(),
                headers=SigNozConfig.get_headers(),
                timeout=2 # 2-second timeout to prevent stalling
            )
            
            # BatchSpanProcessor ensures graceful degradation:
            # If SigNoz is down, it drops spans instead of crashing production.
            processor = BatchSpanProcessor(
                otlp_exporter,
                max_queue_size=2048,
                schedule_delay_millis=5000 # Send batches every 5 seconds
            )
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            
            # Instrument Logging to inject trace_id/span_id
            LoggingInstrumentor().instrument()
            
            if app:
                # Instrument FastAPI
                FastAPIInstrumentor.instrument_app(app)
                
            logger.info("OpenTelemetry initialized successfully with SigNoz exporter.")
        except Exception as e:
            # Graceful degradation: log warning, increment failure metric, do NOT crash
            logger.warning(f"Failed to initialize OpenTelemetry: {e}. Falling back to un-instrumented execution.")
            # In a real setup, we would increment a Prometheus/OTel metric here.
            # e.g., metrics.increment("telemetry_export_failures_total")
