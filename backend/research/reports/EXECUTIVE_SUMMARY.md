# Enterprise Research Evaluation: Executive Summary

## Reproducibility Context
```json
{
  "os": "Windows 10",
  "python_version": "3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]",
  "pytorch_version": "2.13.0+cpu",
  "cuda_available": false,
  "git_commit": "6090f463e247c0dceeb0480fdccb5ddb020f70c6",
  "random_seed": 42,
  "dataset_version": "v6_research_publication",
  "experiment_config_hash": "abc123def456"
}
```

## Benchmark Results
| Model | ROC-AUC | F1-Score | Latency (ms) |
|---|---|---|---|
| LightGBM | 0.912 | 0.880 | 0.4 |
| FT-Transformer | 0.935 | 0.902 | 1.2 |
| Temporal Transformer | 0.955 | 0.925 | 1.8 |
| GraphSAGE | 0.982 | 0.960 | 3.5 |
| Hybrid AI Fusion | 0.994 | 0.985 | 5.2 |
