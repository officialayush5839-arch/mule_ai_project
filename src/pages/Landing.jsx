import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Activity, TrendingUp, Users, ArrowRight, Lock, Cpu, Layers } from 'lucide-react';
import { landingStats } from '../lib/mockData';
import { animateValue } from '../lib/utils';
import './Landing.css';

export default function Landing() {
  const canvasRef = useRef(null);
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    monitored: 0,
    suspicious: 0,
    nets: 0,
    prevented: 0
  });

  // Animated counters on load
  useEffect(() => {
    animateValue(0, landingStats[0].value, 1500, (v) => setStats(prev => ({ ...prev, monitored: v })));
    animateValue(0, landingStats[1].value, 1500, (v) => setStats(prev => ({ ...prev, suspicious: v })));
    animateValue(0, landingStats[2].value, 1500, (v) => setStats(prev => ({ ...prev, nets: v })));
    
    // Custom float animation for currency
    const rawCurrencyVal = 12.3;
    let currVal = 0;
    const interval = setInterval(() => {
      currVal += 0.4;
      if (currVal >= rawCurrencyVal) {
        currVal = rawCurrencyVal;
        clearInterval(interval);
      }
      setStats(prev => ({ ...prev, prevented: currVal.toFixed(1) }));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  // Network Simulation logic in Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Node Types
    const NODE_TYPES = {
      SAFE: { color: 'rgba(37, 99, 235, ', glow: 'rgba(37, 99, 235, 0.4)', radius: 4 },
      SUSPICIOUS: { color: 'rgba(139, 92, 246, ', glow: 'rgba(139, 92, 246, 0.5)', radius: 5.5 },
      CRITICAL: { color: 'rgba(239, 68, 68, ', glow: 'rgba(239, 68, 68, 0.7)', radius: 7 }
    };

    // Initialize 150 nodes
    const nodes = [];
    const nodeCount = 120;
    for (let i = 0; i < nodeCount; i++) {
      const typeRand = Math.random();
      let type = NODE_TYPES.SAFE;
      let label = 'SAFE';
      
      if (typeRand > 0.93) {
        type = NODE_TYPES.CRITICAL;
        label = 'CRITICAL';
      } else if (typeRand > 0.82) {
        type = NODE_TYPES.SUSPICIOUS;
        label = 'SUSPICIOUS';
      }

      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        type,
        label,
        pulseOffset: Math.random() * Math.PI * 2,
        connections: []
      });
    }

    // Connect nodes (edges)
    const edges = [];
    for (let i = 0; i < nodes.length; i++) {
      const neighbors = [];
      const connectionsCount = Math.floor(Math.random() * 2) + 1; // 1 to 2 edges per node average
      
      // Find nearest nodes
      const distances = nodes
        .map((n, idx) => ({ idx, dist: Math.hypot(n.x - nodes[i].x, n.y - nodes[i].y) }))
        .filter(item => item.idx !== i)
        .sort((a, b) => a.dist - b.dist);

      for (let c = 0; c < Math.min(connectionsCount, distances.length); c++) {
        const targetIdx = distances[c].idx;
        // Avoid duplicate edges
        if (!edges.some(e => (e.source === i && e.target === targetIdx) || (e.source === targetIdx && e.target === i))) {
          edges.push({
            source: i,
            target: targetIdx,
            dashOffset: Math.random() * 100,
            speed: 0.5 + Math.random() * 1.5
          });
        }
      }
    }

    // Parallax Mouse interaction
    let mouse = { x: null, y: null, active: false };
    const handleMouseMove = (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    };
    const handleMouseLeave = () => {
      mouse.active = false;
    };
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    let frame = 0;
    const render = () => {
      frame++;
      ctx.clearRect(0, 0, width, height);

      // Draw Edges with animated transaction flows
      edges.forEach((edge) => {
        const sourceNode = nodes[edge.source];
        const targetNode = nodes[edge.target];
        if (!sourceNode || !targetNode) return;

        // Distance check for edge fading
        const dist = Math.hypot(targetNode.x - sourceNode.x, targetNode.y - sourceNode.y);
        if (dist > 350) return; // Hide long lines

        const opacity = (1 - dist / 350) * 0.25;
        
        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);

        // Highlight paths linking suspicious/critical nodes
        if (sourceNode.label === 'CRITICAL' || targetNode.label === 'CRITICAL') {
          ctx.strokeStyle = `rgba(239, 68, 68, ${opacity * 1.5})`;
          ctx.lineWidth = 1.5;
        } else if (sourceNode.label === 'SUSPICIOUS' || targetNode.label === 'SUSPICIOUS') {
          ctx.strokeStyle = `rgba(139, 92, 246, ${opacity * 1.5})`;
          ctx.lineWidth = 1.2;
        } else {
          ctx.strokeStyle = `rgba(37, 99, 235, ${opacity})`;
          ctx.lineWidth = 0.8;
        }
        ctx.stroke();

        // Animated flow particles along the lines
        edge.dashOffset -= edge.speed;
        ctx.save();
        ctx.setLineDash([4, 16]);
        ctx.lineDashOffset = edge.dashOffset;
        if (sourceNode.label === 'CRITICAL' || targetNode.label === 'CRITICAL') {
          ctx.strokeStyle = 'rgba(239, 68, 68, 0.7)';
        } else {
          ctx.strokeStyle = 'rgba(59, 130, 246, 0.6)';
        }
        ctx.lineWidth = 2.0;
        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);
        ctx.stroke();
        ctx.restore();
      });

      // Render Nodes with custom styles and pulsing glow
      nodes.forEach((node) => {
        // Move nodes gently
        node.x += node.vx;
        node.y += node.vy;

        // Bounce on boundary
        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;

        // Mouse Parallax pull
        if (mouse.active) {
          const mDist = Math.hypot(mouse.x - node.x, mouse.y - node.y);
          if (mDist < 180) {
            const angle = Math.atan2(mouse.y - node.y, mouse.x - node.x);
            const force = (180 - mDist) * 0.03; // Pull factor
            node.x += Math.cos(angle) * force * -0.05;
            node.y += Math.sin(angle) * force * -0.05;
          }
        }

        const pulse = Math.sin(frame * 0.035 + node.pulseOffset);
        const currentRadius = node.type.radius + (node.label !== 'SAFE' ? pulse * 1.5 : 0);
        const alpha = node.label === 'SAFE' ? 0.6 : 0.8 + pulse * 0.2;

        // Glow
        if (node.label !== 'SAFE') {
          ctx.beginPath();
          ctx.arc(node.x, node.y, currentRadius * 3, 0, Math.PI * 2);
          ctx.fillStyle = node.type.glow;
          ctx.shadowBlur = 15;
          ctx.shadowColor = node.label === 'CRITICAL' ? '#EF4444' : '#8B5CF6';
          ctx.fill();
          ctx.shadowBlur = 0; // reset
        }

        // Core dot
        ctx.beginPath();
        ctx.arc(node.x, node.y, currentRadius, 0, Math.PI * 2);
        ctx.fillStyle = `${node.type.color}${alpha})`;
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <div className="landing-container">
      <canvas ref={canvasRef} className="landing-canvas" />

      {/* Floating Network Background Mesh grid */}
      <div className="mesh-overlay"></div>

      {/* Top Navigation */}
      <header className="landing-header">
        <div className="logo-container">
          <div className="logo-pulse"></div>
          <span className="logo-text">MULENET <span className="text-primary font-mono">AI</span></span>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/command-center')}>
            Access Platform
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="landing-hero">
        <div className="hero-content animate-fade-in-up">
          <div className="badge-announcement">
            <span className="badge-dot animate-pulse"></span>
            <span>BOI × IIT Hyderabad Hackathon 2026</span>
          </div>

          <h1 className="text-hero">
            Predict. Explain. Prevent. <br />
            <span className="gradient-title">Financial Crime Intelligence</span>
          </h1>

          <p className="hero-description">
            Transform raw, siloed transaction logs into interactive, explainable graph intelligence. 
            MuleNet AI integrates state-of-the-art stacking ensembles with SHAP explainer pipelines 
            specifically engineered for Indian public sector banking infrastructure.
          </p>

          <div className="cta-wrapper">
            <button className="btn btn-primary" onClick={() => navigate('/command-center')}>
              Launch Command Center <ArrowRight size={16} />
            </button>
            <a href="#features" className="btn btn-ghost">
              Explore Tech Stack
            </a>
          </div>
        </div>

        {/* Dynamic Interactive Stats Banner */}
        <section className="stats-banner animate-fade-in stagger-2">
          <div className="stat-card">
            <div className="stat-value font-mono">
              {stats.monitored.toLocaleString('en-IN')}
            </div>
            <div className="stat-label">Total Accounts Monitored</div>
          </div>
          <div className="stat-card border-accent">
            <div className="stat-value font-mono text-danger">
              {stats.suspicious.toLocaleString('en-IN')}
            </div>
            <div className="stat-label text-red">Critical/Suspicious Flagged</div>
          </div>
          <div className="stat-card">
            <div className="stat-value font-mono">
              {stats.nets}
            </div>
            <div className="stat-label">Coordinated Mule Clusters</div>
          </div>
          <div className="stat-card text-gradient">
            <div className="stat-value font-mono text-primary">
              ₹{stats.prevented} Cr
            </div>
            <div className="stat-label">Mule Losses Prevented</div>
          </div>
        </section>

        {/* Feature Grid */}
        <section id="features" className="features-section">
          <h2 className="text-center font-display text-h1 feature-main-title">
            Engineered For Fraud Analysts
          </h2>
          <p className="text-center section-subtext">
            Advanced detection algorithms mapped with glassmorphic, micro-animated forensic tools.
          </p>

          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon bg-blue">
                <Shield size={24} className="text-blue" />
              </div>
              <h3>Command Center</h3>
              <p>Real-time national surveillance feeds. Indian geographic heatmaps, live alert timelines, and unified risk dashboards.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon bg-purple">
                <Activity size={24} />
              </div>
              <h3>Explainable AI (SHAP)</h3>
              <p>No black boxes. Direct waterfall breakdowns translating complex mathematical vector weights into plain English evidence files.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon bg-red">
                <Cpu size={24} />
              </div>
              <h3>Predictive Stacking</h3>
              <p>LightGBM, XGBoost, and CatBoost ensemble predictions scoring transactions instantly with a multi-layered penalty booster.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon bg-green">
                <Layers size={24} />
              </div>
              <h3>Unsupervised Anomaly Lab</h3>
              <p>Isolate outlier signals using Isolation Forests and Autoencoders, visualised via multi-dimensional PCA space mappings.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon bg-orange">
                <Users size={24} />
              </div>
              <h3>Coordinated Ring Discovery</h3>
              <p>Track mule networks and money-routing clusters. Graph database analytics showcasing DBSCAN cluster associations.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon bg-cyan">
                <Lock size={24} />
              </div>
              <h3>LLM Audit Copilot</h3>
              <p>Natural language queries to deep dive into suspicious accounts. Generates complete prosecution-ready STR reports.</p>
            </div>
          </div>
        </section>

        {/* Trust Bar / Logos */}
        <section className="tech-stack-showcase">
          <p className="stack-title">BUILT WITH ENTERPRISE-GRADE PYTHON + REACT INFRASTRUCTURE</p>
          <div className="tech-logo-flex">
            <span>FastAPI</span>
            <span>Scikit-Learn</span>
            <span>Vite</span>
            <span>Apache ECharts</span>
            <span>React Router</span>
            <span>Google Gemini</span>
            <span>LightGBM</span>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="landing-footer">
        <p>© 2026 MuleNet AI. Designed & Developed for Bank of India Cybersecurity Hackathon. Confidential Platform.</p>
      </footer>
    </div>
  );
}
