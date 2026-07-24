import React from 'react';
import * as LucideIcons from 'lucide-react';

export default function KPICard({ 
  label, 
  value, 
  trend, 
  trendDir = 'up', 
  iconName, 
  color = 'primary', 
  pulse = false,
  sparklineData = [] 
}) {
  // Get corresponding Lucide Icon by name
  const Icon = LucideIcons[iconName] || LucideIcons.Activity;

  // Determine classes
  const isUp = trendDir === 'up';
  const trendClass = isUp ? 'trend-up' : 'trend-down';
  const colorClass = color ? `kpi-card--${color}` : '';
  const pulseClass = pulse ? 'kpi-card--pulse' : '';

  // Generate SVG path for sparkline
  const generateSparklinePath = () => {
    if (!sparklineData || sparklineData.length < 2) return '';
    const width = 80;
    const height = 24;
    const padding = 2;
    const minVal = Math.min(...sparklineData);
    const maxVal = Math.max(...sparklineData);
    const valRange = maxVal - minVal || 1;

    const points = sparklineData.map((val, idx) => {
      const x = (idx / (sparklineData.length - 1)) * (width - padding * 2) + padding;
      const y = height - ((val - minVal) / valRange) * (height - padding * 2) - padding;
      return `${x},${y}`;
    });

    return `M ${points.join(' L ')}`;
  };

  return (
    <div className={`card kpi-card ${colorClass} ${pulseClass}`}>
      <div className="kpi-card__header flex justify-between items-center w-full">
        <span className="text-label truncate">{label}</span>
        <div className="kpi-card__icon-container">
          <Icon size={18} className="kpi-icon" />
        </div>
      </div>

      <div className="kpi-card__body flex items-end justify-between w-full">
        <div className="flex flex-col gap-4">
          <span className="text-metric">{value}</span>
          <div className="flex items-center gap-8">
            <span className={`trend-badge ${trendClass}`}>
              {trend}
            </span>
            <span className="text-label" style={{ textTransform: 'none', fontSize: '10px' }}>
              vs last week
            </span>
          </div>
        </div>

        {/* Dynamic SVG Sparkline */}
        {sparklineData && sparklineData.length > 0 && (
          <div className="kpi-sparkline">
            <svg width="80" height="24">
              <path
                d={generateSparklinePath()}
                fill="none"
                stroke={isUp ? '#10B981' : '#EF4444'}
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )}
      </div>

      <style>{`
        .kpi-card {
          position: relative;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .kpi-card__icon-container {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: var(--surface-2);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--text-secondary);
        }

        .kpi-card--warning .kpi-card__icon-container {
          background: var(--watchlist-bg);
          color: var(--warning);
        }

        .kpi-card--critical .kpi-card__icon-container {
          background: var(--critical-bg);
          color: var(--critical);
        }

        .kpi-card--accent .kpi-card__icon-container {
          background: var(--safe-bg);
          color: var(--accent);
        }

        .trend-badge {
          font-size: 11px;
          font-weight: 700;
          font-family: 'JetBrains Mono', monospace;
          padding: 2px 6px;
          border-radius: 4px;
        }

        .trend-up {
          background: var(--safe-bg);
          color: #059669;
        }

        .trend-down {
          background: var(--critical-bg);
          color: #DC2626;
        }

        .kpi-card--pulse::before {
          content: '';
          position: absolute;
          top: 0;
          right: 0;
          width: 8px;
          height: 8px;
          background-color: var(--critical);
          border-radius: 50%;
          margin-top: 10px;
          margin-right: 10px;
          animation: pulse-red 1.5s ease-in-out infinite;
        }

        .kpi-sparkline {
          opacity: 0.8;
        }
      `}</style>
    </div>
  );
}
