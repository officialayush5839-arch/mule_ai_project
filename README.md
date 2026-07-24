<div align="center">
  <img src="public/favicon.svg" alt="MuleNet AI Logo" width="100" />
  <h1>MuleNet AI</h1>
  <p><b>Enterprise Financial Crime & Money Mule Intelligence Platform</b></p>
  
  [![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
  [![License](https://img.shields.io/badge/license-MIT-blue)](#)
  [![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![React](https://img.shields.io/badge/react-18.x-61DAFB.svg)](https://reactjs.org/)
</div>

<br />

MuleNet AI is a production-grade, enterprise-ready machine learning platform engineered to detect complex financial crime typologies, specifically focusing on money mule networks, layering chains, and circular cash movements. 

The platform utilizes a sophisticated ensemble of LightGBM and XGBoost, augmented with Graph Node Centrality features (PageRank, Eigenvector), Behavioral Velocity profiling, and full SHAP-driven Explainable AI.

## 🚀 Key Features

*   **Graph Intelligence**: Computes robust graph metrics (PageRank, Louvain Communities, Betweenness Centrality) to identify bridge nodes and centralized cash-out hubs in directed transaction networks.
*   **Temporal Velocity Profiling**: Tracks dynamic transaction velocities over 30-day and 90-day windows, identifying abnormal bursts of activity indicative of "burner" accounts or dormant reactivations.
*   **Explainable AI (XAI)**: Full SHAP (SHapley Additive exPlanations) integration. Every prediction includes a waterfall chart explaining exactly which features drove the model's confidence.
*   **Research-Grade Synthetic Engine**: Includes a deterministic, heavily-engineered synthetic data generator capable of simulating realistic overlapping fraud typologies (e.g., student mules, crypto cashouts, invoice fraud rings).
*   **Enterprise Architecture**: A high-performance FastAPI asynchronous backend coupled with a sleek, responsive React + Vite frontend dashboard.

## 🧠 Machine Learning Architecture

The current baseline is a scientifically validated Classical ML framework:
*   **Algorithms**: LightGBM, XGBoost, CatBoost, Random Forest Ensembles.
*   **Validation**: Validated via rigorous Leave-One-Typology-Out (LOTO) cross-validation and Cross-Seed temporal out-of-time splits.
*   **Performance**: Extremely robust to distribution shifts and up to 30% missing data, achieving state-of-the-art PR-AUC by dynamically pivoting between Graph and Base behavioral features.

*(Phase 1 Deep Learning Integration involving PyTorch, GraphSAGE, and TabNet is currently in active development).*

## 💻 Tech Stack

### Frontend
*   **React 18** (Vite build system)
*   **Vanilla CSS** (Custom, highly optimized CSS styling with glassmorphism)
*   **Lucide React** (Iconography)
*   **Recharts** (Data Visualization)

### Backend
*   **FastAPI** (High-performance async Python web framework)
*   **Uvicorn** (ASGI Web Server)
*   **Pandas / NumPy / Scikit-Learn** (Data processing)
*   **LightGBM / XGBoost** (Gradient Boosting Decision Trees)
*   **NetworkX** (Graph algorithms)
*   **SHAP** (Model Explainability)

## 🛠️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/officialayush5839-arch/mule_ai_project.git
    cd mule_ai_project
    ```

2.  **Install Frontend Dependencies:**
    ```bash
    npm install
    ```

3.  **Install Backend Dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    cd backend
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

4.  **Run the application (Development Mode):**
    You can start both the frontend and backend simultaneously using the provided script (Windows):
    ```cmd
    run.bat
    ```
    Alternatively, run them separately:
    *   **Frontend:** `npm run dev`
    *   **Backend:** `cd backend && python -m uvicorn main:app --reload --port 8000`

## 📊 Evaluation & Scientific Audit

MuleNet AI has undergone rigorous scientific validation (Phase 0 Audit):
*   **Feature Removal Challenge**: Proved the model doesn't over-rely on trivial features.
*   **Ensemble Stability Analysis**: Confirmed high Cohen's Kappa agreement across different model architectures.
*   **Unknown Fraud Generalization**: Successfully detected synthetic typologies (e.g., Crypto Cashouts) that were strictly excluded from the training set.

Detailed reports are generated internally during training runs using the `ml/research/run_advanced_generalization_audit.py` orchestrator.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
<div align="center">
  <i>Engineered for Enterprise Financial Crime Intelligence.</i>
</div>
