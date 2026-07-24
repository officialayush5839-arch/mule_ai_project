"""
dataset_pipeline.py
===================
Hybrid dataset pipeline for MuleNet AI.
Upgraded to Research-Grade Financial Fraud Simulator.

Mode A – Synthetic: Generates a statistically realistic, seeded fraud dataset
         using GraphBuilder, PersonaEngine, and ScenarioEngine.
Mode B – Uploaded: Automatically handles uploaded datasets.
"""

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import networkx as nx
import community as community_louvain
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RANDOM_SEED = 42

# ─── Canonical Feature Schema (Expanded for Research Graph/Temporal) ────────────
FEATURE_SCHEMA: Dict[str, Dict[str, Any]] = {
    # Original
    "F115":  {"range": (0.0, 1.0), "desc": "Transaction volume / balance ratio"},
    "F321":  {"range": (0.0, 1.0), "desc": "Fund source concentration score"},
    "F527":  {"range": (0.0, 1.0), "desc": "Transaction velocity ratio"},
    "F670":  {"range": (0.0, 1.0), "desc": "Account age (normalized, 1 = oldest)"},
    "F1692": {"range": (0.0, 1.0), "desc": "Mule behaviour pattern score"},
    "F3043": {"range": (0.0, 1.0), "desc": "Outflow dominance ratio"},
    "F3894": {"range": (0.0, 1.0), "desc": "Anomaly isolation index"},
    # Graph Metrics
    "G_Degree": {"range": (0.0, 1.0), "desc": "Degree Centrality"},
    "G_Betweenness": {"range": (0.0, 1.0), "desc": "Betweenness Centrality"},
    "G_Closeness": {"range": (0.0, 1.0), "desc": "Closeness Centrality"},
    "G_Eigenvector": {"range": (0.0, 1.0), "desc": "Eigenvector Centrality"},
    "G_PageRank": {"range": (0.0, 1.0), "desc": "PageRank"},
    "G_Clustering": {"range": (0.0, 1.0), "desc": "Local Clustering"},
    "G_Community": {"range": (0, 100), "desc": "Louvain Community ID"},
    # Temporal Metrics
    "T_Velocity_30d": {"range": (0.0, 1000.0), "desc": "Transactions in 30d"},
    "T_Velocity_90d": {"range": (0.0, 3000.0), "desc": "Transactions in 90d"},
    "T_Hour": {"range": (0, 23), "desc": "Transaction Hour"},
    "T_Day": {"range": (1, 31), "desc": "Transaction Day"},
    "T_Week": {"range": (1, 52), "desc": "Transaction Week"},
    "T_Month": {"range": (1, 12), "desc": "Transaction Month"},
    "T_Quarter": {"range": (1, 4), "desc": "Transaction Quarter"},
    "T_Weekend": {"range": (0, 1), "desc": "Is Weekend"},
    "T_Business_Day": {"range": (0, 1), "desc": "Is Business Day"},
    "T_Holiday": {"range": (0, 1), "desc": "Is Holiday"},
    # Persona Attributes
    "P_Geo_Type": {"range": (0, 3), "desc": "Urban, Semi, Rural, Cross-border"},
    "P_Device_Type": {"range": (0, 5), "desc": "Single, Shared, Frequent, VPN, Emulator, Rooted"},
    "P_Banking_Type": {"range": (0, 5), "desc": "Salary, Current, Business, Dormant, HNW, Gov"},
    "P_Risk_State": {"range": (0, 4), "desc": "Normal, Suspicious, Watchlist, HighRisk, Mule"},
}
FEATURE_COLS: List[str] = list(FEATURE_SCHEMA.keys())
TARGET_COL = "label"

@dataclass
class DatasetMetadata:
    version: str
    source: str
    filename: str
    created_at: str
    n_samples: int
    n_features: int
    n_positive: int
    n_negative: int
    fraud_rate: float
    dataset_hash: str
    feature_columns: List[str]
    has_labels: bool
    train_samples: int
    val_samples: int
    test_samples: int
    generator_seed: Optional[int] = None
    quality_issues: List[str] = field(default_factory=list)
    notes: str = ""

_LATEST_GRAPH = None
_LATEST_NODES = None

