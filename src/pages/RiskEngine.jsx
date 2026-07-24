import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { TrendingUp, Award, ShieldAlert, Cpu, AlertCircle, HelpCircle } from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';

export default function RiskEngine() {
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [history, setHistory] = useState([]);
  const [breakdown, setBreakdown] = useState(null);
  const [forecast, setForecast] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const accs = await api.getAccounts();
      setAccounts(accs);
      if (accs.length > 0) {
        setSelectedAccountId(accs[0].id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Fetch details for account
  useEffect(() => {
    if (!selectedAccountId) return;
    const fetchRiskDetails = async () => {
      try {
        const [histRes, breakRes, foreRes] = await Promise.all([
          api.getAccountRiskHistory(selectedAccountId),
          api.getAccountRiskBreakdown(selectedAccountId),
          api.getAccountFuturePrediction(selectedAccountId)
        ]);
        setHistory(histRes);
        setBreakdown(breakRes);
        setForecast(foreRes);
      } catch (e) {
        console.error(e);
      }
    };
    fetchRiskDetails();
  }, [selectedAccountId]);

  // ECharts Option: Historical Risk & Forecast Confidence Band
  const getRiskHistoryOption = () => {
    if (!history || history.length === 0) return {};
    
    // Past dates and values
    const dates = history.map(h => h.date);
    const scores = history.map(h => h.score);

    // Append forecast dates and scores (next 3 points)
    const futureDates = [...dates, 'Day +1', 'Day +3', 'Day +7'];
    const pastLength = dates.length;
    
    // Values with forecast appending
    const todayScore = scores[scores.length - 1];
    const forecastVal1 = forecast?.day1 || todayScore;
    const forecastVal3 = forecast?.day3 || todayScore + 1;
    const forecastVal7 = forecast?.day7 || todayScore + 2;

    const lineData = [...scores, forecastVal1, forecastVal3, forecastVal7];
    
    // Confidence intervals (upper / lower bands)
    const upperBand = [];
    const lowerBand = [];
    
    // Fill past with null (so it doesn't render band in historical data)
    for (let i = 0; i < pastLength - 1; i++) {
      upperBand.push(null);
      lowerBand.push(null);
    }
    // Anchor point today
    upperBand.push(todayScore);
    lowerBand.push(todayScore);
    
    // Future boundaries
    upperBand.push(Math.min(forecastVal1 + 4, 100));
    lowerBand.push(Math.max(forecastVal1 - 4, 0));

    upperBand.push(Math.min(forecastVal3 + 7, 100));
    lowerBand.push(Math.max(forecastVal3 - 7, 0));

    upperBand.push(Math.min(forecastVal7 + 12, 100));
    lowerBand.push(Math.max(forecastVal7 - 12, 0));

    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 }
      },
      legend: {
        data: ['Observed Risk Index', 'Forecast Projection', 'Confidence Bounds (95%)'],
        bottom: 0,
        textStyle: { color: '#64748b', fontWeight: 600 }
      },
      grid: { left: '3%', right: '3%', top: '5%', bottom: '12%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: futureDates,
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        axisLabel: { color: '#64748b' }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f1f5f9' } },
        axisLabel: { color: '#64748b' }
      },
      series: [
        {
          name: 'Observed Risk Index',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 3 },
          color: '#3b82f6',
          data: lineData.slice(0, pastLength) // render only past
        },
        {
          name: 'Forecast Projection',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 3, type: 'dashed' },
          color: '#ef4444',
          data: lineData // renders whole line including future
        },
        // Area band for confidence interval
        {
          name: 'Confidence Bounds (95%)',
          type: 'line',
          data: upperBand,
          lineStyle: { opacity: 0 },
          stack: 'confidence-band',
          symbol: 'none'
        },
        {
          name: 'Confidence Bounds (95%)',
          type: 'line',
          data: lowerBand.map((val, idx) => {
            if (val === null || upperBand[idx] === null) return null;
            return upperBand[idx] - val; // difference to render stack
          }),
          lineStyle: { opacity: 0 },
          stack: 'confidence-band',
          areaStyle: {
            color: 'rgba(239, 68, 68, 0.12)'
          },
          symbol: 'none'
        }
      ]
    };
  };

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">Forensic Risk Score Engine</h1>
          <p className="page-subtitle">Unified model aggregator processing penalty boosters, anomaly coefficients, and network weights.</p>
        </div>

        <div className="flex items-center gap-8">
          <span className="text-label" style={{ fontSize: '12px' }}>Audit Target:</span>
          <select 
            className="input font-mono" 
            style={{ width: '160px', padding: '6px 12px' }}
            value={selectedAccountId}
            onChange={(e) => setSelectedAccountId(e.target.value)}
          >
            {accounts.map(a => (
              <option key={a.id} value={a.id}>{a.id}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '70vh' }}>
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
          <span className="text-label" style={{ marginTop: '16px' }}>Decrypting score logs...</span>
        </div>
      ) : (
        <div className="flex flex-col gap-24 w-full">
          {/* Main Chart Card */}
          <div className="card flex flex-col justify-between" style={{ minHeight: '440px' }}>
            <div>
              <h3 className="text-h3 font-display">Risk History & Predictive Forecast Range</h3>
              <span className="text-label" style={{ fontSize: '10px' }}>30-day tracking of risk index scores correlated with future confidence bands</span>
            </div>

            <div style={{ flex: 1, marginTop: '24px' }}>
              <ReactECharts option={getRiskHistoryOption()} style={{ height: '100%', width: '100%' }} />
            </div>
          </div>

          {/* Model Weights and Explanations Row */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.8fr 1.2fr' }}>
            {/* Risk zones breakdown */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '320px' }}>
              <div>
                <h3 className="text-h3 font-display">Risk Stratification Thresholds</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Standard regulatory thresholds configured inside bank clusters</span>
              </div>

              <div className="risk-threshold-zones flex flex-col gap-12" style={{ marginTop: '16px' }}>
                <div className="zone-row flex items-center justify-between w-full" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
                  <span className="risk-badge risk-badge--critical" style={{ width: '120px' }}>CRITICAL (&gt;80)</span>
                  <p className="text-data text-muted" style={{ fontSize: '12px', flex: 1, margin: '0 16px', lineHeight: 1.3 }}>
                    Immediate fund freeze directive. STR report generated and sent to FIU node. Branch networks notified under PMLA rules.
                  </p>
                </div>

                <div className="zone-row flex items-center justify-between w-full" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
                  <span className="risk-badge risk-badge--suspicious" style={{ width: '120px' }}>SUSPICIOUS (51-80)</span>
                  <p className="text-data text-muted" style={{ fontSize: '12px', flex: 1, margin: '0 16px', lineHeight: 1.3 }}>
                    Enhanced monitoring cue. Secondary KYC checks triggered. Transaction velocity limits decreased by 50%.
                  </p>
                </div>

                <div className="zone-row flex items-center justify-between w-full" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
                  <span className="risk-badge risk-badge--watchlist" style={{ width: '120px' }}>WATCHLIST (21-50)</span>
                  <p className="text-data text-muted" style={{ fontSize: '12px', flex: 1, margin: '0 16px', lineHeight: 1.3 }}>
                    Flagged for audit review. Shared account activity cross-referenced against known clusters.
                  </p>
                </div>

                <div className="zone-row flex items-center justify-between w-full" style={{ paddingBottom: '4px' }}>
                  <span className="risk-badge risk-badge--safe" style={{ width: '120px' }}>SAFE (0-20)</span>
                  <p className="text-data text-muted" style={{ fontSize: '12px', flex: 1, margin: '0 16px', lineHeight: 1.3 }}>
                    Standard bank operation parameters. Normal consumer profile behavior.
                  </p>
                </div>
              </div>
            </div>

            {/* Predictive Verdict Explanations */}
            <div className="card flex flex-col justify-between bg-primary-light" style={{ border: '1.5px solid rgba(37,99,235,0.15)', minHeight: '320px' }}>
              <div>
                <span className="text-label text-gradient" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Award size={16} />
                  Risk Engine Verdict
                </span>
                <h3 className="text-h3" style={{ color: 'var(--primary-dark)', marginTop: '8px' }}>Forensic Action Forecast</h3>
              </div>

              {forecast && (
                <div style={{ flex: 1, margin: '16px 0', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  <div className="forecast-stat flex justify-between w-full" style={{ marginBottom: '8px' }}>
                    <span>Predicted Day 7 Risk Index:</span>
                    <span className="font-mono font-bold text-red" style={{ color: forecast.trend === 'Escalating' ? 'var(--critical)' : 'var(--text-secondary)' }}>
                      {forecast.day7} / 100
                    </span>
                  </div>
                  <div className="forecast-stat flex justify-between w-full" style={{ marginBottom: '12px' }}>
                    <span>Forecast State:</span>
                    <span className="font-mono text-data" style={{ fontWeight: 600 }}>{forecast.trend}</span>
                  </div>

                  <div className="recommendation-panel" style={{ background: '#fff', borderRadius: '8px', padding: '12px', border: '1px solid rgba(37,99,235,0.1)' }}>
                    <span className="text-label" style={{ fontSize: '8px' }}>SYSTEM DIRECTIVE:</span>
                    <span className="text-data block font-bold text-red" style={{ color: forecast.day7 > 80 ? 'var(--critical)' : 'var(--warning)', marginTop: '4px' }}>
                      {forecast.recommendation}
                    </span>
                  </div>
                </div>
              )}

              <button className="btn btn-primary w-full" onClick={() => setSelectedAccountId(accounts.find(a => a.id !== selectedAccountId)?.id || selectedAccountId)}>
                Toggle Account Targets
              </button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
