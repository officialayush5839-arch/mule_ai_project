import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { Sparkles, HelpCircle, AlertOctagon, Info, ArrowRight, UserCheck } from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';
import ShapWaterfall from '../components/ShapWaterfall';
import { getFeatureLabel } from '../lib/utils';

export default function ExplainableAI() {
  const [loading, setLoading] = useState(true);
  const [globalImportance, setGlobalImportance] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [localShap, setLocalShap] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [globalRes, accountsRes] = await Promise.all([
        api.getGlobalFeatureImportance(),
        api.getAccounts()
      ]);
      setGlobalImportance(globalRes);
      setAccounts(accountsRes);
      
      if (accountsRes.length > 0) {
        setSelectedAccountId(accountsRes[0].id);
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

  // Fetch local SHAP when account changes
  useEffect(() => {
    if (!selectedAccountId) return;
    const fetchLocal = async () => {
      try {
        const shap = await api.getAccountShap(selectedAccountId);
        setLocalShap(shap);
      } catch (e) {
        console.error(e);
      }
    };
    fetchLocal();
  }, [selectedAccountId]);

  // ECharts Option: Global Feature Importance
  const getGlobalOption = () => {
    const data = [...globalImportance].reverse(); // reverse for bottom-up drawing in horizontal chart
    
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 }
      },
      grid: { left: '3%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
      xAxis: {
        type: 'value',
        name: 'Mean |SHAP Value|',
        splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
        axisLabel: { color: '#64748b' }
      },
      yAxis: {
        type: 'category',
        data: data.map(item => getFeatureLabel(item.feature)),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#475569', fontSize: 10, width: 140, overflow: 'truncate' }
      },
      series: [
        {
          name: 'SHAP Feature Importance',
          type: 'bar',
          barWidth: 10,
          itemStyle: {
            color: '#3b82f6',
            borderRadius: [0, 4, 4, 0]
          },
          data: data.map(item => item.importance)
        }
      ]
    };
  };

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">Explainable AI Dashboard (SHAP)</h1>
          <p className="page-subtitle">Translate complex neural network and tree boosting decisions into human-auditable explanations.</p>
        </div>
      </div>

      {loading ? (
        <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '70vh' }}>
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
          <span className="text-label" style={{ marginTop: '16px' }}>Fitting SHAP values...</span>
        </div>
      ) : (
        <div className="flex flex-col gap-24 w-full">
          {/* Main SHAP summary rows */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.4fr 1.6fr' }}>
            {/* Global Feature Importance */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '480px' }}>
              <div>
                <h3 className="text-h3 font-display">Global SHAP Feature Importance</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Contribution frequency across all classified accounts (Stacking ensemble)</span>
              </div>
              <div style={{ flex: 1, marginTop: '24px' }}>
                <ReactECharts option={getGlobalOption()} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>

            {/* Local waterfall & target selector */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '480px' }}>
              <div className="flex justify-between items-start w-full">
                <div>
                  <h3 className="text-h3 font-display">Local SHAP Explanation</h3>
                  <span className="text-label" style={{ fontSize: '10px' }}>Audit individual account classifications</span>
                </div>

                <div className="flex items-center gap-8">
                  <span className="text-label" style={{ fontSize: '9px' }}>Audit Target:</span>
                  <select 
                    className="input font-mono" 
                    style={{ width: '150px', padding: '4px 8px', fontSize: '12px' }}
                    value={selectedAccountId}
                    onChange={(e) => setSelectedAccountId(e.target.value)}
                  >
                    {accounts.map(a => (
                      <option key={a.id} value={a.id}>{a.id}</option>
                    ))}
                  </select>
                </div>
              </div>

              {localShap ? (
                <div className="flex-1 flex flex-col justify-between" style={{ marginTop: '16px' }}>
                  {/* Explainer Stats Panel */}
                  <div className="flex justify-between items-center bg-surface-2" style={{ padding: '12px 16px', borderRadius: '8px', marginBottom: '12px' }}>
                    <div>
                      <span className="text-label" style={{ fontSize: '8px' }}>Model Base Probability</span>
                      <span className="font-mono text-data block" style={{ fontWeight: 700 }}>{localShap.baseValue}</span>
                    </div>
                    <div>
                      <span className="text-label" style={{ fontSize: '8px' }}>Final Risk Index</span>
                      <span className="font-mono text-data block" style={{ fontWeight: 700, color: 'var(--critical)' }}>{localShap.probability.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-label" style={{ fontSize: '8px' }}>Accumulated Forces</span>
                      <span className="font-mono text-data block" style={{ fontWeight: 700, color: 'var(--primary)' }}>+{(localShap.probability - localShap.baseValue).toFixed(2)}</span>
                    </div>
                  </div>

                  <div style={{ flex: 1 }}>
                    <ShapWaterfall features={localShap.features} />
                  </div>
                </div>
              ) : (
                <div className="flex-grow flex items-center justify-center">
                  <span className="text-label">Loading local SHAP weights...</span>
                </div>
              )}
            </div>
          </div>

          {/* Model Trust and Regulatory Audits Info */}
          <div className="card flex flex-col gap-12 bg-primary-light" style={{ border: '1.5px solid rgba(37,99,235,0.15)' }}>
            <div className="flex items-center gap-8 text-gradient">
              <Sparkles size={18} className="text-primary" />
              <h3 className="text-h3">Regulatory Compliance & PMLA Audit Trails</h3>
            </div>
            <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Under the <b>Prevention of Money Laundering Act (PMLA) Section 12</b>, Indian commercial banks are required to maintain clear 
              justification trails for frozen accounts and Suspicious Transaction Reports (STRs). 
              MuleNet AI utilizes game-theoretic SHAP (SHapley Additive exPlanations) values to guarantee 
              <b> "Right to Explanation"</b> standards, proving exactly which behavioral anomalies triggered the ensemble classification model.
            </p>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
