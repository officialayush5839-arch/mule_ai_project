from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from backend.observability.config.otel_config import SigNozConfig
import logging

logger = logging.getLogger(__name__)

class MetricsManager:
    @staticmethod
    def initialize_metrics():
        try:
            resource = Resource.create(attributes={
                SERVICE_NAME: SigNozConfig.get_service_name(),
                "environment": "production"
            })

            exporter = OTLPMetricExporter(
                endpoint=SigNozConfig.get_otlp_endpoint(),
                headers=SigNozConfig.get_headers(),
                timeout=2
            )

            # Export metrics every 15 seconds
            reader = PeriodicExportingMetricReader(exporter, export_interval_millis=15000)
            
            provider = MeterProvider(resource=resource, metric_readers=[reader])
            metrics.set_meter_provider(provider)

            logger.info("OpenTelemetry Metrics initialized successfully with SigNoz exporter.")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenTelemetry Metrics: {e}")

    @staticmethod
    def get_meter(name: str):
        return metrics.get_meter(name)

# Expose global meters for easy import
ai_meter = metrics.get_meter("mulenet.ai")
business_meter = metrics.get_meter("mulenet.business")
system_meter = metrics.get_meter("mulenet.system")

# Define global instruments
prediction_counter = ai_meter.create_counter(
    "ai.predictions.total",
    description="Total number of predictions made"
)

prediction_latency = ai_meter.create_histogram(
    "ai.inference.latency",
    description="Latency of model inference",
    unit="ms"
)

model_drift_gauge = ai_meter.create_gauge(
    "ai.model.drift_score",
    description="Calculated feature/model drift score"
)

gpu_utilization = system_meter.create_histogram(
    "system.gpu.utilization",
    description="GPU utilization during training/inference",
    unit="%"
)
