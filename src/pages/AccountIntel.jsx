import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import { 
  Search, 
  ShieldAlert, 
  User, 
  Calendar, 
  MapPin, 
  Ban, 
  CheckCircle, 
  Eye, 
  Clock, 
  Activity,
  FileSpreadsheet,
  AlertTriangle
} from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';
import RiskBadge from '../components/RiskBadge';
import RiskGauge from '../components/RiskGauge';
import BehaviorRadar from '../components/BehaviorRadar';
import ShapWaterfall from '../components/ShapWaterfall';
import { formatIndianCurrency, formatScore, getRiskColor, getRiskBg } from '../lib/utils';

export default function AccountIntel() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const accountId = searchParams.get('id');

  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Account details states
  const [shap, setShap] = useState(null);
  const [radar, setRadar] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [futureRisk, setFutureRisk] = useState(null);
  const [breakdown, setBreakdown] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);

  // Load account lists
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const accs = await api.getAccounts();
        setAccounts(accs);
        
        // If no ID is in URL or the current ID does not exist in the new dataset, select first critical
        const hasCurrentId = accs.some(a => a.id === accountId);
        if ((!accountId || !hasCurrentId) && accs.length > 0) {
          const firstCrit = accs.find(a => a.classification === 'CRITICAL') || accs[0];
          setSearchParams({ id: firstCrit.id });
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchAccounts();

    const handleDataChange = () => {
      fetchAccounts();
    };
    window.addEventListener('datasource-changed', handleDataChange);
    return () => window.removeEventListener('datasource-changed', handleDataChange);
  }, [accountId]);

  // Fetch individual details when ID changes
  useEffect(() => {
    if (!accountId) return;
    
    const fetchDetails = async () => {
      setLoading(true);
      try {
        const [accDetails, shapRes, radarRes, timelineRes, futureRes, breakdownRes] = await Promise.all([
          api.getAccountDetails(accountId),
          api.getAccountShap(accountId),
          api.getAccountBehaviorRadar(accountId),
          api.getAccountTransactionTrend(accountId),
          api.getAccountFuturePrediction(accountId),
          api.getAccountRiskBreakdown(accountId)
        ]);

        setSelectedAccount(accDetails);
        setShap(shapRes);
        setRadar(radarRes);
        setTimeline(timelineRes);
        setFutureRisk(futureRes);
        setBreakdown(breakdownRes);
        setActionMessage(null);
      } catch (e) {
        console.error("Failed to load details for " + accountId, e);
        setSelectedAccount(null);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [accountId]);

  // Transaction trend option
  const getTrendOption = () => {
    if (!timeline || timeline.length === 0) return {};
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 }
      },
      grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: timeline.map(t => t.date),
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        axisLabel: { color: '#64748b' }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Volume (₹)',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f1f5f9' } },
          axisLabel: {
            formatter: (v) => formatIndianCurrency(v),
            color: '#64748b'
          }
        },
        {
          type: 'value',
          name: 'Tx Count',
          axisLine: { show: false },
          splitLine: { show: false },
          axisLabel: { color: '#64748b' }
        }
      ],
      series: [
        {
          name: 'Volume (₹)',
          type: 'bar',
          itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] },
          data: timeline.map(t => t.volume)
        },
        {
          name: 'Tx Count',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          lineStyle: { width: 3 },
          color: '#f59e0b',
          data: timeline.map(t => t.count)
        }
      ]
    };
  };

  const handleAction = (type) => {
    const time = new Date().toLocaleTimeString('en-IN');
    if (type === 'freeze') {
      setActionMessage({ type: 'error', text: `Account FREEZE instruction sent to branch network at ${time}. Flagged to FIU-IND.` });
    } else if (type === 'watchlist') {
      setActionMessage({ type: 'warning', text: `Account placed on Advanced Watchlist node monitoring at ${time}.` });
    } else {
      setActionMessage({ type: 'success', text: `Account cleared. False positive status documented at ${time}.` });
    }
  };

  const currentClassification = selectedAccount?.classification || 'SAFE';
  const riskColor = getRiskColor(currentClassification);
  const riskBg = getRiskBg(currentClassification);

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">Account Intelligence Center</h1>
          <p className="page-subtitle">Deep forensic audit and explainable model metrics for target nodes.</p>
        </div>

        <div className="flex gap-12 items-center">
          <span className="text-label" style={{ fontSize: '12px' }}>Audit Target:</span>
          <select 
            className="input font-mono" 
            style={{ width: '180px', padding: '6px 12px' }}
            value={accountId || ''}
            onChange={(e) => setSearchParams({ id: e.target.value })}
          >
            {accounts.map(a => (
              <option key={a.id} value={a.id}>{a.id} - {a.name.slice(0, 15)}...</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '70vh' }}>
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
          <span className="text-label" style={{ marginTop: '16px' }}>Decrypting neural weights...</span>
        </div>
      ) : selectedAccount ? (
        <div className="flex flex-col gap-24 w-full animate-fade-in">
          {/* Action Alert Banner */}
          {actionMessage && (
            <div className={`action-alert-banner flex justify-between items-center bg-${actionMessage.type === 'error' ? 'critical-bg' : actionMessage.type === 'warning' ? 'watchlist-bg' : 'safe-bg'}`} style={{ border: `1.5px dashed ${actionMessage.type === 'error' ? 'var(--critical)' : actionMessage.type === 'warning' ? 'var(--warning)' : 'var(--accent)'}`, padding: '16px', borderRadius: '12px' }}>
              <span className="flex items-center gap-8 text-data" style={{ color: actionMessage.type === 'error' ? 'var(--critical)' : actionMessage.type === 'warning' ? 'var(--warning)' : '#059669', fontWeight: 600 }}>
                <AlertTriangle size={16} />
                <span>{actionMessage.text}</span>
              </span>
              <button className="btn btn-ghost btn-sm" onClick={() => setActionMessage(null)}>Dismiss</button>
            </div>
          )}

          {/* Account Profile Header Row */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.8fr 1.2fr' }}>
            {/* Left Card: Account Profile Meta */}
            <div className="card flex flex-col gap-20 justify-between">
              <div className="flex gap-20 items-center">
                <div className="profile-badge-avatar" style={{ backgroundColor: riskBg, color: riskColor }}>
                  <User size={32} />
                </div>
                <div className="flex flex-col">
                  <div className="flex items-center gap-12">
                    <h2 className="text-h2" style={{ fontWeight: 800 }}>{selectedAccount.name}</h2>
                    <RiskBadge classification={selectedAccount.classification} />
                  </div>
                  <span className="font-mono text-label" style={{ fontSize: '13px', marginTop: '2px' }}>Account ID: {selectedAccount.id}</span>
                </div>
              </div>

              <div className="grid-3 w-full border-top-divider" style={{ paddingTop: '20px' }}>
                <div className="flex flex-col">
                  <span className="text-label">Branch Location</span>
                  <span className="text-data text-primary" style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                    <MapPin size={13} />
                    {selectedAccount.branch}
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-label">Account Type</span>
                  <span className="text-data" style={{ fontWeight: 600, marginTop: '4px' }}>{selectedAccount.type}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-label">Opened Date</span>
                  <span className="text-data" style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                    <Calendar size={13} />
                    {selectedAccount.opened}
                  </span>
                </div>
              </div>

              {/* Analyst Decision Control Row */}
              <div className="flex justify-between items-center w-full border-top-divider" style={{ paddingTop: '20px' }}>
                <span className="text-label" style={{ fontSize: '10px' }}>FIU ACTIONS:</span>
                <div className="flex gap-12">
                  <button className="btn btn-secondary btn-sm" onClick={() => handleAction('clear')}>
                    <CheckCircle size={13} className="text-accent" /> Exonerate Account
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleAction('watchlist')}>
                    Add to Watchlist
                  </button>
                  <button 
                    className="btn btn-danger btn-sm" 
                    style={{ background: 'linear-gradient(135deg, #EF4444, #DC2626)' }}
                    onClick={() => handleAction('freeze')}
                  >
                    <Ban size={13} /> Freeze Funds
                  </button>
                </div>
              </div>
            </div>

            {/* Right Card: Risk Score Gauge and Prediction */}
            <div className="card flex flex-col justify-between items-center">
              <h3 className="text-h3 font-display w-full text-left" style={{ fontSize: '14px' }}>Unified Risk Indicator</h3>
              <RiskGauge score={selectedAccount.riskScore} />
              
              <div className="w-full flex justify-between items-center border-top-divider" style={{ paddingTop: '12px', marginTop: '8px' }}>
                <div className="flex flex-col">
                  <span className="text-label" style={{ fontSize: '9px' }}>Model Confidence</span>
                  <span className="font-mono text-data" style={{ fontWeight: 700 }}>{selectedAccount.confidence}%</span>
                </div>
                <div className="flex flex-col text-right">
                  <span className="text-label" style={{ fontSize: '9px' }}>Trend Forecast</span>
                  <span className="text-data font-mono font-bold text-red" style={{ color: futureRisk?.trend === 'Escalating' ? 'var(--critical)' : 'var(--text-secondary)' }}>
                    {futureRisk?.trend || 'Stable'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Model Breakdown & Behavioral Radar */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.2fr 1.8fr' }}>
            {/* Left Card: Behavioral Radar */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '340px' }}>
              <div>
                <h3 className="text-h3 font-display">Behavioral Deviations</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Deviation relative to standard branch baseline</span>
              </div>
              <div style={{ flex: 1, marginTop: '12px' }}>
                {radar && <BehaviorRadar current={radar.current} baseline={radar.baseline} />}
              </div>
            </div>

            {/* Right Card: Stacking Ensemble Risk Weights */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '340px' }}>
              <div>
                <h3 className="text-h3 font-display">Stacking Risk Contributions</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Contribution weighting calculated by Ensemble Meta-Classifier</span>
              </div>

              {breakdown && (
                <div className="weights-list flex flex-col gap-16" style={{ marginTop: '24px', flex: 1 }}>
                  <div className="weight-item flex items-center justify-between w-full">
                    <div style={{ width: '180px' }}>
                      <span className="font-mono text-data" style={{ fontWeight: 600 }}>Ensemble Model (LGBM)</span>
                      <span className="text-label block" style={{ fontSize: '9px', textTransform: 'none' }}>Gradient boosting classification</span>
                    </div>
                    <div className="progress-bar" style={{ flex: 1, margin: '0 20px', height: '10px' }}>
                      <div className="progress-bar__fill" style={{ width: `${breakdown.lgbmProbability * 100}%`, backgroundColor: 'var(--primary)' }}></div>
                    </div>
                    <span className="font-mono text-data" style={{ width: '60px', textAlign: 'right' }}>{formatScore(breakdown.lgbmContribution)} pts</span>
                  </div>

                  <div className="weight-item flex items-center justify-between w-full">
                    <div style={{ width: '180px' }}>
                      <span className="font-mono text-data" style={{ fontWeight: 600 }}>Anomaly Model (IsoForest)</span>
                      <span className="text-label block" style={{ fontSize: '9px', textTransform: 'none' }}>Unsupervised feature outlier score</span>
                    </div>
                    <div className="progress-bar" style={{ flex: 1, margin: '0 20px', height: '10px' }}>
                      <div className="progress-bar__fill" style={{ width: `${breakdown.anomalyScore * 100}%`, backgroundColor: 'var(--secondary)' }}></div>
                    </div>
                    <span className="font-mono text-data" style={{ width: '60px', textAlign: 'right' }}>{formatScore(breakdown.anomalyContribution)} pts</span>
                  </div>

                  <div className="weight-item flex items-center justify-between w-full">
                    <div style={{ width: '180px' }}>
                      <span className="font-mono text-data" style={{ fontWeight: 600 }}>Behavioral Deviation</span>
                      <span className="text-label block" style={{ fontSize: '9px', textTransform: 'none' }}>Variance from typical consumer usage</span>
                    </div>
                    <div className="progress-bar" style={{ flex: 1, margin: '0 20px', height: '10px' }}>
                      <div className="progress-bar__fill" style={{ width: `${breakdown.behavioralRisk * 100}%`, backgroundColor: 'var(--suspicious)' }}></div>
                    </div>
                    <span className="font-mono text-data" style={{ width: '60px', textAlign: 'right' }}>{formatScore(breakdown.behavioralContribution)} pts</span>
                  </div>

                  <div className="weight-item flex items-center justify-between w-full">
                    <div style={{ width: '180px' }}>
                      <span className="font-mono text-data" style={{ fontWeight: 600 }}>Graph Centrality Risk</span>
                      <span className="text-label block" style={{ fontSize: '9px', textTransform: 'none' }}>Proximity index to watchlisted clusters</span>
                    </div>
                    <div className="progress-bar" style={{ flex: 1, margin: '0 20px', height: '10px' }}>
                      <div className="progress-bar__fill" style={{ width: `${breakdown.networkRisk * 100}%`, backgroundColor: '#38bdf8' }}></div>
                    </div>
                    <span className="font-mono text-data" style={{ width: '60px', textAlign: 'right' }}>{formatScore(breakdown.networkContribution)} pts</span>
                  </div>

                  {breakdown.penaltyVelocitySpike > 0 && (
                    <div className="penalty-tag flex justify-between items-center w-full bg-critical-bg" style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.15)' }}>
                      <span className="text-data text-critical" style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <ShieldAlert size={14} /> Penalty Booster: Transaction Velocity Spike Detected
                      </span>
                      <span className="font-mono text-data text-critical" style={{ fontWeight: 700 }}>+{breakdown.penaltyVelocitySpike} pts</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Local Explainer (SHAP Waterfall) & Time series transactions */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.6fr 1.4fr' }}>
            {/* Local SHAP Waterfall */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '380px' }}>
              <div>
                <h3 className="text-h3 font-display">Local SHAP Explanation waterfall</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Features shifting probability output from baseline (0.31) to final prediction</span>
              </div>
              <div style={{ flex: 1, marginTop: '24px' }}>
                {shap && <ShapWaterfall features={shap.features} />}
              </div>
            </div>

            {/* Plain English summary report card */}
            <div className="card flex flex-col justify-between bg-primary-light" style={{ border: '1.5px solid rgba(37,99,235,0.15)', minHeight: '380px' }}>
              <div>
                <div className="flex items-center gap-8 text-label text-gradient">
                  <FileSpreadsheet size={16} className="text-primary" />
                  <span>Explainable AI (Forensic Notes)</span>
                </div>
                <h3 className="text-h3" style={{ color: 'var(--primary-dark)', marginTop: '8px' }}>Model Verdict Translation</h3>
              </div>

              <div className="explainable-notes" style={{ flex: 1, margin: '20px 0', display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                <p>
                  Target account <b>{selectedAccount.id}</b> is flagged as a <b>{selectedAccount.classification}</b> risk due to a confluence of velocity breaches and behavioral matches.
                </p>
                <div className="notes-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div className="note-line flex gap-8 items-start">
                    <span className="bullet text-critical" style={{ fontSize: '16px', lineHeight: 1 }}>•</span>
                    <span>
                      <b>Velocity Threshold (F527)</b>: Represents the strongest positive SHAP force. Current velocity is significantly elevated vs historical baseline.
                    </span>
                  </div>
                  <div className="note-line flex gap-8 items-start">
                    <span className="bullet text-critical" style={{ fontSize: '16px', lineHeight: 1 }}>•</span>
                    <span>
                      <b>Typology Match (F1692)</b>: The transaction sequence correlates closely with historical money mule behavior (rapid inflow-outflow).
                    </span>
                  </div>
                  <div className="note-line flex gap-8 items-start">
                    <span className="bullet text-green" style={{ fontSize: '16px', lineHeight: 1 }}>•</span>
                    <span>
                      <b>Account History (F670)</b>: Established account age operates as a minor protective factor, preventing an even higher risk score.
                    </span>
                  </div>
                </div>
                <p style={{ fontStyle: 'italic', fontSize: '12px', borderTop: '1px solid rgba(37,99,235,0.1)', paddingTop: '10px' }}>
                  Verdict: Escalation to FIU-IND recommended under PMLA rules. STR report template pre-compiled in Copilot.
                </p>
              </div>

              <button className="btn btn-primary w-full" onClick={() => navigate(`/copilot?query=generate report for ${selectedAccount.id}`)}>
                Open Report in AI Copilot
              </button>
            </div>
          </div>

          {/* Time Series Transaction Trends */}
          <div className="card flex flex-col justify-between" style={{ minHeight: '340px' }}>
            <div>
              <h3 className="text-h3 font-display">Transaction History Trends (30 Days)</h3>
              <span className="text-label" style={{ fontSize: '10px' }}>Correlation index between transaction volumes and overall frequency</span>
            </div>
            <div style={{ flex: 1, marginTop: '24px' }}>
              <ReactECharts option={getTrendOption()} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>
        </div>
      ) : (
        <div className="card text-center" style={{ padding: '40px' }}>
          <AlertTriangle size={48} className="text-critical" style={{ margin: '0 auto 16px' }} />
          <h3 className="text-h3">Account ID not found in telemetry registry</h3>
          <p className="text-muted" style={{ margin: '8px 0 20px' }}>The node may be dormant or does not exist.</p>
          <button className="btn btn-primary" onClick={() => setSearchParams({})}>Reset Lookup</button>
        </div>
      )}

      <style>{`
        .profile-badge-avatar {
          width: 64px;
          height: 64px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .border-top-divider {
          border-top: 1px solid var(--border);
        }
      `}</style>
    </AppLayout>
  );
}
