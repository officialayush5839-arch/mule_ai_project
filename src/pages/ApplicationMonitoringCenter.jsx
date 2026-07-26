import React, { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import { Activity, Clock, Server, AlertCircle, RefreshCw, Terminal, Search } from 'lucide-react';
import './ApplicationMonitoringCenter.css';

export default function ApplicationMonitoringCenter() {
  const [activeTab, setActiveTab] = useState('traces');
  const [traces, setTraces] = useState([]);
  const [logs, setLogs] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMonitoringData = async () => {
    try {
      const [tracesRes, logsRes, servicesRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/monitoring/traces'),
        fetch('http://127.0.0.1:8000/api/monitoring/logs'),
        fetch('http://127.0.0.1:8000/api/monitoring/services')
      ]);
      const tracesData = await tracesRes.json();
      const logsData = await logsRes.json();
      const servicesData = await servicesRes.json();
      
      setTraces(tracesData.traces || []);
      setLogs(logsData.logs || []);
      setServices(servicesData.services || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonitoringData();
    const int = setInterval(fetchMonitoringData, 5000);
    return () => clearInterval(int);
  }, []);

  return (
    <AppLayout>
      <div className="monitoring-center">
        <header className="monitoring-header">
          <div>
            <h1>Application Monitoring Center</h1>
            <p className="text-muted">In-house Enterprise APM, Tracing, and Logging</p>
          </div>
          <button className="btn btn-primary" onClick={fetchMonitoringData}>
            <RefreshCw size={16} /> Refresh
          </button>
        </header>

        <div className="monitoring-tabs">
          <button className={activeTab === 'traces' ? 'active' : ''} onClick={() => setActiveTab('traces')}>
            <Activity size={16} /> Trace Explorer
          </button>
          <button className={activeTab === 'services' ? 'active' : ''} onClick={() => setActiveTab('services')}>
            <Server size={16} /> Services Health
          </button>
          <button className={activeTab === 'logs' ? 'active' : ''} onClick={() => setActiveTab('logs')}>
            <Terminal size={16} /> Application Logs
          </button>
        </div>

        <div className="monitoring-content">
          {activeTab === 'services' && (
            <div className="services-grid animate-fade-in">
              {services.map((s, i) => (
                <div key={i} className={`service-card ${s.status === 'Healthy' ? 'border-success' : 'border-critical'}`}>
                  <h3>{s.name}</h3>
                  <div className="service-meta">
                    <span className={`status-badge ${s.status === 'Healthy' ? 'bg-success' : 'bg-critical'}`}>
                      {s.status}
                    </span>
                    <span className="latency">{s.latency_ms} ms</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'traces' && (
            <div className="traces-table-container animate-fade-in">
              <table className="monitoring-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Method</th>
                    <th>Endpoint</th>
                    <th>Status</th>
                    <th>Duration (ms)</th>
                    <th>Trace ID</th>
                  </tr>
                </thead>
                <tbody>
                  {traces.length === 0 ? (
                    <tr><td colSpan="6" className="text-center">No traces recorded yet</td></tr>
                  ) : traces.map((t, i) => (
                    <tr key={i} className={t.status_code >= 400 ? 'error-row' : ''}>
                      <td>{new Date(t.timestamp * 1000).toLocaleTimeString()}</td>
                      <td><span className={`method-badge ${t.method.toLowerCase()}`}>{t.method}</span></td>
                      <td>{t.endpoint}</td>
                      <td>
                        <span className={t.status_code >= 400 ? 'text-critical' : 'text-success'}>
                          {t.status_code}
                        </span>
                      </td>
                      <td>{t.duration_ms}</td>
                      <td className="trace-id">{t.trace_id.split('-')[0]}...</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="logs-terminal animate-fade-in">
              {logs.length === 0 ? (
                <div className="text-muted text-center p-4">No logs collected in buffer</div>
              ) : logs.map((l, i) => (
                <div key={i} className="log-line">
                  <span className="log-time">[{new Date(l.timestamp * 1000).toISOString()}]</span>
                  <span className={`log-level ${l.level.toLowerCase()}`}>{l.level}</span>
                  <span className="log-msg">{l.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
