import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { LineChart, BarChart, RefreshCw, Cpu, ShieldCheck, Heart, AlertTriangle, Layers } from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';

export default function ModelIntel() {
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);

  // States
  const [metrics, setMetrics] = useState({});
  const [matrix, setMatrix] = useState({});
  const [roc, setRoc] = useState([]);
  const [baseModels, setBaseModels] = useState([]);
  const [health, setHealth] = useState({});

  const loadData = async () => {
    setLoading(true);
    try {
      const [metricsRes, matrixRes, rocRes, baseRes, healthRes] = await Promise.all([
        api.getModelMetrics(),
        api.getConfusionMatrix(),
        api.getROCCurve(),
        api.getBaseModels(),
        api.getModelHealth()
      ]);
      setMetrics(metricsRes);
      setMatrix(matrixRes);
      setRoc(rocRes);
      setBaseModels(baseRes);
      setHealth(healthRes);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRetrain = () => {
    setRetraining(true);
    setTimeout(() => {
      setRetraining(false);
      // Simulate minor improvement in health and metrics
      setMetrics(prev => ({
        ...prev,
        accuracy: { ...prev.accuracy, value: 96.6 },
        f1Score: { ...prev.f1Score, value: 94.2 }
      }));
      setHealth(prev => ({
        ...prev,
        lastRetrain: 'Just now'
      }));
    }, 1500);
  };

  // ECharts Option: ROC Curve
  const getRocOption = () => {
    if (!roc || roc.length === 0) return {};
    
    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 },
        formatter: (params) => {
          const pt = params[0].data;
          return `FPR: ${pt[0].toFixed(3)}<br/>TPR: ${pt[1].toFixed(3)}`;
        }
      },
      legend: {
        data: ['Stacking Ensemble (AUC = 0.987)', 'Random Guess'],
        bottom: 0,
        textStyle: { color: '#64748b', fontWeight: 600 }
      },
      grid: { left: '3%', right: '3%', top: '5%', bottom: '12%', containLabel: true },
      xAxis: {
        type: 'value',
        name: 'False Positive Rate',
        min: 0,
        max: 1,
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        splitLine: { lineStyle: { type: 'dashed', color: '#cbd5e1' } }
      },
      yAxis: {
        type: 'value',
        name: 'True Positive Rate',
        min: 0,
        max: 1,
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        splitLine: { lineStyle: { type: 'dashed', color: '#cbd5e1' } }
      },
      series: [
        {
          name: 'Stacking Ensemble (AUC = 0.987)',
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3 },
          color: '#3b82f6',
          data: roc.map(r => [r.fpr, r.tpr])
        },
        {
          name: 'Random Guess',
          type: 'line',
          showSymbol: false,
          lineStyle: { width: 1.5, type: 'dashed' },
          color: '#94a3b8',
          data: [[0, 0], [1, 1]]
        }
      ]
    };
  };

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">Model Performance & Auditing</h1>
          <p className="page-subtitle">Historical evaluation reports, confusion matrices, and model retraining controls.</p>
        </div>

        <button 
          className="btn btn-secondary btn-sm"
          disabled={retraining}
          onClick={handleRetrain}
        >
          <RefreshCw size={14} className={retraining ? 'animate-spin' : ''} />
          <span>{retraining ? 'Retraining Models...' : 'Trigger Model Retrain'}</span>
        </button>
      </div>

      {loading ? (
        <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '70vh' }}>
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
          <span className="text-label" style={{ marginTop: '16px' }}>Decrypting evaluation scores...</span>
        </div>
      ) : (
        <div className="flex flex-col gap-24 w-full">
          {/* Top Row: Neural Metrics Ribbon */}
          <div className="grid-3 w-full">
            {/* Accuracy */}
            <div className="card flex flex-col justify-between" style={{ padding: '16px 20px' }}>
              <span className="text-label" style={{ fontSize: '9px' }}>Accuracy</span>
              <div className="flex justify-between items-end w-full" style={{ marginTop: '10px' }}>
                <span className="font-mono text-metric">{metrics.accuracy?.value}%</span>
                <span className="trend-badge trend-up">{metrics.accuracy?.trend}</span>
              </div>
            </div>

            {/* F1 Score */}
            <div className="card flex flex-col justify-between" style={{ padding: '16px 20px' }}>
              <span className="text-label" style={{ fontSize: '9px' }}>F1 Classification Index</span>
              <div className="flex justify-between items-end w-full" style={{ marginTop: '10px' }}>
                <span className="font-mono text-metric">{metrics.f1Score?.value}%</span>
                <span className="trend-badge trend-up">{metrics.f1Score?.trend}</span>
              </div>
            </div>

            {/* ROC AUC */}
            <div className="card flex flex-col justify-between" style={{ padding: '16px 20px' }}>
              <span className="text-label" style={{ fontSize: '9px' }}>Area Under ROC (AUC)</span>
              <div className="flex justify-between items-end w-full" style={{ marginTop: '10px' }}>
                <span className="font-mono text-metric">{metrics.rocAuc?.value}</span>
                <span className="trend-badge trend-up">{metrics.rocAuc?.trend}</span>
              </div>
            </div>
          </div>

          {/* Middle Row: Confusion Matrix & ROC Curve */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.2fr 1.8fr' }}>
            {/* Confusion Matrix Card */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '400px' }}>
              <div>
                <h3 className="text-h3 font-display">Confusion Matrix</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Testing set distribution (n = 47,809 records)</span>
              </div>

              <div className="matrix-grid" style={{ marginTop: '20px', flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div className="flex gap-8" style={{ flex: 1 }}>
                  {/* True Negative */}
                  <div className="matrix-cell bg-safe-bg flex flex-col justify-center items-center" style={{ flex: 1, border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', padding: '16px' }}>
                    <span className="text-label" style={{ fontSize: '8px' }}>True Neg (TN)</span>
                    <span className="font-mono text-data block" style={{ fontSize: '16px', fontWeight: 800, color: '#059669' }}>{matrix.trueNegative?.toLocaleString()}</span>
                    <span className="text-label" style={{ fontSize: '7px', textTransform: 'none' }}>Correct safe accounts</span>
                  </div>
                  {/* False Positive */}
                  <div className="matrix-cell bg-critical-bg flex flex-col justify-center items-center" style={{ flex: 1, border: '1px solid rgba(239,68,68,0.2)', borderRadius: '8px', padding: '16px' }}>
                    <span className="text-label" style={{ fontSize: '8px', color: 'var(--critical)' }}>False Pos (FP: FPR {matrix.fpr}%)</span>
                    <span className="font-mono text-data block text-critical" style={{ fontSize: '16px', fontWeight: 800 }}>{matrix.falsePositive?.toLocaleString()}</span>
                    <span className="text-label" style={{ fontSize: '7px', textTransform: 'none' }}>False alarms (Watchlist)</span>
                  </div>
                </div>

                <div className="flex gap-8" style={{ flex: 1 }}>
                  {/* False Negative */}
                  <div className="matrix-cell bg-watchlist-bg flex flex-col justify-center items-center" style={{ flex: 1, border: '1px solid rgba(245,158,11,0.2)', borderRadius: '8px', padding: '16px' }}>
                    <span className="text-label" style={{ fontSize: '8px', color: 'var(--warning)' }}>False Neg (FN: FNR {matrix.fnr}%)</span>
                    <span className="font-mono text-data block text-warning" style={{ fontSize: '16px', fontWeight: 800 }}>{matrix.falseNegative?.toLocaleString()}</span>
                    <span className="text-label" style={{ fontSize: '7px', textTransform: 'none' }}>Missed mules</span>
                  </div>
                  {/* True Positive */}
                  <div className="matrix-cell bg-safe-bg flex flex-col justify-center items-center" style={{ flex: 1, border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', padding: '16px' }}>
                    <span className="text-label" style={{ fontSize: '8px' }}>True Pos (TP)</span>
                    <span className="font-mono text-data block" style={{ fontSize: '16px', fontWeight: 800, color: '#059669' }}>{matrix.truePositive?.toLocaleString()}</span>
                    <span className="text-label" style={{ fontSize: '7px', textTransform: 'none' }}>Correctly flagged mules</span>
                  </div>
                </div>
              </div>
            </div>

            {/* ROC Curve Chart */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '400px' }}>
              <div>
                <h3 className="text-h3 font-display">Ensemble ROC curve</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Ensemble performance relative to random classification</span>
              </div>

              <div style={{ flex: 1, marginTop: '16px' }}>
                <ReactECharts option={getRocOption()} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>
          </div>

          {/* Model Weights & Health Grid */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.2fr 1.8fr' }}>
            {/* Stacking Weights */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '300px' }}>
              <div>
                <h3 className="text-h3 font-display">Model Stacking Coefficients</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Linear weights allocated to individual model predictors</span>
              </div>

              <div className="base-models-list flex flex-col gap-12" style={{ marginTop: '20px', flex: 1 }}>
                {baseModels.map(bm => (
                  <div key={bm.name} className="base-model-item flex flex-col gap-4">
                    <div className="flex justify-between text-data" style={{ fontSize: '12px' }}>
                      <span style={{ fontWeight: 600 }}>{bm.name} (AUC: {bm.auc})</span>
                      <span className="font-mono text-muted">{(bm.weight * 100).toFixed(0)}% weight</span>
                    </div>
                    <div className="progress-bar w-full" style={{ height: '6px' }}>
                      <div className="progress-bar__fill" style={{ width: `${bm.weight * 100}%`, backgroundColor: 'var(--primary)' }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Health Logs */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '300px' }}>
              <div>
                <h3 className="text-h3 font-display">Neural Stream Health Diagnostics</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Telemetry drift verification nodes</span>
              </div>

              {health.status && (
                <div className="grid-3" style={{ marginTop: '20px', flex: 1, gap: '16px' }}>
                  <div className="health-card bg-safe-bg flex flex-col gap-8" style={{ border: '1px solid rgba(16,185,129,0.15)', borderRadius: '8px', padding: '16px' }}>
                    <span className="text-label" style={{ fontSize: '8px' }}>Concept Drift</span>
                    <span className="font-mono text-data text-accent block" style={{ fontSize: '18px', fontWeight: 800 }}>{health.conceptDrift.level}</span>
                    <span className="text-label" style={{ fontSize: '7px', textTransform: 'none' }}>Psi coefficient: {health.conceptDrift.score}</span>
                  </div>

                  <div className="health-card bg-safe-bg flex flex-col gap-8" style={{ border: '1px solid rgba(16,185,129,0.15)', borderRadius: '8px', padding: '16px' }}>
                    <span className="text-label" style={{ fontSize: '8px' }}>Data Drift</span>
                    <span className="font-mono text-data text-accent block" style={{ fontSize: '18px', fontWeight: 800 }}>{health.dataDrift.level}</span>
                    <span className="text-label" style={{ fontSize: '7px', textTransform: 'none' }}>Psi coefficient: {health.dataDrift.score}</span>
                  </div>

                  <div className="health-card bg-surface-2 flex flex-col gap-8" style={{ borderRadius: '8px', padding: '16px' }}>
                    <span className="text-label" style={{ fontSize: '8px' }}>Retrain Cycle</span>
                    <span className="font-mono text-data block" style={{ fontSize: '14px', fontWeight: 700 }}>{health.lastRetrain}</span>
                    <span className="text-label" style={{ fontSize: '7px', textTransform: 'none' }}>Next retrain: {health.nextScheduled}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
