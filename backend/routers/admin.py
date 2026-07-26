from fastapi import APIRouter, Depends, HTTPException, Request
from observability.monitoring.health_service import HealthService
from observability.monitoring.metrics_store import metrics_store
import os
import logging
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin Observability"])
logger = logging.getLogger(__name__)

# --- Dummy JWT/Auth Middleware Simulation ---
class MockUser:
    def __init__(self, uid: str, name: str, role: str):
        self.id = uid
        self.name = name
        self.role = role

def get_current_user(request: Request) -> MockUser:
    # In a real app, parse request.headers.get("Authorization") for JWT
    # Returning mock admin for Hackathon demo purposes
    return MockUser(uid="admin-001", name="Ayush S.", role="ADMIN")

def require_admin(user: MockUser = Depends(get_current_user)):
    allowed_roles = ["ADMIN", "SUPER_ADMIN", "OBSERVABILITY_ADMIN"]
    if user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient privileges")
    return user
# --------------------------------------------

@router.get("/system-health")
async def get_system_health(user: MockUser = Depends(require_admin)):
    return HealthService.get_system_health()

@router.get("/metrics")
async def get_metrics(user: MockUser = Depends(require_admin)):
    return metrics_store.get_metrics()

@router.get("/signoz-access")
async def get_signoz_access(request: Request, user: MockUser = Depends(require_admin)):
    """
    RBAC Protected API to fetch the SigNoz URL and connection status.
    Generates an explicit Audit event upon access.
    """
    # 1. Fetch connection status (using HealthService backend check)
    health = HealthService.get_system_health()
    backend_status = health["services"]["backend"]
    
    # 2. Log structured Audit Event
    audit_event = {
        "event": "SIGNOZ_ADMIN_ACCESS",
        "user": user.name,
        "role": user.role,
        "timestamp": datetime.utcnow().isoformat(),
        "ip": request.client.host if request.client else "unknown"
    }
    logger.info("Audit Event Generated", extra={"audit": audit_event})
    
    # 3. Retrieve SigNoz Endpoint
    signoz_url = os.getenv("SIGNOZ_ENDPOINT", "http://localhost:3301")
    
    return {
        "success": True,
        "has_access": True,
        "signoz": {
            "url": signoz_url,
            "status": "connected" if backend_status["status"] == "healthy" else "offline",
            "latency_ms": int(backend_status["latency"].replace("ms", "")) if backend_status["latency"] != "N/A" else 0
        }
    }