# ─── Persona Engine ───────────────────────────────────────────────────────────
class PersonaEngine:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def generate(self, n_samples: int, labels: np.ndarray) -> pd.DataFrame:
        df = pd.DataFrame()
        df["P_Geo_Type"] = self.rng.choice([0, 1, 2, 3], p=[0.5, 0.3, 0.15, 0.05], size=n_samples)
        df["P_Device_Type"] = self.rng.choice([0, 1, 2, 3, 4, 5], p=[0.7, 0.1, 0.05, 0.05, 0.05, 0.05], size=n_samples)
        df["P_Banking_Type"] = self.rng.choice([0, 1, 2, 3, 4, 5], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05], size=n_samples)
        
        risk_states = np.zeros(n_samples, dtype=int)
        fraud_idx = np.where(labels == 1)[0]
        legit_idx = np.where(labels == 0)[0]
        
        risk_states[fraud_idx] = self.rng.choice([1, 2, 3, 4], p=[0.1, 0.2, 0.3, 0.4], size=len(fraud_idx))
        risk_states[legit_idx] = self.rng.choice([0, 1, 2, 3], p=[0.85, 0.10, 0.04, 0.01], size=len(legit_idx))
        df["P_Risk_State"] = risk_states
        
        return df

# ─── Scenario Engine ──────────────────────────────────────────────────────────
class ScenarioEngine:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng
        self.scenarios = [
            "student_mule", "dormant_reactivated", "shell_company", 
            "payroll_fraud", "crypto_cashout", "cross_border_abuse", 
            "atm_chain", "merchant_collusion", "circular_movement", "mule_network"
        ]
        self.node_scenarios = {}

    def apply_scenarios(self, G: nx.DiGraph, fraud_nodes: np.ndarray, legit_nodes: np.ndarray):
        np.random.shuffle(fraud_nodes)
        chunks = np.array_split(fraud_nodes, len(self.scenarios))
        
        for i, scenario in enumerate(self.scenarios):
            nodes = chunks[i]
            if len(nodes) < 2: continue
            
            for n in nodes:
                self.node_scenarios[n] = scenario
            
            if scenario == "circular_movement":
                for j in range(len(nodes)):
                    G.add_edge(nodes[j], nodes[(j+1)%len(nodes)], weight=self.rng.uniform(1000, 5000))
            elif scenario == "mule_network":
                sink = nodes[0]
                for src in nodes[1:]:
                    G.add_edge(src, sink, weight=self.rng.uniform(100, 500))
            elif scenario == "layering_chain":
                for j in range(len(nodes)-1):
                    G.add_edge(nodes[j], nodes[j+1], weight=self.rng.uniform(500, 2000))
            elif scenario == "shell_company":
                shell = nodes[0]
                for _ in range(10):
                    src = self.rng.choice(legit_nodes)
                    G.add_edge(src, shell, weight=self.rng.uniform(5000, 20000))
                for dst in nodes[1:3]:
                    G.add_edge(shell, dst, weight=self.rng.uniform(10000, 50000))
            elif scenario == "student_mule":
                for node in nodes:
                    srcs = self.rng.choice(list(G.nodes()), 3)
                    for src in srcs: G.add_edge(src, node, weight=self.rng.uniform(50, 200))
                    dst = self.rng.choice(fraud_nodes)
                    G.add_edge(node, dst, weight=self.rng.uniform(150, 600))
            else:
                for src in nodes:
                    dst = self.rng.choice(nodes)
                    if src != dst:
                        G.add_edge(src, dst, weight=self.rng.uniform(10, 1000))

