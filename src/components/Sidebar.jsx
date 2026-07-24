import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Bell, 
  Search, 
  Binary, 
  Sparkles, 
  TrendingUp, 
  GitFork, 
  MessageSquareText, 
  LineChart,
  Home,
  ChevronRight,
  LogOut
} from 'lucide-react';
import './Sidebar.css';

export default function Sidebar() {
  const [isExpanded, setIsExpanded] = useState(false);

  const menuItems = [
    { path: '/command-center', name: 'Command Center', icon: LayoutDashboard },
    { path: '/alert-center', name: 'Alert Center', icon: Bell },
    { path: '/account-intel', name: 'Account Intel', icon: Search },
    { path: '/anomaly-lab', name: 'Anomaly Lab', icon: Binary },
    { path: '/explainable-ai', name: 'Explainable AI', icon: Sparkles },
    { path: '/risk-engine', name: 'Risk Engine', icon: TrendingUp },
    { path: '/pattern-discovery', name: 'Pattern Discovery', icon: GitFork },
    { path: '/copilot', name: 'AI Copilot', icon: MessageSquareText },
    { path: '/model-intel', name: 'Model Intel', icon: LineChart },
  ];

  return (
    <aside 
      className={`sidebar ${isExpanded ? 'expanded' : ''}`}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      <div className="sidebar-header">
        <div className="logo-section">
          <div className="logo-icon-container">
            <div className="logo-dot"></div>
          </div>
          {isExpanded && <span className="logo-name">MULENET <span className="logo-version">AI</span></span>}
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink 
          to="/" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          end
        >
          <Home size={20} className="nav-icon" />
          {isExpanded && <span className="nav-label">Portal Home</span>}
        </NavLink>

        <div className="nav-divider"></div>

        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} className="nav-icon" />
              {isExpanded && <span className="nav-label">{item.name}</span>}
              {!isExpanded && (
                <div className="sidebar-tooltip">
                  {item.name}
                </div>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="nav-divider"></div>
        <div className="analyst-info">
          <div className="analyst-avatar">AS</div>
          {isExpanded && (
            <div className="analyst-details">
              <span className="analyst-name">Ayush S.</span>
              <span className="analyst-role">Lead FIU Analyst</span>
            </div>
          )}
        </div>
        <NavLink to="/" className="nav-item logout-btn">
          <LogOut size={20} className="nav-icon" />
          {isExpanded && <span className="nav-label">Logout</span>}
        </NavLink>
      </div>
    </aside>
  );
}
