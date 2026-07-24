import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import { 
  ShieldAlert, 
  TrendingUp, 
  MapPin, 
  Bot, 
  Activity, 
  ArrowRight,
  Filter,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { api } from '../lib/api';
import KPICard from '../components/KPICard';
import AccountTable from '../components/AccountTable';
import AppLayout from '../components/AppLayout';

export default function CommandCenter() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState([]);
  const [riskDist, setRiskDist] = useState([]);
  const [riskTimeline, setRiskTimeline] = useState([]);
  const [geoRisk, setGeoRisk] = useState([]);
  const [insights, setInsights] = useState([]);
  const [highRiskAccounts, setHighRiskAccounts] = useState([]);
  const [insightIndex, setInsightIndex] = useState(0);

  // Load all dashboard data
  const fetchData = async () => {
    setLoading(true);
    try {
      const [kpiRes, distRes, timelineRes, geoRes, insightRes, accountRes] = await Promise.all([
        api.getKPIs(),
        api.getRiskDistribution(),
        api.getRiskTimeline(),
        api.getGeoRiskData(),
        api.getAIInsights(),
        api.getHighRiskAccounts(10)
      ]);
      setKpis(kpiRes);
      setRiskDist(distRes);
      setRiskTimeline(timelineRes);
      setGeoRisk(geoRes);
      setInsights(insightRes);
      setHighRiskAccounts(accountRes);
    } catch (e) {
      console.error("Error fetching command center data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    const handleDataChange = () => {
      fetchData();
    };
    window.addEventListener('datasource-changed', handleDataChange);
    return () => window.removeEventListener('datasource-changed', handleDataChange);
  }, []);

  // Auto-cycle AI Insights
  useEffect(() => {
    if (insights.length === 0) return;
    const interval = setInterval(() => {
      setInsightIndex((prev) => (prev + 1) % insights.length);
    }, 6000);
    return () => clearInterval(interval);
  }, [insights]);

  // ECharts Options: Risk Distribution Donut
  const getDonutOption = () => {
    return {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}% ({d}%)',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 }
      },
      legend: {
        orient: 'vertical',
        left: 'right',
        top: 'center',
        icon: 'circle',
        textStyle: { color: '#475569', fontWeight: 600, fontSize: 11 }
      },
      series: [
        {
          name: 'Risk Distribution',
          type: 'pie',
          radius: ['55%', '80%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 6,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false },
          labelLine: { show: false },
          data: riskDist.map(item => ({
            name: item.name,
            value: item.value,
            itemStyle: { color: item.color }
          }))
        }
      ]
    };
  };

  // ECharts Options: Live Timeline 30 Days
  const getTimelineOption = () => {
    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 }
      },
      legend: {
        data: ['SAFE', 'WATCHLIST', 'SUSPICIOUS', 'CRITICAL'],
        top: 0,
        icon: 'circle',
        textStyle: { color: '#475569', fontWeight: 600, fontSize: 11 }
      },
      grid: {
        left: '2%',
        right: '2%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: riskTimeline.map(item => item.date),
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        axisLabel: { color: '#64748b' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f1f5f9' } },
        axisLabel: { color: '#64748b' }
      },
      series: [
        {
          name: 'SAFE',
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3 },
          color: '#10B981',
          data: riskTimeline.map(item => item.safe)
        },
        {
          name: 'WATCHLIST',
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3 },
          color: '#F59E0B',
          data: riskTimeline.map(item => item.watchlist)
        },
        {
          name: 'SUSPICIOUS',
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3 },
          color: '#8B5CF6',
          data: riskTimeline.map(item => item.suspicious)
        },
        {
          name: 'CRITICAL',
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 3 },
          color: '#EF4444',
          data: riskTimeline.map(item => item.critical)
        }
      ]
    };
  };

  const activeInsight = insights[insightIndex];

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">National Fraud Command Center</h1>
          <p className="page-subtitle">Unified dashboard of surveillance nodes and banking telemetry feeds.</p>
        </div>
        
        <div className="flex gap-12">
          <button className="btn btn-secondary btn-sm" onClick={fetchData}>
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span>Refresh Feeds</span>
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/alert-center')}>
            <span>View Alerts Queue</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '70vh' }}>
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
          <span className="text-label" style={{ marginTop: '16px' }}>Decrypting streams...</span>
        </div>
      ) : (
        <div className="dashboard-grid flex flex-col gap-24 w-full">
          {/* KPI Dashboard Ribbon */}
          <div className="grid-4 w-full">
            {kpis.slice(0, 4).map((kpi) => (
              <KPICard
                key={kpi.id}
                label={kpi.label}
                value={kpi.value.toLocaleString('en-IN')}
                trend={kpi.trend}
                trendDir={kpi.trendDir}
                iconName={kpi.icon}
                color={kpi.color}
                pulse={kpi.pulse}
                sparklineData={kpi.sparkline}
              />
            ))}
          </div>

          <div className="grid-4 w-full">
            {kpis.slice(4, 8).map((kpi) => (
              <KPICard
                key={kpi.id}
                label={kpi.label}
                value={kpi.formatted || kpi.value.toLocaleString('en-IN')}
                trend={kpi.trend}
                trendDir={kpi.trendDir}
                iconName={kpi.icon}
                color={kpi.color}
                pulse={kpi.pulse}
                sparklineData={kpi.sparkline}
              />
            ))}
          </div>

          {/* AI Insights & Main Chart Layout */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.2fr 1.8fr' }}>
            {/* Donut and AI Insights */}
            <div className="flex flex-col gap-20 h-full">
              {/* Donut Distribution Card */}
              <div className="card h-full flex flex-col justify-between" style={{ minHeight: '230px' }}>
                <h3 className="text-h3 font-display">Risk Distribution</h3>
                <div style={{ flex: 1, marginTop: '12px' }}>
                  <ReactECharts option={getDonutOption()} style={{ height: '100%', width: '100%' }} />
                </div>
              </div>

              {/* Dynamic Copilot Insights Feed */}
              {activeInsight && (
                <div className="card ai-insights-card bg-primary-light flex flex-col justify-between" style={{ border: '1.5px solid rgba(37,99,235,0.15)', minHeight: '160px' }}>
                  <div className="flex justify-between items-center w-full">
                    <span className="flex items-center gap-8 text-label text-gradient">
                      <Bot size={16} className="text-primary" />
                      <span>Copilot Intel Feed</span>
                    </span>
                    <span className="text-label" style={{ fontSize: '10px', textTransform: 'none' }}>
                      {activeInsight.time}
                    </span>
                  </div>
                  <div className="insight-body" style={{ margin: '12px 0' }}>
                    <h4 className="text-h3" style={{ fontSize: '15px', color: 'var(--primary-dark)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <AlertTriangle size={14} className={activeInsight.type === 'critical' ? 'text-critical' : 'text-warning'} />
                      {activeInsight.title}
                    </h4>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: '1.4' }}>
                      {activeInsight.description}
                    </p>
                  </div>
                  <div className="flex justify-between items-center w-full">
                    <button className="btn btn-ghost btn-sm btn-insight-action" onClick={() => navigate('/alert-center')}>
                      {activeInsight.action}
                    </button>
                    <span className="insight-dot-indicator flex gap-4">
                      {insights.map((_, i) => (
                        <span key={i} className={`dot ${i === insightIndex ? 'active' : ''}`}></span>
                      ))}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Risk Timeline Line Chart */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '410px' }}>
              <div className="flex justify-between items-center w-full">
                <div>
                  <h3 className="text-h3 font-display">Live Risk Timeline</h3>
                  <span className="text-label" style={{ fontSize: '10px' }}>30-day tracking of account classification waves</span>
                </div>
                <div className="timeline-badge-label font-mono">
                  ACTIVE SURVEILLANCE
                </div>
              </div>
              <div style={{ flex: 1, marginTop: '24px' }}>
                <ReactECharts option={getTimelineOption()} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>
          </div>

          {/* Regional Geo Risk & High Risk Account Table */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.8fr 1.2fr' }}>
            {/* Account table */}
            <div className="card flex flex-col gap-16">
              <div className="flex justify-between items-center w-full">
                <div>
                  <h3 className="text-h3 font-display">High-Risk Accounts</h3>
                  <span className="text-label" style={{ fontSize: '10px' }}>Top accounts currently flagged for immediate audit</span>
                </div>
                <button className="btn btn-ghost btn-sm" onClick={() => navigate('/account-intel')}>
                  All Profiles
                </button>
              </div>
              <AccountTable accounts={highRiskAccounts} limit={5} />
            </div>

            {/* Indian Regional Heatmap Card */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '400px' }}>
              <div>
                <h3 className="text-h3 font-display">Geographic Risk (India)</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>States ranked by active fraud density index</span>
              </div>
              
              <div className="geo-state-list" style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>
                {geoRisk.slice(0, 6).map((item, index) => (
                  <div key={item.state} className="geo-state-item flex flex-col gap-4">
                    <div className="flex justify-between items-center w-full text-data" style={{ fontSize: '12px' }}>
                      <span style={{ fontWeight: 600 }}>{index + 1}. {item.state}</span>
                      <span className="text-muted">{item.accounts.toLocaleString('en-IN')} cases ({item.risk} index)</span>
                    </div>
                    <div className="progress-bar w-full" style={{ height: '8px' }}>
                      <div 
                        className="progress-bar__fill" 
                        style={{ 
                          width: `${item.risk}%`, 
                          backgroundColor: item.risk > 70 ? 'var(--critical)' : item.risk > 50 ? 'var(--warning)' : 'var(--primary)' 
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .timeline-badge-label {
          background: rgba(37,99,235,0.08);
          border: 1px solid rgba(37,99,235,0.15);
          color: var(--primary);
          font-size: 11px;
          font-weight: 700;
          padding: 4px 10px;
          border-radius: 4px;
        }

        .ai-insights-card {
          padding: 16px 20px;
        }

        .insight-dot-indicator .dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: rgba(37,99,235,0.2);
          display: inline-block;
          transition: background 0.3s ease;
        }

        .insight-dot-indicator .dot.active {
          background: var(--primary);
        }

        .btn-insight-action {
          border-color: rgba(37,99,235,0.2) !important;
          color: var(--primary) !important;
          background: transparent !important;
        }
        .btn-insight-action:hover {
          background: var(--primary-light) !important;
          border-color: var(--primary) !important;
        }

        .geo-state-item {
          padding: 4px 0;
        }
      `}</style>
    </AppLayout>
  );
}