# ─── Graph Builder ────────────────────────────────────────────────────────────
class GraphBuilder:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng
        self.G = nx.DiGraph()

    def build(self, n_samples: int, labels: np.ndarray, scenario_engine: ScenarioEngine):
        base_G = nx.barabasi_albert_graph(n_samples, m=3, seed=int(self.rng.integers(0, 10000)))
        self.G = nx.DiGraph(base_G)
        for u, v in self.G.edges():
            self.G[u][v]['weight'] = self.rng.uniform(10, 1000)
            
        fraud_nodes = np.where(labels == 1)[0]
        legit_nodes = np.where(labels == 0)[0]
        
        scenario_engine.apply_scenarios(self.G, fraud_nodes, legit_nodes)

    def extract_metrics(self) -> pd.DataFrame:
        if len(self.G) == 0: return pd.DataFrame()
        
        deg = nx.degree_centrality(self.G)
        bet = nx.betweenness_centrality(self.G, k=min(200, len(self.G)))
        clo = nx.closeness_centrality(self.G)
        pr = nx.pagerank(self.G, alpha=0.85)
        clust = nx.clustering(self.G)
        
        undirected_G = self.G.to_undirected()
        try:
            communities = community_louvain.best_partition(undirected_G)
        except:
            communities = {n: 0 for n in self.G.nodes()}
            
        try:
            eig = nx.eigenvector_centrality(self.G, max_iter=500, tol=1e-2)
        except:
            eig = {n: 0.0 for n in self.G.nodes()}
            
        df = pd.DataFrame({
            "G_Degree": [deg[i] for i in range(len(self.G))],
            "G_Betweenness": [bet[i] for i in range(len(self.G))],
            "G_Closeness": [clo[i] for i in range(len(self.G))],
            "G_Eigenvector": [eig[i] for i in range(len(self.G))],
            "G_PageRank": [pr[i] for i in range(len(self.G))],
            "G_Clustering": [clust[i] for i in range(len(self.G))],
            "G_Community": [communities[i] for i in range(len(self.G))],
        })
        return df

# ─── Financial Simulator ──────────────────────────────────────────────────────
class FinancialSimulator:
    def __init__(self, n_samples: int, fraud_rate: float, seed: int, temporal_days: int = 365):
        self.n_samples = n_samples
        self.fraud_rate = fraud_rate
        self.rng = np.random.default_rng(seed)
        self.temporal_days = temporal_days
        
        self.persona_engine = PersonaEngine(self.rng)
        self.scenario_engine = ScenarioEngine(self.rng)
        self.graph_builder = GraphBuilder(self.rng)
        
    def generate(self) -> pd.DataFrame:
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
        
        # Temporal Simulation
        base_date = datetime(2025, 1, 1)
        creation_dates = [base_date + timedelta(days=float(self.rng.uniform(0, 365))) for _ in range(self.n_samples)]
        tx_timestamps = [c + timedelta(days=float(self.rng.uniform(0, 30)), hours=float(self.rng.uniform(0, 24))) for c in creation_dates]
        
        t30 = np.where(fraud_mask, self.rng.poisson(120, self.n_samples), self.rng.poisson(30, self.n_samples))
        t90 = t30 * 3 + self.rng.poisson(15, self.n_samples)
        
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
                
        global _LATEST_GRAPH, _LATEST_NODES
        _LATEST_GRAPH = self.graph_builder.G
        _LATEST_NODES = df_final.copy()
        
        return df_final


# ─── API Methods ──────────────────────────────────────────────────────────────
def generate_synthetic_dataset(
    n_samples: int = 50_000,
    fraud_rate: float = 0.04,
    seed: int = RANDOM_SEED,
    temporal_days: int = 365,
) -> pd.DataFrame:
    logger.info(f"Research-Grade Simulator: {n_samples} samples, {fraud_rate*100}% fraud.")
    simulator = FinancialSimulator(n_samples=n_samples, fraud_rate=fraud_rate, seed=seed, temporal_days=temporal_days)
    return simulator.generate()

def compute_dataset_hash(df: pd.DataFrame) -> str:
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()

def load_uploaded_csv(path: str) -> pd.DataFrame:
    if not Path(path).exists() or Path(path).stat().st_size == 0: raise ValueError("Invalid CSV")
    return pd.read_csv(path)

def normalise_label_column(df: pd.DataFrame) -> pd.DataFrame:
    for alias in ("is_fraud", "fraud", "target", "is_mule", "mule"):
        if alias in df.columns and TARGET_COL not in df.columns:
            df = df.rename(columns={alias: TARGET_COL})
            break
    return df

def validate_schema(df: pd.DataFrame) -> Dict[str, Any]:
    errors = [f"Missing: {c}" for c in FEATURE_COLS if c not in df.columns]
    return {"valid": len(errors) == 0, "errors": errors, "warnings": []}

def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    return {"shape": {"rows": len(df), "cols": len(df.columns)}}

def clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = df.drop_duplicates().reset_index(drop=True)
    feat = [c for c in df.columns if c in FEATURE_COLS]
    if int(df[feat].isna().sum().sum()) > 0:
        df[feat] = df[feat].fillna(df[feat].median())
    return df, {"steps": []}

