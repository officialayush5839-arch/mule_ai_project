import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, 
  Search, 
  Filter, 
  Download, 
  CheckCircle, 
  RefreshCw,
  AlertOctagon,
  FileCheck
} from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';
import AlertCard from '../components/AlertCard';

export default function AlertCenter() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);
  
  // Filters
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts();
      setAlerts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();

    const handleDataChange = () => {
      loadAlerts();
    };
    window.addEventListener('datasource-changed', handleDataChange);
    return () => window.removeEventListener('datasource-changed', handleDataChange);
  }, []);

  const handleAction = async (alertId, actionType) => {
    try {
      const res = await api.actionAlert(alertId, actionType);
      if (res.success) {
        // Update alert item state locally
        setAlerts(prev => prev.map(a => {
          if (a.id === alertId) {
            return { 
              ...a, 
              status: actionType === 'monitor' ? 'monitored' : 'frozen',
              actionTaken: actionType
            };
          }
          return a;
        }));
      }
    } catch (e) {
      console.error("Alert action failed", e);
    }
  };

  // Filter logic
  const filteredAlerts = alerts.filter(a => {
    const matchesPriority = priorityFilter === 'ALL' || a.priority === priorityFilter;
    const matchesStatus = statusFilter === 'ALL' || 
      (statusFilter === 'ACTIVE' && a.status === 'active') || 
      (statusFilter === 'PROCESSED' && a.status !== 'active');
    
    const query = searchQuery.toLowerCase().trim();
    const matchesSearch = !query || 
      a.id.toLowerCase().includes(query) || 
      a.accountId.toLowerCase().includes(query) || 
      a.trigger.toLowerCase().includes(query);

    return matchesPriority && matchesStatus && matchesSearch;
  });

  // Export to CSV utility
  const exportCSV = () => {
    if (filteredAlerts.length === 0) return;
    
    const headers = ['Alert ID', 'Account ID', 'Priority', 'Status', 'Risk Score', 'Confidence', 'Trigger'];
    const rows = filteredAlerts.map(a => [
      a.id, 
      a.accountId, 
      a.priority, 
      a.status, 
      a.riskScore, 
      a.confidence, 
      `"${a.trigger.replace(/"/g, '""')}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `mulenet_alerts_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">Surveillance Alert Queue</h1>
          <p className="page-subtitle">Real-time listing of active risk breaches and neural network anomalies.</p>
        </div>

        <div className="flex gap-12">
          <button className="btn btn-secondary btn-sm" onClick={loadAlerts}>
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span>Sync Live Queue</span>
          </button>
          <button className="btn btn-primary btn-sm" disabled={filteredAlerts.length === 0} onClick={exportCSV}>
            <Download size={14} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-20 w-full">
        {/* Filter Toolbar Ribbon */}
        <div className="card filter-toolbar flex flex-wrap justify-between items-center gap-16 w-full" style={{ padding: '16px 24px' }}>
          <div className="flex items-center gap-16 flex-wrap">
            {/* Search Input */}
            <div className="input-with-icon" style={{ width: '260px' }}>
              <Search size={16} className="input-icon" />
              <input 
                type="text" 
                placeholder="Search alert, account, key terms..." 
                className="input"
                style={{ padding: '6px 12px 6px 36px' }}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Priority Selector */}
            <div className="flex items-center gap-8">
              <span className="text-label" style={{ fontSize: '10px' }}>Priority:</span>
              <select 
                className="input" 
                style={{ width: '120px', padding: '6px 10px' }}
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
              >
                <option value="ALL">All Priorities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>

            {/* Status Selector */}
            <div className="flex items-center gap-8">
              <span className="text-label" style={{ fontSize: '10px' }}>Status:</span>
              <select 
                className="input" 
                style={{ width: '130px', padding: '6px 10px' }}
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">All Statuses</option>
                <option value="ACTIVE">Active Alerts</option>
                <option value="PROCESSED">Processed</option>
              </select>
            </div>
          </div>

          <div className="text-label font-mono text-right" style={{ fontSize: '10px' }}>
            MATCHED FLAGS: {filteredAlerts.length}
          </div>
        </div>

        {/* Loading and Results Lists */}
        {loading ? (
          <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '50vh' }}>
            <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
            <span className="text-label" style={{ marginTop: '16px' }}>Decrypting active signals...</span>
          </div>
        ) : filteredAlerts.length > 0 ? (
          <div className="alerts-card-list flex flex-col gap-16 w-full">
            {filteredAlerts.map(alert => (
              <AlertCard 
                key={alert.id} 
                alert={alert} 
                onAction={handleAction} 
              />
            ))}
          </div>
        ) : (
          <div className="card text-center" style={{ padding: '60px' }}>
            <AlertOctagon size={48} className="text-muted" style={{ margin: '0 auto 16px' }} />
            <h3 className="text-h3">No Alerts Matched Selected Criteria</h3>
            <p className="text-muted" style={{ margin: '8px 0 20px' }}>Adjust filters or lookup search query to locate alerts.</p>
          </div>
        )}
      </div>

      <style>{`
        .filter-toolbar {
          background: rgba(255,255,255,0.7);
        }
      `}</style>
    </AppLayout>
  );
}
