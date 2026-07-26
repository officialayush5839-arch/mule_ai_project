import os
from typing import Dict, Any

class SigNozConfig:
    @staticmethod
    def get_otlp_endpoint() -> str:
        """Returns the SigNoz OTLP gRPC endpoint, defaulting to local."""
        return os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    @staticmethod
    def get_service_name() -> str:
        """Returns the configured service name."""
        return os.getenv("SIGNOZ_SERVICE_NAME", "MuleNet-Enterprise")

    @staticmethod
    def get_api_key() -> str:
        """Returns the SigNoz API Key for cloud deployments."""
        return os.getenv("SIGNOZ_API_KEY", "")

    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Returns required headers, including API key if provided."""
        headers_env = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
        headers = {}
        if headers_env:
            for pair in headers_env.split(","):
                k, v = pair.split("=", 1)
                headers[k.strip()] = v.strip()
                
        api_key = SigNozConfig.get_api_key()
        if api_key:
            headers["signoz-access-token"] = api_key
            
        return headers
