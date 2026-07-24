import pandas as pd
import numpy as np
import networkx as nx
from datetime import datetime, timedelta
from ml.dataset_pipeline import FinancialSimulator, FEATURE_COLS, TARGET_COL

class ResearchOverlapSimulator(FinancialSimulator):
    """
    A temporary override of the FinancialSimulator exclusively for research validation.
    It forces heavily overlapping distributions for Temporal features (Velocity) 
    so they are not trivially separable (which previously yielded PR-AUC=1.000).
    It also injects Unknown Fraud Typologies for Phase 2 validation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def generate(self) -> pd.DataFrame:
        # Override to inject heavily overlapping temporal velocities 
        n_fraud = max(1, int(self.n_samples * self.fraud_rate))
        n_legit = self.n_samples - n_fraud
        labels = np.array([1]*n_fraud + [0]*n_legit)
        self.rng.shuffle(labels)
        fraud_mask = (labels == 1)

        df_base = pd.DataFrame()
        def gen_feature(legit_mean, fraud_mean, legit_std, fraud_std):
            v = np.where(fraud_mask, 
                         self.rng.normal(fraud_mean, fraud_std, self.n_samples),
                         self.rng.normal(legit_mean, legit_std, self.n_samples))
            return np.clip(v, 0.0, 1.0)

        df_base["F115"] = gen_feature(0.3, 0.6, 0.2, 0.3)
        df_base["F321"] = gen_feature(0.4, 0.7, 0.25, 0.2)
        df_base["F527"] = gen_feature(0.2, 0.8, 0.2, 0.2)
        df_base["F670"] = gen_feature(0.8, 0.3, 0.3, 0.2)
        df_base["F1692"] = gen_feature(0.1, 0.7, 0.2, 0.25)
        df_base["F3043"] = gen_feature(0.4, 0.7, 0.2, 0.2)
        df_base["F3894"] = gen_feature(0.2, 0.8, 0.2, 0.2)
        
        df_personas = self.persona_engine.generate(self.n_samples, labels)
        
        # RESEARCH OVERLAP FIX: Force almost identical temporal distributions
        # Legit mean=50, Fraud mean=55 (instead of 30 vs 120)
        t30 = np.where(fraud_mask, self.rng.poisson(55, self.n_samples), self.rng.poisson(50, self.n_samples))
        t90 = t30 * 3 + self.rng.poisson(20, self.n_samples)
        
        base_date = datetime(2025, 1, 1)
        creation_dates = [base_date + timedelta(days=float(self.rng.uniform(0, 365))) for _ in range(self.n_samples)]
        tx_timestamps = [c + timedelta(days=float(self.rng.uniform(0, 30)), hours=float(self.rng.uniform(0, 24))) for c in creation_dates]
        
        df_temporal = pd.DataFrame({
            "T_Velocity_30d": np.clip(t30, 0, 1000),
            "T_Velocity_90d": np.clip(t90, 0, 3000),
            "T_Hour": [dt.hour for dt in tx_timestamps],
            "T_Day": [dt.day for dt in tx_timestamps],
            "T_Week": [dt.isocalendar()[1] for dt in tx_timestamps],
            "T_Month": [dt.month for dt in tx_timestamps],
            "T_Quarter": [(dt.month - 1) // 3 + 1 for dt in tx_timestamps],
            "T_Weekend": [1 if dt.weekday() >= 5 else 0 for dt in tx_timestamps],
            "T_Business_Day": [1 if dt.weekday() < 5 else 0 for dt in tx_timestamps],
            "T_Holiday": self.rng.choice([0, 1], p=[0.97, 0.03], size=self.n_samples)
        })

        # Inject unseen typologies into scenario engine
        self.scenario_engine.scenarios.extend(["crypto_cashout_network", "invoice_fraud_ring"])
        
        self.graph_builder.build(self.n_samples, labels, self.scenario_engine)
        df_graph = self.graph_builder.extract_metrics()
        
        df_final = pd.concat([df_base, df_graph, df_temporal, df_personas], axis=1)
        df_final[TARGET_COL] = labels
        
        df_final["Ground_Truth_Scenario"] = [self.scenario_engine.node_scenarios.get(i, "legit") for i in range(self.n_samples)]
        df_final["Account_Creation_Date"] = [dt.isoformat() for dt in creation_dates]
        df_final["Transaction_Timestamp"] = [dt.isoformat() for dt in tx_timestamps]
        
        for c in ["G_Degree", "G_Betweenness", "G_Closeness", "G_Eigenvector", "G_PageRank", "G_Clustering"]:
            if c in df_final.columns:
                mx = df_final[c].max()
                df_final[c] = df_final[c] / mx if mx > 0 else 0.0
                
        return df_final
