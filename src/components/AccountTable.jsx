import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUpDown, Eye, Search, AlertOctagon } from 'lucide-react';
import RiskBadge from './RiskBadge';
import { formatScore, getRiskColor, getRiskBg } from '../lib/utils';

export default function AccountTable({ accounts = [], limit = null }) {
  const navigate = useNavigate();
  const [sortField, setSortField] = useState('riskScore');
  const [sortOrder, setSortOrder] = useState('desc');

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc'); // default sort desc
    }
  };

  const sortedAccounts = [...accounts].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];

    if (typeof aVal === 'string') {
      return sortOrder === 'asc' 
        ? aVal.localeCompare(bVal) 
        : bVal.localeCompare(aVal);
    }
    
    // Numbers
    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
  });

  const displayAccounts = limit ? sortedAccounts.slice(0, limit) : sortedAccounts;

  return (
    <div className="table-responsive">
      <table className="data-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('id')}>
              Account ID <ArrowUpDown size={12} className="sort-icon" />
            </th>
            <th onClick={() => handleSort('name')}>
              Holder Name <ArrowUpDown size={12} className="sort-icon" />
            </th>
            <th onClick={() => handleSort('riskScore')} className="text-right">
              Risk Score <ArrowUpDown size={12} className="sort-icon" />
            </th>
            <th>Risk Classification</th>
            <th onClick={() => handleSort('confidence')} className="text-right">
              Confidence <ArrowUpDown size={12} className="sort-icon" />
            </th>
            <th onClick={() => handleSort('trustScore')} className="text-right">
              Trust Score <ArrowUpDown size={12} className="sort-icon" />
            </th>
            <th>Branch</th>
            <th className="text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          {displayAccounts.map((account) => {
            const riskColor = getRiskColor(account.classification);
            return (
              <tr key={account.id} className="table-row-interactive">
                <td className="col-mono">{account.id}</td>
                <td style={{ fontWeight: 600 }}>{account.name}</td>
                <td className="text-right">
                  <div className="flex flex-col items-end gap-4">
                    <span className="font-mono font-bold" style={{ color: riskColor }}>
                      {formatScore(account.riskScore)}
                    </span>
                    <div className="progress-bar" style={{ width: '80px' }}>
                      <div 
                        className="progress-bar__fill" 
                        style={{ 
                          width: `${account.riskScore}%`,
                          backgroundColor: riskColor
                        }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td>
                  <RiskBadge classification={account.classification} />
                </td>
                <td className="text-right font-mono">{account.confidence}%</td>
                <td className="text-right">
                  <div className="flex flex-col items-end gap-4">
                    <span className="font-mono">{account.trustScore}</span>
                    <div className="progress-bar" style={{ width: '60px' }}>
                      <div 
                        className="progress-bar__fill" 
                        style={{ 
                          width: `${account.trustScore}%`,
                          backgroundColor: '#10B981'
                        }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  {account.branch}
                </td>
                <td className="text-center">
                  <div className="flex justify-center gap-8">
                    <button 
                      className="btn-icon btn-sm tooltip" 
                      data-tooltip="View Account Intel"
                      onClick={() => navigate(`/account-intel?id=${account.id}`)}
                    >
                      <Eye size={14} />
                    </button>
                    <button 
                      className="btn-icon btn-sm tooltip" 
                      data-tooltip="Chat in AI Copilot"
                      onClick={() => navigate(`/copilot?query=Analyze account ${account.id}`)}
                    >
                      <Search size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <style>{`
        .table-responsive {
          width: 100%;
          overflow-x: auto;
          border-radius: var(--radius-lg);
          border: 1px solid var(--border);
          background: var(--surface);
        }

        .table-row-interactive {
          cursor: pointer;
        }

        .sort-icon {
          display: inline-block;
          margin-left: 4px;
          vertical-align: middle;
          opacity: 0.5;
        }

        th:hover .sort-icon {
          opacity: 1;
        }
      `}</style>
    </div>
  );
}
