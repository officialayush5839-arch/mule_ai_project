import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from observability.custom_telemetry import telemetry_store

class CustomTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add to request state for other modules to access if needed
        request.state.trace_id = request_id
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            trace_data = {
                "trace_id": request_id,
                "timestamp": time.time(),
                "method": request.method,
                "endpoint": request.url.path,
                "duration_ms": int(process_time * 1000),
                "status_code": response.status_code,
                "ip": request.client.host if request.client else "unknown",
                "error": None
            }
            telemetry_store.add_trace(trace_data)
            
            # Inject trace ID into response header
            response.headers["X-Trace-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            trace_data = {
                "trace_id": request_id,
                "timestamp": time.time(),
                "method": request.method,
                "endpoint": request.url.path,
                "duration_ms": int(process_time * 1000),
                "status_code": 500,
                "ip": request.client.host if request.client else "unknown",
                "error": str(e)
            }
            telemetry_store.add_trace(trace_data)
            raise e
