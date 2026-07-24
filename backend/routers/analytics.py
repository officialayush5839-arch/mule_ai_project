from fastapi import APIRouter, HTTPException
from typing import List, Optional
import random

router = APIRouter()

# Mock Accounts Registry matching frontend mock list
MOCK_ACCOUNTS = [
    { "id": 'ACC-847291', "name": 'Rajesh Kumar Sharma', "type": 'Savings', "branch": 'Mumbai - Andheri West', "opened": '2024-01-14', "status": 'Active', "riskScore": 94, "classification": 'CRITICAL', "confidence": 97.3, "trustScore": 23 },
    { "id": 'ACC-291847', "name": 'Priya Nair', "type": 'Current', "branch": 'Chennai - T Nagar', "opened": '2023-11-08', "status": 'Active', "riskScore": 81, "classification": 'SUSPICIOUS', "confidence": 89.1, "trustScore": 34 },
    { "id": 'ACC-738291', "name": 'Amit Patel', "type": 'Savings', "branch": 'Delhi - Connaught Place', "opened": '2024-03-22', "status": 'Active', "riskScore": 87, "classification": 'CRITICAL', "confidence": 93.7, "trustScore": 19 },
    { "id": 'ACC-482916', "name": 'Sunita Devi', "type": 'Savings', "branch": 'Kolkata - Salt Lake', "opened": '2023-09-15', "status": 'Active', "riskScore": 76, "classification": 'SUSPICIOUS', "confidence": 85.4, "trustScore": 38 },
    { "id": 'ACC-619283', "name": 'Mohammed Irfan', "type": 'Current', "branch": 'Hyderabad - Banjara Hills', "opened": '2024-02-01', "status": 'Active', "riskScore": 91, "classification": 'CRITICAL', "confidence": 95.8, "trustScore": 15 },
]

@router.get("/dashboard/stats")
def get_dashboard_stats():
    """
    Returns unified metrics ribbon telemetry data.
    """
    return [
        { "id": 'total-accounts', "label": 'Total Accounts', "value": 247831, "trend": '+3.2%', "trendDir": 'up', "icon": 'Users' },
        { "id": 'monitoring', "label": 'Under Monitoring', "value": 18429, "trend": '+8.1%', "trendDir": 'up', "icon": 'Eye' },
        { "id": 'suspicious', "label": 'Suspicious Accounts', "value": 4219, "trend": '+12.4%', "trendDir": 'up', "icon": 'AlertTriangle', "color": 'warning' },
        { "id": 'critical', "label": 'Critical Accounts', "value": 1847, "trend": '+6.7%', "trendDir": 'up', "icon": 'ShieldAlert', "color": 'critical' },
    ]

@router.get("/accounts/high-risk")
def get_high_risk_accounts(limit: int = 5):
    """
    Returns top high-risk accounts sorted by risk score index.
    """
    sorted_acc = sorted(MOCK_ACCOUNTS, key=lambda x: x['riskScore'], reverse=True)
    return sorted_acc[:limit]

@router.get("/accounts/{account_id}")
def get_account_profile(account_id: str):
    """
    Locates detailed profile metadata of target account node.
    """
    acc = next((a for a in MOCK_ACCOUNTS if a['id'] == account_id), None)
    if not acc:
        raise HTTPException(status_code=404, detail=f"Account ID {account_id} not found in telemetry registry.")
    return acc

@router.get("/accounts/{account_id}/history")
def get_account_risk_history(account_id: str):
    """
    Generates 30-day historical risk scores for target account node.
    """
    acc = next((a for a in MOCK_ACCOUNTS if a['id'] == account_id), None)
    score = acc['riskScore'] if acc else 50
    
    history = []
    for day in range(1, 31):
        # Generate upward or steady historical trend ending in the current score
        val = int(score * 0.4 + (score * 0.6 * (day / 30.0)) + random.randint(-4, 4))
        history.append({
            "day": day,
            "date": f"Day {day}",
            "score": min(max(val, 0), 100)
        })
    return history
