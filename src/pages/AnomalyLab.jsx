import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import { 
  Binary, 
  Upload, 
  FileSpreadsheet, 
  CheckCircle, 
  Cpu, 
  HelpCircle,
  Eye,
  AlertTriangle,
  FileCheck
} from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';
import RiskBadge from '../components/RiskBadge';

export default function AnomalyLab() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(true);
  
  // States
  const [models, setModels] = useState([]);
  const [scatterPoints, setScatterPoints] = useState([]);
  const [rankings, setRankings] = useState([]);
  
  // CSV Upload States
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [modelsRes, scatterRes, rankingRes] = await Promise.all([
        api.getAnomalyModels(),
        api.getAnomalyScatter(),
        api.getAnomalyRankings()
      ]);
      setModels(modelsRes);
      setScatterPoints(scatterRes);
      setRankings(rankingRes);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    const handleDataChange = () => {
      loadData();
    };
    window.addEventListener('datasource-changed', handleDataChange);
    return () => window.removeEventListener('datasource-changed', handleDataChange);
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setUploadError('Invalid file type. Only CSV files are supported.');
      return;
    }

    setUploadError(null);
    setIsUploading(true);
    setUploadResult(null);

    try {
      const result = await api.uploadCSV(file);
      setUploadResult(result);
    } catch (err) {
      setUploadError('Failed to process batch CSV file. Technical error.');
    } finally {
      setIsUploading(false);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  // ECharts PCA Scatter option
  const getScatterOption = () => {
    const normal = scatterPoints.filter(p => p.severity === 'normal');
    const anomalies = scatterPoints.filter(p => p.severity !== 'normal');

    return {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 },
        formatter: function (params) {
          const pt = params.data;
          return `
            <b>Account ID: ${pt[2]}</b><br/>
            PCA C1: ${pt[0].toFixed(2)}<br/>
            PCA C2: ${pt[1].toFixed(2)}<br/>
            Outlier Score: ${(pt[3] * 100).toFixed(1)}%<br/>
            IF Score: ${pt[4]} | AE: ${pt[5]}
          `;
        }
      },
      legend: {
        data: ['Normal Transactions', 'Outlier Anomalies'],
        bottom: 0,
        textStyle: { color: '#64748b', fontWeight: 600 }
      },
      grid: { left: '3%', right: '3%', top: '5%', bottom: '10%', containLabel: true },
      xAxis: {
        type: 'value',
        name: 'PCA Comp 1',
        splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
        axisLabel: { color: '#64748b' }
      },
      yAxis: {
        type: 'value',
        name: 'PCA Comp 2',
        splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
        axisLabel: { color: '#64748b' }
      },
      series: [
        {
          name: 'Normal Transactions',
          type: 'scatter',
          symbolSize: 5,
          color: 'rgba(59, 130, 246, 0.45)', // Blue
          data: normal.map(p => [p.x, p.y, p.id, p.combined, p.ifScore, p.aeScore])
        },
        {
          name: 'Outlier Anomalies',
          type: 'scatter',
          symbolSize: (data) => {
            const score = data[3] || 0.5;
            return score * 14;
          },
          color: '#ef4444', // Red
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(239, 68, 68, 0.6)'
          },
          data: anomalies.map(p => [p.x, p.y, p.id, p.combined, p.ifScore, p.aeScore])
        }
      ]
    };
  };

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">Unsupervised Anomaly Lab</h1>
          <p className="page-subtitle">Isolate zero-day money laundering Typologies using Autoencoders & Isolation Forests.</p>
        </div>
      </div>

      {loading ? (
        <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '70vh' }}>
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
          <span className="text-label" style={{ marginTop: '16px' }}>Projecting tensor anomalies...</span>
        </div>
      ) : (
        <div className="flex flex-col gap-24 w-full">
          {/* Top Row: Unsupervised Algorithm Cards */}
          <div className="grid-3 w-full">
            {models.map((model) => (
              <div key={model.name} className="card flex flex-col justify-between">
                <div className="flex justify-between items-start w-full">
                  <div>
                    <h3 className="text-h3 font-display" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Binary size={18} className="text-primary" />
                      {model.name}
                    </h3>
                    <span className="text-label" style={{ fontSize: '9px', textTransform: 'none' }}>Anomaly threshold: {model.threshold}</span>
                  </div>
                  <span className="risk-badge risk-badge--watchlist" style={{ fontSize: '10px' }}>
                    {model.anomalies} Flags
                  </span>
                </div>
                
                <div className="grid-2 w-full border-top-divider" style={{ marginTop: '20px', paddingTop: '12px' }}>
                  <div className="flex flex-col">
                    <span className="text-label" style={{ fontSize: '9px' }}>Model Precision</span>
                    <span className="text-data font-mono" style={{ fontWeight: 700, color: 'var(--accent)' }}>{(model.precision * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-label" style={{ fontSize: '9px' }}>Model Recall</span>
                    <span className="text-data font-mono" style={{ fontWeight: 700, color: 'var(--primary)' }}>{(model.recall * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Core Analytics: PCA Scatter & Bulk CSV Upload */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.8fr 1.2fr' }}>
            {/* PCA Scatter Chart */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '420px' }}>
              <div>
                <h3 className="text-h3 font-display">Multi-Dimensional PCA Outliers</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Scatter projection of high-dimensional transactions down to 2 principal components</span>
              </div>
              
              <div style={{ flex: 1, marginTop: '24px' }}>
                <ReactECharts option={getScatterOption()} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>

            {/* Drag & Drop Upload Simulation */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '420px' }}>
              <div>
                <h3 className="text-h3 font-display">Batch File Analysis</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Upload large transaction CSV logs to score accounts in batch</span>
              </div>

              <div className="upload-container-wrapper" style={{ flex: 1, margin: '24px 0', display: 'flex', flexDirection: 'column', justify: 'center' }}>
                {!isUploading && !uploadResult && (
                  <div 
                    className="drag-drop-zone flex flex-col items-center justify-center gap-16 cursor-pointer"
                    onClick={triggerFileSelect}
                  >
                    <Upload size={40} className="text-primary animate-pulse" />
                    <div className="text-center">
                      <span className="text-data block" style={{ fontWeight: 700 }}>Select Batch CSV File</span>
                      <span className="text-label" style={{ fontSize: '10px', textTransform: 'none' }}>Supports standard corporate transaction headers</span>
                    </div>
                    <input 
                      type="file" 
                      ref={fileInputRef} 
                      style={{ display: 'none' }} 
                      accept=".csv"
                      onChange={handleFileUpload}
                    />
                  </div>
                )}

                {isUploading && (
                  <div className="upload-processing flex flex-col items-center justify-center gap-16" style={{ height: '100%' }}>
                    <div className="spinner" style={{ width: '36px', height: '36px', borderWidth: '3px' }}></div>
                    <div className="text-center">
                      <span className="text-data block" style={{ fontWeight: 700 }}>Processing Batch File...</span>
                      <span className="text-label" style={{ fontSize: '10px', textTransform: 'none' }}>Generating SMOTE scaling dimensions...</span>
                    </div>
                  </div>
                )}

                {uploadResult && (
                  <div className="upload-success-panel flex flex-col gap-12" style={{ overflowY: 'auto', maxHeight: '280px' }}>
                    <div className="flex items-center gap-8 text-accent">
                      <FileCheck size={20} />
                      <span className="text-data" style={{ fontWeight: 700 }}>Analysis Complete</span>
                    </div>

                    <div className="grid-2 bg-primary-light" style={{ padding: '12px', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.1)' }}>
                      <div>
                        <span className="text-label" style={{ fontSize: '8px' }}>Total Uploaded</span>
                        <span className="font-mono text-data block" style={{ fontSize: '18px', fontWeight: 800 }}>{uploadResult.totalUploaded}</span>
                      </div>
                      <div>
                        <span className="text-label" style={{ fontSize: '8px', color: 'var(--critical)' }}>Anomalies Flagged</span>
                        <span className="font-mono text-data block text-critical" style={{ fontSize: '18px', fontWeight: 800 }}>{uploadResult.anomaliesDetected}</span>
                      </div>
                    </div>

                    <div className="upload-anomaly-list flex flex-col gap-8">
                      <span className="text-label" style={{ fontSize: '9px' }}>Critical Outliers Found:</span>
                      {uploadResult.anomalousAccounts.map(acc => (
                        <div key={acc.id} className="flex justify-between items-center bg-surface-2" style={{ padding: '8px 12px', borderRadius: '6px' }}>
                          <span className="font-mono text-data cursor-pointer text-primary" style={{ fontSize: '12px' }} onClick={() => navigate(`/account-intel?id=${acc.id}`)}>
                            {acc.id}
                          </span>
                          <span className="risk-badge risk-badge--critical" style={{ fontSize: '8px', padding: '2px 6px' }}>
                            Risk {acc.riskScore}
                          </span>
                        </div>
                      ))}
                    </div>

                    <button className="btn btn-secondary btn-sm" onClick={() => setUploadResult(null)}>
                      Upload Another File
                    </button>
                  </div>
                )}

                {uploadError && (
                  <div className="upload-error flex flex-col items-center gap-12 text-critical text-center">
                    <AlertTriangle size={32} />
                    <span className="text-data" style={{ fontWeight: 600 }}>{uploadError}</span>
                    <button className="btn btn-ghost btn-sm" onClick={() => setUploadError(null)}>Retry</button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Ranking & Escalation Queue */}
          <div className="card flex flex-col gap-16">
            <div>
              <h3 className="text-h3 font-display">Unsupervised Outlier Rank Queue</h3>
              <span className="text-label" style={{ fontSize: '10px' }}>Top structural outlier nodes detected across all three algorithms</span>
            </div>

            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th className="text-center" style={{ width: '60px' }}>Rank</th>
                    <th>Account ID</th>
                    <th className="text-right">Isolation Forest Score</th>
                    <th className="text-right">Autoencoder Loss</th>
                    <th className="text-right">Local Outlier Factor</th>
                    <th className="text-right">Combined Index</th>
                    <th className="text-center">Severity</th>
                    <th className="text-center">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {rankings.map((pt) => (
                    <tr key={pt.id} className="table-row-interactive">
                      <td className="text-center col-mono" style={{ fontWeight: 700 }}>#{pt.rank}</td>
                      <td className="col-mono">{pt.id}</td>
                      <td className="text-right font-mono">{pt.ifScore.toFixed(2)}</td>
                      <td className="text-right font-mono">{pt.aeScore.toFixed(2)}</td>
                      <td className="text-right font-mono">{pt.lofScore.toFixed(2)}</td>
                      <td className="text-right font-mono" style={{ fontWeight: 700, color: pt.combined > 0.8 ? 'var(--critical)' : 'var(--warning)' }}>
                        {(pt.combined * 100).toFixed(1)}%
                      </td>
                      <td className="text-center">
                        <span className={`risk-badge risk-badge--${pt.severity}`}>
                          {pt.severity}
                        </span>
                      </td>
                      <td className="text-center">
                        <button 
                          className="btn-icon btn-sm"
                          onClick={() => navigate(`/account-intel?id=${pt.id}`)}
                        >
                          <Eye size={12} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .drag-drop-zone {
          border: 2px dashed var(--border);
          border-radius: var(--radius-lg);
          padding: 40px 20px;
          background: rgba(248, 250, 252, 0.4);
          transition: all var(--transition-base);
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }

        .drag-drop-zone:hover {
          border-color: var(--primary);
          background: var(--primary-light);
        }
      `}</style>
    </AppLayout>
  );
}
