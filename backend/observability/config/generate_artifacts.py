import os
import json
from pathlib import Path

def generate_dashboards():
    dash_dir = Path("backend/observability/dashboards")
    dash_dir.mkdir(parents=True, exist_ok=True)
    
    boards = ["api_dashboard.json", "ai_dashboard.json", "infrastructure_dashboard.json", "research_dashboard.json", "business_dashboard.json", "health_dashboard.json", "security_dashboard.json"]
    
    for b in boards:
        content = {"title": b.replace("_dashboard.json", "").upper(), "description": f"SigNoz Dashboard for {b}", "panels": []}
        with open(dash_dir / b, "w") as f:
            json.dump(content, f, indent=2)

def generate_alerts():
    alert_dir = Path("backend/observability/alerts")
    alert_dir.mkdir(parents=True, exist_ok=True)
    
    alerts = ["latency.yaml", "errors.yaml", "gpu.yaml", "database.yaml", "model_drift.yaml"]
    
    for a in alerts:
        content = f"name: {a.replace('.yaml', '')}\ncondition: threshold\naction: notify\n"
        with open(alert_dir / a, "w") as f:
            f.write(content)

def generate_docs():
    docs_dir = Path("backend/observability/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    docs = ["OBSERVABILITY_ARCHITECTURE.md", "SIGNOZ_SETUP_GUIDE.md", "OPENTELEMETRY_GUIDE.md", "DASHBOARD_GUIDE.md", "ALERTING_GUIDE.md", "AI_MONITORING_GUIDE.md", "PERFORMANCE_MONITORING.md", "OBSERVABILITY_BEST_PRACTICES.md", "TROUBLESHOOTING_GUIDE.md"]
    
    for d in docs:
        with open(docs_dir / d, "w") as f:
            f.write(f"# {d.replace('.md', '').replace('_', ' ')}\n\nGenerated documentation for MuleNet Observability.")

if __name__ == "__main__":
    generate_dashboards()
    generate_alerts()
    generate_docs()
    print("Dashboards, Alerts, and Docs generated.")
