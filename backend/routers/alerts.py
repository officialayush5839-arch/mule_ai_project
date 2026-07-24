from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AlertActionPayload(BaseModel):
    action: str  # monitor, freeze, dismiss

# Mock database
MOCK_ALERTS = [
    { "id": 'ALT-2847', "accountId": 'ACC-847291', "priority": 'CRITICAL', "timestamp": '2026-06-12T12:00:00Z', "riskScore": 94, "confidence": 97.3, "trigger": 'Risk threshold breach (>80) combined with velocity spike', "status": 'active' },
    { "id": 'ALT-2846', "accountId": 'ACC-481927', "priority": 'CRITICAL', "timestamp": '2026-06-12T11:45:00Z', "riskScore": 92, "confidence": 96.4, "trigger": 'Velocity spike detected — ₹15.2L moved in 4 hours', "status": 'active' },
]

@router.get("/alerts")
def get_alerts():
    """
    Returns lists of active anomalies and flagged accounts.
    """
    return MOCK_ALERTS

@router.post("/alerts/{alert_id}/action")
def take_alert_action(alert_id: str, payload: AlertActionPayload):
    """
    Triggers administrative decisions (Monitor, Freeze, Dismiss) on active flags.
    """
    alert = next((a for a in MOCK_ALERTS if a['id'] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert code not found.")
        
    alert['status'] = 'processed'
    alert['actionTaken'] = payload.action
    
    return {
        "success": True,
        "alertId": alert_id,
        "action": payload.action,
        "message": f"Alert successfully updated. Action '{payload.action}' executed."
    }
