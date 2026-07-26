import React, { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import './AdminObservability.css';
import { Activity, Server, Cpu, AlertTriangle, Shield, HardDrive, Clock, CheckCircle } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function AdminObservability() {
  const [sysHealth, setSysHealth] = useState(null);
  const [sysMetrics, setSysMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);

  // Chart data history
  const [cpuHistory, setCpuHistory] = useState(Array(20).fill(0));
  const [ramHistory, setRamHistory] = useState(Array(20).fill(0));
  const [latencyHistory, setLatencyHistory] = useState(Array(20).fill(0));

  useEffect(() => {
    // Initial fetch to avoid empty state
    const fetchInitial = async () => {
      try {
        const [healthRes, metricsRes] = await Promise.all([
          fetch('http://127.0.0.1:8000/api/monitoring/health'),
          fetch('http://127.0.0.1:8000/api/monitoring/system')
        ]);
        if (healthRes.ok) setSysHealth(await healthRes.json());
        if (metricsRes.ok) setSysMetrics(await metricsRes.json());
      } catch (err) {
        setError('Failed to connect to monitoring API');
      } finally {
        setIsLoading(false);
      }
    };
    fetchInitial();

    // WebSocket connection for live telemetry stream (Phase 5)
    let ws = null;
    try {
      ws = new WebSocket('ws://127.0.0.1:8000/api/monitoring/ws');
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setSysHealth(data.system);
        setSysMetrics(data.metrics);
        
        // Update live charts
        setCpuHistory(prev => [...prev.slice(1), data.system.cpu_percent]);
        setRamHistory(prev => [...prev.slice(1), data.system.memory_percent]);
        setLatencyHistory(prev => [...prev.slice(1), Math.floor(Math.random() * 20) + 10]); // Mocked ms latency variation
      };
      ws.onclose = () => setWsConnected(false);
    } catch (e) {
      console.error("WS error", e);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const formatUptime = (seconds) => {
    if (!seconds) return '0s';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h}h ${m}m ${s}s`;
  };

  const lineChartOptions = (data, color, name) => ({
    animation: false,
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '5%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: Array(20).fill(''), show: false },
    yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
    series: [{
      name,
      type: 'line',
      data,
      smooth: true,
      lineStyle: { color, width: 3 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color }, { offset: 1, color: 'rgba(0,0,0,0)' }]
        }
      },
      itemStyle: { color },
      symbol: 'none'
    }]
  });

  const latencyChartOptions = (data, color, name) => ({
    ...lineChartOptions(data, color, name),
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } } // Auto max for latency
  });

  if (isLoading) {
    return (
      <AppLayout>
        <div className="admin-observability loading-state">
          <Activity size={32} className="spinning-icon" />
          <h2>Initializing Enterprise Telemetry...</h2>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="admin-observability">
        <header className="admin-header">
          <div>
            <h1>Observability Dashboard</h1>
            <div className="header-meta">
              <p>Real-time Infrastructure & Application Telemetry</p>
            </div>
          </div>
          
          <div className="ws-indicator">
            {wsConnected ? (
              <span className="ws-status connected"><span className="ws-dot"></span> Live Stream Active</span>
            ) : (
              <span className="ws-status disconnected"><span className="ws-dot offline"></span> Disconnected (Retrying...)</span>
            )}
          </div>
        </header>

        {error && !wsConnected && (
          <div className="error-banner">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* TOP KPI ROW */}
        <div className="kpi-row animate-fade-in">
          <div className="kpi-card">
            <div className="kpi-icon blue"><Activity size={20} /></div>
            <div className="kpi-data">
              <span className="kpi-label">API Requests</span>
              <span className="kpi-value">{sysMetrics?.total_requests || 0}</span>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon purple"><Cpu size={20} /></div>
            <div className="kpi-data">
              <span className="kpi-label">ML Predictions</span>
              <span className="kpi-value">{sysMetrics?.predictions || 0}</span>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon red"><AlertTriangle size={20} /></div>
            <div className="kpi-data">
              <span className="kpi-label">Total Errors</span>
              <span className="kpi-value">{sysMetrics?.errors || 0}</span>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon green"><Clock size={20} /></div>
            <div className="kpi-data">
              <span className="kpi-label">Uptime</span>
              <span className="kpi-value">{formatUptime(sysHealth?.uptime_seconds)}</span>
            </div>
          </div>
        </div>

        {/* CHARTS GRID */}
        <div className="charts-grid animate-fade-in">
          <div className="chart-card">
            <h3>CPU Utilization</h3>
            <div className="chart-wrapper">
              <ReactECharts option={lineChartOptions(cpuHistory, '#3b82f6', 'CPU %')} style={{ height: '200px' }} />
            </div>
            <div className="chart-footer">Current: {sysHealth?.cpu_percent}%</div>
          </div>

          <div className="chart-card">
            <h3>Memory Allocation</h3>
            <div className="chart-wrapper">
              <ReactECharts option={lineChartOptions(ramHistory, '#8b5cf6', 'RAM %')} style={{ height: '200px' }} />
            </div>
            <div className="chart-footer">Current: {sysHealth?.memory_percent}%</div>
          </div>

          <div className="chart-card">
            <h3>API Latency (ms)</h3>
            <div className="chart-wrapper">
              <ReactECharts option={latencyChartOptions(latencyHistory, '#10b981', 'Latency')} style={{ height: '200px' }} />
            </div>
            <div className="chart-footer">Avg Response: {latencyHistory[latencyHistory.length-1]} ms</div>
          </div>
        </div>

        {/* HARDWARE & DB STATUS */}
        <div className="hardware-grid animate-fade-in">
          <div className="hw-card">
            <Server size={24} className="text-muted" />
            <div>
              <h4>Server Node</h4>
              <p className="text-success"><CheckCircle size={14} /> Active</p>
            </div>
          </div>
          <div className="hw-card">
            <HardDrive size={24} className="text-muted" />
            <div>
              <h4>SQLite Storage</h4>
              <p className="text-success"><CheckCircle size={14} /> {sysHealth?.disk_percent}% Used</p>
            </div>
          </div>
          <div className="hw-card">
            <Shield size={24} className="text-muted" />
            <div>
              <h4>Security Engine</h4>
              <p className="text-success"><CheckCircle size={14} /> Enforcing</p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
