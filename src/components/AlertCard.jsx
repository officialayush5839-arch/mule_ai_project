import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Clock, CheckCircle2, ShieldAlert, Ban, Eye, Search } from 'lucide-react';
import RiskBadge from './RiskBadge';
import { timeAgo } from '../lib/utils';

export default function AlertCard({ alert, onAction }) {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);

  const getPriorityColor = (p) => {
    switch (p) {
      case 'CRITICAL': return '#EF4444';
      case 'HIGH': return '#F59E0B';
      case 'MEDIUM': return '#8B5CF6';
      default: return '#3B82F6';
    }
  };

  const getPriorityBg = (p) => {
    switch (p) {
      case 'CRITICAL': return '#FEF2F2';
      case 'HIGH': return '#FFFBEB';
      case 'MEDIUM': return '#F5F3FF';
      default: return '#EFF6FF';
    }
  };

  const handleAction = async (actionType) => {
    setIsProcessing(true);
    if (onAction) {
      await onAction(alert.id, actionType);
    }
    setIsProcessing(false);
  };

  const priorityColor = getPriorityColor(alert.priority);
  const priorityBg = getPriorityBg(alert.priority);

  return (
    <div className={`card alert-card ${alert.status !== 'active' ? 'processed' : ''}`} style={{ borderLeft: `6px solid ${priorityColor}` }}>
      <div className="alert-header flex justify-between items-center w-full">
        <div className="flex items-center gap-12">
          <span className="alert-priority-badge font-mono" style={{ color: priorityColor, backgroundColor: priorityBg }}>
            {alert.priority}
          </span>
          <span className="font-mono text-label">{alert.id}</span>
        </div>
        <div className="flex items-center gap-8 text-muted text-label" style={{ textTransform: 'none' }}>
          <Clock size={12} />
          <span>{timeAgo(alert.timestamp)}</span>
        </div>
      </div>

      <div className="alert-body w-full">
        <div className="flex justify-between items-start w-full alert-acc-row">
          <div>
            <h4 className="alert-title">Account Breach: <span className="font-mono text-primary cursor-pointer" onClick={() => navigate(`/account-intel?id=${alert.accountId}`)}>{alert.accountId}</span></h4>
            <p className="alert-trigger-desc">{alert.trigger}</p>
          </div>
          <div className="text-right">
            <span className="font-mono block text-metric" style={{ fontSize: '20px', lineHeight: 1 }}>{alert.riskScore}</span>
            <span className="text-label" style={{ fontSize: '9px' }}>Risk Score</span>
          </div>
        </div>

        {alert.evidence && alert.evidence.length > 0 && (
          <div className="alert-evidence-section">
            <span className="text-label" style={{ fontSize: '10px' }}>Evidence / Anomaly Points:</span>
            <ul className="evidence-list">
              {alert.evidence.map((ev, idx) => (
                <li key={idx} className="evidence-item flex items-start gap-8">
                  <ShieldAlert size={12} className="text-muted" style={{ marginTop: '4px', flexShrink: 0 }} />
                  <span>{ev}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="alert-footer flex justify-between items-center w-full">
        <div className="flex gap-8">
          <button 
            className="btn btn-secondary btn-sm"
            onClick={() => navigate(`/account-intel?id=${alert.accountId}`)}
          >
            <Eye size={12} /> View Intel
          </button>
          <button 
            className="btn btn-secondary btn-sm"
            onClick={() => navigate(`/copilot?query=Analyze alert ${alert.id} for account ${alert.accountId}`)}
          >
            <Search size={12} /> AI Copilot
          </button>
        </div>

        {alert.status === 'active' ? (
          <div className="flex gap-8">
            <button 
              className="btn btn-ghost btn-sm text-green hover-green"
              disabled={isProcessing}
              onClick={() => handleAction('monitor')}
            >
              <CheckCircle2 size={12} /> Monitor
            </button>
            <button 
              className="btn btn-danger btn-sm"
              disabled={isProcessing}
              style={{ background: 'linear-gradient(135deg, #EF4444, #DC2626)' }}
              onClick={() => handleAction('freeze')}
            >
              <Ban size={12} /> Freeze Account
            </button>
          </div>
        ) : (
          <span className="alert-resolved-badge">
            <CheckCircle2 size={14} className="text-accent" />
            <span>Processed ({alert.status})</span>
          </span>
        )}
      </div>

      <style>{`
        .alert-card {
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 16px;
          transition: opacity 0.3s ease, transform 0.2s ease;
        }

        .alert-card.processed {
          opacity: 0.65;
          pointer-events: none;
        }

        .alert-priority-badge {
          font-size: 11px;
          font-weight: 700;
          padding: 2px 8px;
          border-radius: 4px;
        }

        .alert-title {
          font-size: 15px;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .alert-trigger-desc {
          font-size: 13px;
          color: var(--text-secondary);
          line-height: 1.4;
        }

        .alert-acc-row {
          margin-top: 8px;
        }

        .alert-evidence-section {
          background: var(--surface-2);
          border-radius: var(--radius-sm);
          padding: 12px;
          margin-top: 12px;
        }

        .evidence-list {
          list-style: none;
          margin-top: 6px;
          padding-left: 0;
        }

        .evidence-item {
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 4px;
          line-height: 1.4;
        }

        .alert-footer {
          border-top: 1px solid var(--border);
          padding-top: 12px;
          margin-top: 4px;
        }

        .hover-green:hover {
          color: #059669 !important;
          border-color: #059669 !important;
          background: #ECFDF5 !important;
        }

        .alert-resolved-badge {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          font-weight: 600;
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  );
}