def split_dataset(df: pd.DataFrame, seed: int = RANDOM_SEED, oot: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    has_lbl = TARGET_COL in df.columns
    
    if oot and "Transaction_Timestamp" in df.columns:
        df = df.sort_values(by="Transaction_Timestamp").reset_index(drop=True)
        train_idx = int(len(df) * 0.70)
        val_idx = int(len(df) * 0.85)
        train_df = df.iloc[:train_idx].copy()
        val_df = df.iloc[train_idx:val_idx].copy()
        test_df = df.iloc[val_idx:].copy()
        return train_df, val_df, test_df
    
    stratify = df[TARGET_COL] if has_lbl else None
    train_df, temp_df = train_test_split(df, test_size=0.30, random_state=seed, stratify=stratify)
    
    strat_temp = temp_df[TARGET_COL] if has_lbl else None
    val_df, test_df = train_test_split(temp_df, test_size=0.50, random_state=seed, stratify=strat_temp)
    
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)

def save_splits(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame, version: str) -> Dict[str, Path]:
    vdir = DATA_DIR / version
    vdir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(vdir / "train.csv", index=False)
    val_df.to_csv(vdir / "val.csv", index=False)
    test_df.to_csv(vdir / "test.csv", index=False)
    
    global _LATEST_GRAPH, _LATEST_NODES
    if _LATEST_GRAPH is not None:
        nx.write_edgelist(_LATEST_GRAPH, vdir / "edges.csv", delimiter=",", data=["weight"])
        _LATEST_NODES.to_csv(vdir / "nodes.csv", index_label="node_id")
        _LATEST_GRAPH = None
        _LATEST_NODES = None
        
    return {"train": vdir / "train.csv"}

def load_splits(version: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    vdir = DATA_DIR / version
    return pd.read_csv(vdir / "train.csv"), pd.read_csv(vdir / "val.csv"), pd.read_csv(vdir / "test.csv")

def find_latest_version() -> Optional[str]:
    if not DATA_DIR.exists(): return None
    dirs = sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir() and (d / "train.csv").exists()], reverse=True)
    return dirs[0] if dirs else None

def run_dataset_pipeline(
    data_path: Optional[str] = None,
    n_samples: int = 50_000,
    fraud_rate: float = 0.04,
    seed: int = RANDOM_SEED,
    temporal_days: int = 365,
    oot_split: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, DatasetMetadata]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if data_path and Path(data_path).exists():
        df = normalise_label_column(load_uploaded_csv(data_path))
        src, fn = "uploaded", Path(data_path).name
    else:
        df = generate_synthetic_dataset(n_samples, fraud_rate, seed, temporal_days)
        src, fn = "synthetic", f"synthetic_{ts}.csv"

    has_lbl = TARGET_COL in df.columns
    if not validate_schema(df)["valid"]:
        avail = [c for c in FEATURE_COLS if c in df.columns]
        for c in FEATURE_COLS:
            if c not in df.columns: df[c] = df[avail[0]].median() if avail else 0.5

    df, _ = clean_dataset(df)
    train_df, val_df, test_df = split_dataset(df, seed, oot=oot_split)
    
    ver = f"{src}_{ts}"
    save_splits(train_df, val_df, test_df, ver)
    df.to_csv(DATA_DIR / ver / "full_dataset.csv", index=False)

    n_pos = int(df[TARGET_COL].sum()) if has_lbl else 0
    meta = DatasetMetadata(
        version=ver, source=src, filename=fn, created_at=datetime.now(timezone.utc).isoformat(),
        n_samples=len(df), n_features=len(FEATURE_COLS), n_positive=n_pos, n_negative=len(df)-n_pos,
        fraud_rate=round(n_pos/max(len(df),1), 4), dataset_hash=compute_dataset_hash(df),
        feature_columns=FEATURE_COLS, has_labels=has_lbl, train_samples=len(train_df),
        val_samples=len(val_df), test_samples=len(test_df), generator_seed=seed if src=="synthetic" else None
    )
    with open(DATA_DIR / ver / "metadata.json", "w") as fh:
        json.dump(asdict(meta), fh, indent=2)

    return train_df, val_df, test_df, meta
