from fastapi import APIRouter
from pydantic import BaseModel
import re

router = APIRouter()

class CopilotChatInput(BaseModel):
    message: str

MOCK_COPILOT_RESPONSES = {
    "acc-847291": """Account **ACC-847291** has been classified as a **CRITICAL** mule account with **97.3% confidence**. Here's the breakdown:

**PRIMARY EVIDENCE:**
• **Transaction Velocity (F527):** 4.2× above branch average — the account received ₹8.4L across 23 transactions in 48 hours, then transferred 94% outward within 6 hours. Classic pass-through behavior.

• **Behavioral Pattern Match (F1692):** 87% similarity to confirmed mule accounts in training data. The inflow-then-rapid-outflow signature matches FATF typology for third-party mule accounts.

• **Anomaly Score:** 0.94/1.00 (Isolation Forest) — places this account in the top 0.8% of all accounts by behavioral deviation.

**RISK FACTORS SUMMARY:**
| Feature | SHAP Value | Impact |
|---------|-----------|--------|
| F527 | +0.42 | Velocity spike |
| F1692 | +0.31 | Mule pattern match |
| F3043 | +0.24 | Rapid outflow |
| F3894 | +0.19 | Anomaly confirmed |

**RECOMMENDATION:** FREEZE ACCOUNT immediately and escalate to the Financial Intelligence Unit. Document under PMLA Section 12 and file an STR with FIU-IND within 7 working days.

*Confidence: 97.3% | Model: Stacking Ensemble*""",

    "report": """# MULENET AI INVESTIGATION REPORT
---
**Account:** ACC-847291 | **Analyst:** Ayush S.
**Risk Score:** 94/100 | **Classification:** CRITICAL | **Confidence:** 97.3%

## EXECUTIVE SUMMARY
Account ACC-847291 exhibits strong indicators of mule account behavior with a risk score of 94/100. The account shows classic pass-through patterns with high-velocity fund movement and rapid outflow, matching confirmed mule account templates with 87% similarity.

## RISK ASSESSMENT
- ⚠️ Risk score in CRITICAL zone (>80) for 12 consecutive days
- ⚠️ Transaction velocity 4.2× above branch average
- ⚠️ Outflow-to-inflow ratio of 0.94 (near-complete pass-through)
- ⚠️ Connected to 3 other flagged accounts in fraud network

## BEHAVIORAL ANALYSIS
- 23 transactions received in 48-hour window
- 94% of funds transferred outward within 6 hours
- Multiple recipients across different banks
- Transaction timing suggests automated behavior

## SHAP EVIDENCE
1. **F527 (+0.42):** Unusually high transaction velocity
2. **F1692 (+0.31):** Matches historical mule behavior
3. **F3043 (+0.24):** Rapid fund outflow pattern
4. **F3894 (+0.19):** Strong anomaly detection signal
5. **F321 (+0.17):** Concentrated fund sources

## RECOMMENDED ACTION
**FREEZE ACCOUNT** and escalate to FIU-IND. File STR under PMLA Section 12.

**CONFIDENCE LEVEL: 97.3%**""",

    "summary": """## Today's Alert Summary

📊 **Active Alerts: 342**

### By Priority:
| Priority | Count | Change |
|----------|-------|--------|
| 🔴 Critical | 47 | +5 today |
| 🟠 High | 128 | +12 today |
| 🟡 Medium | 101 | +3 today |
| 🟢 Low | 66 | -2 today |

### Top Critical Alerts:
1. **ALT-2847** — ACC-847291 — Risk 94 — Velocity spike + mule pattern
2. **ALT-2846** — ACC-481927 — Risk 92 — ₹15.2L moved in 4 hours
3. **ALT-2845** — ACC-619283 — Risk 91 — Multiple converging signals

**Recommendation:** Focus on Cluster 4 growth and velocity-based alerts. Consider batch investigation for the 17 newly flagged accounts."""
}

@router.post("/copilot/chat")
def get_copilot_response(payload: CopilotChatInput):
    """
    Simulates / proxies chat instructions specifically matching key audit phrases.
    """
    msg = payload.message.lower().strip()
    
    if "847291" in msg:
        res = MOCK_COPILOT_RESPONSES["acc-847291"]
    elif "report" in msg:
        res = MOCK_COPILOT_RESPONSES["report"]
    elif "alert" in msg or "summary" in msg:
        res = MOCK_COPILOT_RESPONSES["summary"]
    else:
        res = """I've analyzed the available platform telemetry. Here's what I recommend:

Based on the active risk landscape, there are **342 active alerts** across the monitored banking registry. 

**Observations:**
- 47 critical accounts require immediate freeze directives.
- Cluster 4 (known velocity pass-through pattern) is expanding.
- Average risk score has increased by 2.1 points.

Would you like me to deep dive into a specific account (e.g. `ACC-847291`), generate a report, or summarize the active alert list?"""
        
    return {
        "reply": res
    }
