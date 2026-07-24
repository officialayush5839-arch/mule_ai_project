import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import { GitFork, Settings, RefreshCw, Cpu, ShieldAlert, Award, Grid, ArrowRight } from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';

export default function PatternDiscovery() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recomputing, setRecomputing] = useState(false);

  // States
  const [clusters, setClusters] = useState([]);
  const [scatter, setScatter] = useState([]);
  
  // Alg Parameters
  const [alg, setAlg] = useState('DBSCAN');
  const [eps, setEps] = useState(1.2);
  const [minPts, setMinPts] = useState(5);
  
  const loadData = async () => {
    setLoading(true);
    try {
      const [clustersRes, scatterRes] = await Promise.all([
        api.getClusters(),
        api.getClusterScatter()
      ]);
      setClusters(clustersRes);
      setScatter(scatterRes);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRecalculate = () => {
    setRecomputing(true);
    setTimeout(() => {
      // Simulate slight variation in cluster counts/risk based on params
      if (alg === 'KMeans') {
        // KMeans mock variation
        setClusters(prev => prev.map(c => ({
          ...c,
          count: Math.max(10, c.count + Math.floor(Math.random() * 20 - 10))
        })));
      } else {
        // DBSCAN variation
        setClusters(prev => prev.map(c => ({
          ...c,
          count: Math.max(8, c.count + Math.floor(Math.random() * 12 - 6))
        })));
      }
      setRecomputing(false);
    }, 800);
  };

  // ECharts Scatter Options
  const getScatterOption = () => {
    const series = clusters.map(c => {
      const clusterPoints = scatter.filter(p => p.cluster === c.id);
      return {
        name: c.name,
        type: 'scatter',
        symbolSize: 8,
        color: c.color,
        itemStyle: {
          shadowBlur: 4,
          shadowColor: 'rgba(0,0,0,0.15)'
        },
        data: clusterPoints.map(p => [p.x, p.y, p.accountId])
      };
    });

    return {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderWidth: 0,
        textStyle: { color: '#fff', fontSize: 11 },
        formatter: function (params) {
          return `
            <b>Account: ${params.data[2]}</b><br/>
            Cluster: ${params.seriesName}<br/>
            Projection X: ${params.data[0].toFixed(2)}<br/>
            Projection Y: ${params.data[1].toFixed(2)}
          `;
        }
      },
      legend: {
        orient: 'horizontal',
        bottom: 0,
        icon: 'circle',
        textStyle: { color: '#64748b', fontSize: 10, fontWeight: 600 }
      },
      grid: { left: '3%', right: '3%', top: '5%', bottom: '15%', containLabel: true },
      xAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        splitLine: { show: false },
        axisLabel: { color: '#64748b' }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#cbd5e1' } },
        splitLine: { show: false },
        axisLabel: { color: '#64748b' }
      },
      series
    };
  };

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">Coordinated Pattern Discovery</h1>
          <p className="page-subtitle">Expose structured money mule rings and coordinated deposit structures in multi-dimensional feature topologies.</p>
        </div>
      </div>

      {loading ? (
        <div className="dashboard-loading flex flex-col justify-center items-center w-full" style={{ height: '70vh' }}>
          <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></div>
          <span className="text-label" style={{ marginTop: '16px' }}>Resolving cluster vectors...</span>
        </div>
      ) : (
        <div className="flex flex-col gap-24 w-full">
          {/* Main Grid: Parameter settings and ECharts Scatter */}
          <div className="grid-3 w-full" style={{ gridTemplateColumns: '1.2fr 1.8fr' }}>
            {/* Algorithm Config Panel */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '440px' }}>
              <div>
                <div className="flex items-center gap-8 text-label">
                  <Settings size={16} />
                  <span>Algorithm Hyperparameters</span>
                </div>
                <h3 className="text-h3 font-display" style={{ marginTop: '8px' }}>Cluster Configuration</h3>
              </div>

              <div className="config-form flex flex-col gap-16" style={{ flex: 1, marginTop: '24px' }}>
                {/* Alg Selector */}
                <div className="flex flex-col gap-4">
                  <span className="text-label" style={{ fontSize: '9px' }}>Clustering Engine</span>
                  <div className="flex gap-8">
                    <button 
                      className={`btn btn-sm ${alg === 'DBSCAN' ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ flex: 1 }}
                      onClick={() => setAlg('DBSCAN')}
                    >
                      DBSCAN
                    </button>
                    <button 
                      className={`btn btn-sm ${alg === 'KMeans' ? 'btn-primary' : 'btn-secondary'}`}
                      style={{ flex: 1 }}
                      onClick={() => setAlg('KMeans')}
                    >
                      K-Means ++
                    </button>
                  </div>
                </div>

                {/* Epsilon Slider */}
                {alg === 'DBSCAN' && (
                  <div className="flex flex-col gap-4">
                    <div className="flex justify-between items-center w-full text-label" style={{ fontSize: '9px' }}>
                      <span>Epsilon (Radius: ε)</span>
                      <span className="font-mono text-primary font-bold">{eps}</span>
                    </div>
                    <input 
                      type="range" 
                      min="0.4" 
                      max="2.5" 
                      step="0.1" 
                      className="input-range"
                      value={eps}
                      onChange={(e) => setEps(parseFloat(e.target.value))}
                    />
                  </div>
                )}

                {/* Min Points / K Slider */}
                <div className="flex flex-col gap-4">
                  <div className="flex justify-between items-center w-full text-label" style={{ fontSize: '9px' }}>
                    <span>{alg === 'DBSCAN' ? 'Min Cluster Core Points' : 'Number of Centroids (k)'}</span>
                    <span className="font-mono text-primary font-bold">{minPts}</span>
                  </div>
                  <input 
                    type="range" 
                    min={alg === 'DBSCAN' ? '2' : '3'} 
                    max={alg === 'DBSCAN' ? '20' : '10'} 
                    step="1" 
                    className="input-range"
                    value={minPts}
                    onChange={(e) => setMinPts(parseInt(e.target.value))}
                  />
                </div>
              </div>

              <button 
                className="btn btn-primary w-full"
                disabled={recomputing}
                onClick={handleRecalculate}
              >
                {recomputing ? (
                  <>
                    <RefreshCw size={14} className="animate-spin" />
                    <span>Recalculating...</span>
                  </>
                ) : (
                  <span>Compile Cluster Nodes</span>
                )}
              </button>
            </div>

            {/* Scatter Graph */}
            <div className="card flex flex-col justify-between" style={{ minHeight: '440px' }}>
              <div>
                <h3 className="text-h3 font-display">Clustered Coordinate Projections</h3>
                <span className="text-label" style={{ fontSize: '10px' }}>Structural connections mapped in high-dimensional node space</span>
              </div>

              <div style={{ flex: 1, marginTop: '16px' }}>
                <ReactECharts option={getScatterOption()} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>
          </div>

          {/* Cluster Detailed Showcase */}
          <div className="flex flex-col gap-12 w-full">
            <h3 className="text-h3 font-display">Cluster Signatures</h3>
            
            <div className="grid-3 w-full">
              {clusters.map((c) => (
                <div key={c.id} className="card flex flex-col justify-between" style={{ borderLeft: `5px solid ${c.color}` }}>
                  <div className="flex justify-between items-start w-full">
                    <div>
                      <h4 className="text-h3" style={{ fontSize: '15px', fontWeight: 700 }}>{c.name}</h4>
                      <span className="font-mono text-label" style={{ fontSize: '9px' }}>Cluster ID: #{c.id} | Members: {c.count}</span>
                    </div>
                    <span className={`risk-badge risk-badge--${c.risk.toLowerCase()}`} style={{ fontSize: '9px' }}>
                      {c.risk}
                    </span>
                  </div>

                  <div className="cluster-features border-top-divider" style={{ marginTop: '16px', paddingTop: '12px' }}>
                    <span className="text-label" style={{ fontSize: '9px' }}>Typology Characteristics:</span>
                    <ul style={{ listStyle: 'none', paddingLeft: 0, marginTop: '4px' }}>
                      {c.features.slice(0, 3).map((feat, i) => (
                        <li key={i} style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '3px', lineHeight: 1.3 }}>
                          • {feat}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex justify-between items-center w-full border-top-divider" style={{ marginTop: '12px', paddingTop: '10px' }}>
                    <span className="text-label" style={{ fontSize: '9px' }}>Engine Confidence: {(c.confidence * 100).toFixed(0)}%</span>
                    <button className="btn btn-ghost btn-sm" onClick={() => navigate('/alert-center')}>
                      Audit Cluster <ArrowRight size={10} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .input-range {
          width: 100%;
          cursor: pointer;
          accent-color: var(--primary);
        }
      `}</style>
    </AppLayout>
  );
}
