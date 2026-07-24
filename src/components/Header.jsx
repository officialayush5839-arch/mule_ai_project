import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, Shield, Network, Activity, Database, Upload, RefreshCw, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import './Header.css';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [activeSource, setActiveSource] = useState(api.getActiveSource());
  const [isProcessing, setIsProcessing] = useState(false);
  
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleSourceChange = () => {
      setActiveSource(api.getActiveSource());
    };
    window.addEventListener('datasource-changed', handleSourceChange);
    return () => window.removeEventListener('datasource-changed', handleSourceChange);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    // Normalize format
    let query = searchQuery.trim().toUpperCase();
    if (query.startsWith('ACC-') || query.length >= 6) {
      if (!query.startsWith('ACC-') && /^\d+$/.test(query)) {
        query = `ACC-${query}`;
      }
      navigate(`/account-intel?id=${query}`);
    } else {
      // generic lookup, go to account intel list
      navigate(`/account-intel?search=${query}`);
    }
    setSearchQuery('');
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      alert("Invalid file format. Please upload a standard CSV file.");
      return;
    }

    setIsProcessing(true);
    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        await api.processCustomCSV(event.target.result, file.name);
      } catch (err) {
        alert("Failed to parse custom CSV dataset: " + err.message);
      } finally {
        setIsProcessing(false);
      }
    };
    reader.readAsText(file);
  };

  const handleReset = () => {
    if (window.confirm("Are you sure you want to restore the default sandbox dataset?")) {
      api.resetToMock();
    }
  };

  const mockNotifications = [
    { id: 1, title: 'Critical Mule Spike', desc: '17 accounts triggered velocity anomalies', time: '2m ago', read: false },
    { id: 2, title: 'Freeze Requested', desc: 'ACC-847291 pending FIU escalation approval', time: '15m ago', read: false },
    { id: 3, title: 'Concept Drift Alert', desc: 'Model performance monitored: stable (96.4%)', time: '2h ago', read: true }
  ];

  return (
    <header className="header">
      <form className="header-search-form" onSubmit={handleSearch}>
        <div className="input-with-icon">
          <Search size={18} className="input-icon" />
          <input 
            type="text" 
            placeholder="Search accounts (e.g., ACC-847291), alert codes..." 
            className="input search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </form>

      <div className="header-actions">
        {/* Dynamic Data Ingestion Node */}
        <div className="data-source-widget flex items-center gap-8 bg-surface-2" style={{ padding: '4px 10px', borderRadius: '10px', border: '1px solid var(--border)' }}>
          <Database size={15} className={activeSource === 'custom' ? 'text-primary' : 'text-muted'} />
          
          <div className="flex flex-col text-left" style={{ lineHeight: '1.1' }}>
            <span className="text-label" style={{ fontSize: '8px', padding: 0 }}>Active Node DB</span>
            <span className="font-mono text-data" style={{ fontSize: '11px', fontWeight: 700, color: activeSource === 'custom' ? 'var(--primary)' : 'var(--text-secondary)' }}>
              {activeSource === 'custom' ? 'Uploaded CSV' : 'Sandbox (Mock)'}
            </span>
          </div>

          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            accept=".csv"
            onChange={handleFileUpload}
          />

          {isProcessing ? (
            <div className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px', marginLeft: '4px' }}></div>
          ) : activeSource === 'custom' ? (
            <button 
              className="btn-icon btn-sm text-critical" 
              style={{ padding: '4px', border: 'none', background: 'transparent', cursor: 'pointer' }}
              onClick={handleReset}
              title="Reset to Sandbox data"
            >
              <XCircle size={15} />
            </button>
          ) : (
            <button 
              className="btn btn-primary btn-sm flex items-center gap-4" 
              style={{ padding: '4px 8px', fontSize: '10px', height: '24px', borderRadius: '6px', marginLeft: '6px' }}
              onClick={handleFileSelect}
              title="Upload custom database CSV"
            >
              <Upload size={10} />
              <span>Upload CSV</span>
            </button>
          )}
        </div>

        {/* System Health Widget */}
        <div className="system-health">
          <span className="health-dot"></span>
          <span className="health-text">ML PIPELINE: ACTIVE (96.4%)</span>
        </div>

        {/* Notifications */}
        <div className="notification-wrapper">
          <button 
            className="btn-action-icon tooltip" 
            data-tooltip="Alert Center notifications"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell size={18} />
            <span className="notification-badge"></span>
          </button>
          
          {showNotifications && (
            <div className="notification-dropdown animate-fade-in">
              <div className="dropdown-header">
                <h3>Notifications</h3>
                <span className="mark-read">Mark all read</span>
              </div>
              <div className="dropdown-items">
                {mockNotifications.map(n => (
                  <div key={n.id} className={`dropdown-item ${!n.read ? 'unread' : ''}`}>
                    <div className="item-title-row">
                      <span className="item-title">{n.title}</span>
                      <span className="item-time">{n.time}</span>
                    </div>
                    <p className="item-desc">{n.desc}</p>
                  </div>
                ))}
              </div>
              <div className="dropdown-footer" onClick={() => { setShowNotifications(false); navigate('/alert-center'); }}>
                View all in Alert Center
              </div>
            </div>
          )}
        </div>

        {/* User Session Profile */}
        <div className="user-profile">
          <div className="profile-text">
            <span className="profile-name">Ayush S.</span>
            <span className="profile-role">Lead Analyst</span>
          </div>
          <div className="profile-avatar">AS</div>
        </div>
      </div>
    </header>
  );
}
