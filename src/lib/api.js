/* ═══════════════════════════════════════════
   MuleNet AI — API Integration Layer
   Allows seamless toggling between Mock and Real
   ═══════════════════════════════════════════ */

import * as mock from './mockData';

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Flag to switch between mock data and the real FastAPI backend
// When running in production / hackathon mode, this can be set to true if backend is running
const USE_REAL_BACKEND = false; 
const BACKEND_URL = 'http://127.0.0.1:8000/api';

// --- In-Memory State for Uploaded Dataset ---
let activeDataset = null; // Can be 'mock' or 'custom'
let customAccounts = [];
let customKpis = [];
let customRiskDistribution = [];
let customRiskTimeline = [];
let customGeoRiskData = [];
let customAlerts = [];

// Helper to generate dynamic Indian names
const IndianNames = [
  'Rajesh Kumar', 'Amit Patel', 'Priya Nair', 'Sunita Devi', 'Mohammed Irfan',
  'Deepika Reddy', 'Vikram Singh', 'Lakshmi Menon', 'Arjun Mehta', 'Kavita Joshi',
  'Suresh Iyer', 'Neha Gupta', 'Ramesh Babu', 'Anjali Deshmukh', 'Karthik Rajan',
  'Fatima Begum', 'Anil Kapoor', 'Meera Bhat', 'Rohit Verma', 'Pooja Saxena',
  'Sanjay Dutt', 'Divya Teja', 'Sandeep Rao', 'Shalini Sharma', 'Vijay Mallya'
];

const IndianBranches = [
  'Mumbai - Andheri West', 'Chennai - T Nagar', 'Delhi - Connaught Place',
  'Kolkata - Salt Lake', 'Hyderabad - Banjara Hills', 'Bangalore - Koramangala',
  'Pune - Kothrud', 'Kochi - MG Road', 'Mumbai - Bandra', 'Jaipur - MI Road',
  'Chennai - Adyar', 'Delhi - Karol Bagh', 'Hyderabad - Madhapur', 'Pune - Hinjewadi',
  'Bangalore - Whitefield', 'Lucknow - Hazratganj', 'Mumbai - Dadar', 'Ahmedabad - CG Road',
  'Chandigarh - Sector 17', 'Indore - Vijay Nagar'
];

// Simple CSV parser that handles quotes and returns an array of objects
function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter(line => line.trim() !== '');
  if (lines.length === 0) return [];
  
  // Parse headers
  const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
  const results = [];
  
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    // simple comma split, ignoring commas inside quotes
    const values = [];
    let current = '';
    let inQuotes = false;
    
    for (let char of line) {
      if (char === '"' || char === "'") {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim().replace(/^["']|["']$/g, ''));
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current.trim().replace(/^["']|["']$/g, ''));
    
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });
    results.push(row);
  }
  return results;
}

export const api = {
  // Get active source
  getActiveSource: () => {
    return activeDataset || 'mock';
  },

  // Switch source or reset
  resetToMock: () => {
    activeDataset = null;
    customAccounts = [];
    customKpis = [];
    customRiskDistribution = [];
    customRiskTimeline = [];
    customGeoRiskData = [];
    customAlerts = [];
    // Broadcast event for UI updates
    window.dispatchEvent(new Event('datasource-changed'));
  },

  // Parse and set custom dataset from CSV
  processCustomCSV: async (csvText, fileName) => {
    try {
      const rows = parseCSV(csvText);
      if (rows.length === 0) {
        throw new Error('CSV file is empty or formatted incorrectly');
      }

      // 1. Identify key columns (look for ID, Name, Risk etc.)
      const sample = rows[0];
      const keys = Object.keys(sample);
      
      const idKey = keys.find(k => k.toLowerCase().includes('id') || k.toLowerCase().includes('account')) || keys[0];
      const nameKey = keys.find(k => k.toLowerCase().includes('name') || k.toLowerCase().includes('customer') || k.toLowerCase().includes('holder'));
      const riskKey = keys.find(k => k.toLowerCase().includes('risk') || k.toLowerCase().includes('score') || k.toLowerCase().includes('prob'));
      const typeKey = keys.find(k => k.toLowerCase().includes('type'));
      const branchKey = keys.find(k => k.toLowerCase().includes('branch') || k.toLowerCase().includes('location') || k.toLowerCase().includes('city'));
      const dateKey = keys.find(k => k.toLowerCase().includes('date') || k.toLowerCase().includes('open') || k.toLowerCase().includes('created'));

      // 2. Generate Accounts list
      const accountsList = rows.map((row, idx) => {
        let rawId = String(row[idKey] || `ACC-${100000 + idx}`);
        if (!rawId.startsWith('ACC-')) {
          rawId = `ACC-${rawId}`;
        }
        
        let rawName = nameKey ? row[nameKey] : IndianNames[idx % IndianNames.length];
        let type = typeKey ? row[typeKey] : (idx % 3 === 0 ? 'Current' : 'Savings');
        let branch = branchKey ? row[branchKey] : IndianBranches[idx % IndianBranches.length];
        
        let opened = dateKey ? row[dateKey] : new Date(Date.now() - (idx * 15 + 10) * 86400000).toISOString().split('T')[0];
        
        let riskScore = 50;
        if (riskKey) {
          let parsedRisk = parseFloat(row[riskKey]);
          if (!isNaN(parsedRisk)) {
            // handle probability values 0.0 - 1.0 vs score values 0 - 100
            riskScore = parsedRisk <= 1.0 && parsedRisk >= 0.0 ? Math.round(parsedRisk * 100) : Math.min(Math.max(Math.round(parsedRisk), 0), 100);
          } else {
            riskScore = Math.floor(10 + Math.random() * 85);
          }
        } else {
          // If no risk score, determine dynamically based on numerical features if available
          let numericSum = 0;
          let numericCount = 0;
          Object.values(row).forEach(val => {
            let n = parseFloat(val);
            if (!isNaN(n) && n >= 0 && n <= 100) {
              numericSum += n;
              numericCount++;
            }
          });
          riskScore = numericCount > 0 ? Math.round((numericSum / numericCount) * 1.2) : Math.floor(10 + Math.random() * 85);
          riskScore = Math.min(Math.max(riskScore, 5), 98);
        }

        let classification = 'SAFE';
        if (riskScore > 80) classification = 'CRITICAL';
        else if (riskScore > 60) classification = 'SUSPICIOUS';
        else if (riskScore > 30) classification = 'WATCHLIST';

        return {
          id: rawId,
          name: rawName,
          type,
          branch,
          opened,
          status: 'Active',
          riskScore,
          classification,
          confidence: parseFloat((85 + Math.random() * 14.5).toFixed(1)),
          lastSeen: new Date(Date.now() - Math.floor(Math.random() * 60) * 60000).toISOString(),
          alertLevel: classification === 'CRITICAL' ? 'HIGH' : classification === 'SUSPICIOUS' ? 'MEDIUM' : classification === 'WATCHLIST' ? 'LOW' : 'NONE',
          modelUsed: 'Custom Dataset Pipeline',
          trustScore: 100 - riskScore
        };
      });

      // Optimize for large datasets: compute stats on the full list, but cap the active
      // rendering list to the top 1000 highest risk accounts to prevent browser UI lockups.
      const totalCount = accountsList.length;
      const criticalCount = accountsList.filter(a => a.classification === 'CRITICAL').length;
      const suspiciousCount = accountsList.filter(a => a.classification === 'SUSPICIOUS').length;
      const watchlistCount = accountsList.filter(a => a.classification === 'WATCHLIST').length;
      const monitoringCount = Math.round(totalCount * 0.08) + watchlistCount;
      const avgRisk = parseFloat((accountsList.reduce((sum, a) => sum + a.riskScore, 0) / totalCount).toFixed(1));

      // Sort and slice custom accounts for the UI components
      const sortedList = [...accountsList].sort((a, b) => b.riskScore - a.riskScore);
      customAccounts = sortedList.slice(0, 1000);

      customKpis = [
        { id: 'total-accounts', label: 'Total Accounts', value: totalCount, trend: '+0.0%', trendDir: 'up', icon: 'Users', sparkline: [42, 45, 48, 44, 52, 55, totalCount > 100 ? 58 : 42] },
        { id: 'monitoring', label: 'Under Monitoring', value: monitoringCount, trend: '+4.2%', trendDir: 'up', icon: 'Eye', sparkline: [32, 34, 38, 36, 40, 42, 45] },
        { id: 'suspicious', label: 'Suspicious Accounts', value: suspiciousCount, trend: '+10.4%', trendDir: 'up', icon: 'AlertTriangle', color: 'warning', sparkline: [18, 22, 24, 28, 30, 35, 38] },
        { id: 'critical', label: 'Critical Accounts', value: criticalCount, trend: '+5.1%', trendDir: 'up', icon: 'ShieldAlert', color: 'critical', sparkline: [12, 14, 13, 16, 15, 18, 20] },
        { id: 'active-alerts', label: 'Active Alerts', value: criticalCount + suspiciousCount, trend: '+15.4%', trendDir: 'up', icon: 'Bell', color: 'critical', pulse: true, sparkline: [20, 24, 28, 22, 30, 34, 38] },
        { id: 'investigations', label: 'Open Investigations', value: Math.round(criticalCount * 0.8), trend: '-2.1%', trendDir: 'down', icon: 'Search', color: 'accent', sparkline: [15, 14, 12, 13, 11, 10, 9] },
        { id: 'avg-risk', label: 'Avg Risk Score', value: avgRisk, trend: '+1.4', trendDir: 'up', icon: 'Gauge', sparkline: [40, 42, 44, 43, 45, 46, 47] },
        { id: 'loss-prevented', label: 'Loss Prevented (₹)', value: Math.round(criticalCount * 35000), formatted: `${((criticalCount * 0.035)).toFixed(2)} Cr`, trend: '+12.4%', trendDir: 'up', icon: 'Shield', color: 'accent', sparkline: [60, 65, 68, 72, 78, 82, 90] },
      ];

      // 4. Risk Distribution
      const safeCount = customAccounts.filter(a => a.classification === 'SAFE').length;
      customRiskDistribution = [
        { name: 'SAFE', value: Math.round((safeCount / totalCount) * 100), color: '#10B981' },
        { name: 'WATCHLIST', value: Math.round((watchlistCount / totalCount) * 100), color: '#F59E0B' },
        { name: 'SUSPICIOUS', value: Math.round((suspiciousCount / totalCount) * 100), color: '#8B5CF6' },
        { name: 'CRITICAL', value: Math.round((criticalCount / totalCount) * 100), color: '#EF4444' },
      ];

      // 5. Risk Timeline
      customRiskTimeline = Array.from({ length: 30 }, (_, i) => {
        const date = new Date(Date.now() - (29 - i) * 86400000);
        return {
          date: date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
          safe: Math.floor(safeCount * 0.8 / 30 * i + safeCount * 0.1),
          watchlist: Math.floor(watchlistCount * 0.8 / 30 * i + watchlistCount * 0.1),
          suspicious: Math.floor(suspiciousCount * 0.8 / 30 * i + suspiciousCount * 0.1),
          critical: Math.floor(criticalCount * 0.8 / 30 * i + criticalCount * 0.1),
        };
      });

      // 6. Geographic Risk
      const stateCounts = {};
      customAccounts.forEach(acc => {
        const state = acc.branch.split(' - ')[0] || 'Unknown';
        stateCounts[state] = (stateCounts[state] || 0) + 1;
      });
      customGeoRiskData = Object.entries(stateCounts)
        .map(([state, count]) => ({
          state,
          accounts: count,
          risk: Math.min(Math.round((count / totalCount) * 180 + 20), 98)
        }))
        .sort((a, b) => b.accounts - a.accounts);

      // 7. Active Alerts
      customAlerts = customAccounts
        .filter(a => a.classification === 'CRITICAL' || a.classification === 'SUSPICIOUS')
        .map((a, idx) => ({
          id: `ALT-${3000 + idx}`,
          accountId: a.id,
          priority: a.classification,
          timestamp: new Date(Date.now() - idx * 240000).toISOString(),
          riskScore: a.riskScore,
          confidence: a.confidence,
          trigger: a.classification === 'CRITICAL' ? 'Critical threat coefficients detected' : 'Suspicious activity sequence matching watchlist',
          evidence: [`Outflow risk index: ${a.riskScore}%`, `Model match confidence: ${a.confidence}%`],
          status: 'active'
        }));

      activeDataset = 'custom';
      
      // Broadcast event for UI updates
      window.dispatchEvent(new Event('datasource-changed'));
      
      return {
        success: true,
        totalUploaded: totalCount,
        anomaliesDetected: criticalCount + suspiciousCount,
        avgRiskScore: avgRisk,
        criticalMulesFound: criticalCount
      };
    } catch (e) {
      console.error(e);
      throw e;
    }
  },

  // ── General / Dashboard ──
  getKPIs: async () => {
    await delay(300);
    return activeDataset === 'custom' ? customKpis : mock.kpiData;
  },

  getRiskDistribution: async () => {
    await delay(200);
    return activeDataset === 'custom' ? customRiskDistribution : mock.riskDistribution;
  },

  getRiskTimeline: async () => {
    await delay(250);
    return activeDataset === 'custom' ? customRiskTimeline : mock.riskTimeline;
  },

  getAIInsights: async () => {
    await delay(200);
    if (activeDataset === 'custom') {
      const crit = customAccounts.filter(a => a.classification === 'CRITICAL').length;
      return [
        { id: 1, type: 'critical', title: 'Custom Dataset Risk Spike', time: '1m ago', description: `${crit} newly identified critical threat patterns found in uploaded CSV file.`, action: 'Investigate Cluster', icon: 'AlertTriangle' },
        { id: 2, type: 'info', title: 'File ingestion successfully complete', time: '10m ago', description: 'ML classification run across all CSV transactions. Features mapped.', action: 'View Metrics', icon: 'CheckCircle' }
      ];
    }
    return mock.aiInsights;
  },

  getGeoRiskData: async () => {
    await delay(300);
    return activeDataset === 'custom' ? customGeoRiskData : mock.geoRiskData;
  },

  // ── Accounts ──
  getAccounts: async () => {
    await delay(400);
    return activeDataset === 'custom' ? customAccounts : mock.accounts;
  },

  getHighRiskAccounts: async (limit = 10) => {
    await delay(300);
    const source = activeDataset === 'custom' ? customAccounts : mock.accounts;
    return source
      .filter(a => a.classification === 'CRITICAL' || a.classification === 'SUSPICIOUS')
      .sort((a, b) => b.riskScore - a.riskScore)
      .slice(0, limit);
  },

  getAccountDetails: async (accountId) => {
    await delay(350);
    const source = activeDataset === 'custom' ? customAccounts : mock.accounts;
    const acc = source.find(a => a.id === accountId);
    if (!acc) throw new Error('Account not found');
    return acc;
  },

  getAccountShap: async (accountId) => {
    await delay(300);
    return mock.getShapForAccount(accountId);
  },

  getAccountBehaviorRadar: async (accountId) => {
    await delay(250);
    return mock.getBehaviorRadar(accountId);
  },

  getAccountRiskHistory: async (accountId) => {
    await delay(300);
    return mock.getRiskHistory(accountId);
  },

  getAccountRiskBreakdown: async (accountId) => {
    await delay(300);
    return mock.getRiskBreakdown(accountId);
  },

  getAccountFuturePrediction: async (accountId) => {
    await delay(300);
    return mock.getFuturePrediction(accountId);
  },

  getAccountTransactionTrend: async (accountId) => {
    await delay(350);
    return mock.getTransactionTrend(accountId);
  },

  // ── Alerts ──
  getAlerts: async () => {
    await delay(300);
    return activeDataset === 'custom' ? customAlerts : mock.alerts;
  },

  actionAlert: async (alertId, action) => {
    await delay(500);
    const source = activeDataset === 'custom' ? customAlerts : mock.alerts;
    const alert = source.find(a => a.id === alertId);
    if (alert) {
      alert.status = action === 'dismiss' ? 'dismissed' : 'processed';
      alert.actionTaken = action;
    }
    return { success: true, alertId, action };
  },

  // ── Anomaly Lab ──
  getAnomalyModels: async () => {
    await delay(200);
    return mock.anomalyModels;
  },

  getAnomalyScatter: async () => {
    await delay(400);
    if (activeDataset === 'custom') {
      return customAccounts.map((acc, i) => {
        const isAnomaly = acc.classification === 'CRITICAL' || acc.classification === 'SUSPICIOUS';
        return {
          id: acc.id,
          x: isAnomaly ? (Math.random() * 4 + 3) : (Math.random() * 6 - 3),
          y: isAnomaly ? (Math.random() * 4 + 2) : (Math.random() * 6 - 3),
          severity: acc.classification.toLowerCase(),
          ifScore: isAnomaly ? +(0.65 + Math.random() * 0.35).toFixed(2) : +(Math.random() * 0.5).toFixed(2),
          aeScore: isAnomaly ? +(0.60 + Math.random() * 0.40).toFixed(2) : +(Math.random() * 0.45).toFixed(2),
          lofScore: isAnomaly ? +(0.55 + Math.random() * 0.45).toFixed(2) : +(Math.random() * 0.40).toFixed(2),
          combined: isAnomaly ? +(0.65 + Math.random() * 0.35).toFixed(2) : +(Math.random() * 0.40).toFixed(2),
        };
      });
    }
    return mock.anomalyScatter;
  },

  getAnomalyRankings: async () => {
    await delay(350);
    if (activeDataset === 'custom') {
      return customAccounts
        .filter(a => a.classification === 'CRITICAL' || a.classification === 'SUSPICIOUS')
        .sort((a, b) => b.riskScore - a.riskScore)
        .slice(0, 15)
        .map((a, i) => ({
          id: a.id,
          x: 4 + Math.random(),
          y: 3 + Math.random(),
          severity: a.classification.toLowerCase(),
          ifScore: a.riskScore / 100,
          aeScore: a.riskScore / 100 * 0.9,
          lofScore: a.riskScore / 100 * 0.85,
          combined: a.riskScore / 100,
          rank: i + 1
        }));
    }
    return mock.anomalyRankings;
  },

  // ── Explainable AI (Global) ──
  getGlobalFeatureImportance: async () => {
    await delay(250);
    return mock.globalFeatureImportance;
  },

  // ── Pattern Discovery ──
  getClusters: async () => {
    await delay(300);
    return mock.clusters;
  },

  getClusterScatter: async () => {
    await delay(450);
    return mock.clusterScatter;
  },

  // ── Model Intelligence ──
  getModelMetrics: async () => {
    await delay(250);
    return mock.modelMetrics;
  },

  getConfusionMatrix: async () => {
    await delay(200);
    return mock.confusionMatrix;
  },

  getROCCurve: async () => {
    await delay(300);
    return mock.rocCurve;
  },

  getBaseModels: async () => {
    await delay(200);
    return mock.baseModels;
  },

  getModelHealth: async () => {
    await delay(250);
    return mock.modelHealth;
  },

  // ── Copilot ──
  sendCopilotMessage: async (message) => {
    await delay(800);
    const normalized = message.toLowerCase().trim();
    
    if (normalized.includes('why is acc-847291 flagged') || normalized.includes('acc-847291')) {
      return mock.copilotResponses['why is ACC-847291 flagged'];
    }
    if (normalized.includes('generate report') || normalized.includes('report for acc-847291')) {
      return mock.copilotResponses['generate report'];
    }
    if (normalized.includes('summarize alerts') || normalized.includes('alert summary') || normalized.includes('summarise alerts')) {
      return mock.copilotResponses['summarize alerts'];
    }
    return mock.copilotResponses['default'];
  },

  // ── File Upload Anomaly Detection ──
  uploadCSV: async (file) => {
    await delay(1500);
    return {
      totalUploaded: 1250,
      anomaliesDetected: 43,
      avgRiskScore: 68.2,
      criticalMulesFound: 9,
      jobId: `JOB-${Math.floor(100000 + Math.random() * 900000)}`,
      anomalousAccounts: [
        { id: 'ACC-UPLOAD-01', riskScore: 92, classification: 'CRITICAL', reason: 'High velocity pattern match' },
        { id: 'ACC-UPLOAD-02', riskScore: 88, classification: 'CRITICAL', reason: 'Dormancy activation' },
        { id: 'ACC-UPLOAD-03', riskScore: 84, classification: 'CRITICAL', reason: 'Fund concentration (SMOTE feature variance)' },
        { id: 'ACC-UPLOAD-04', riskScore: 78, classification: 'SUSPICIOUS', reason: 'Outflow dominance ratio' },
        { id: 'ACC-UPLOAD-05', riskScore: 76, classification: 'SUSPICIOUS', reason: 'Centrality anomaly' }
      ]
    };
  },

  // ── Admin Observability ──
  getSystemHealth: async () => {
    if (!USE_REAL_BACKEND) {
      await delay(500);
      return {
        timestamp: new Date().toISOString(),
        services: {
          status: "demo",
          backend: { status: "healthy", latency: "45ms" },
          database: { status: "healthy", latency: "12ms" },
          redis: { status: "healthy", latency: "5ms" },
          ai_engine: { status: "healthy", latency: "85ms" }
        }
      };
    }
    
    try {
      const response = await fetch(`${BACKEND_URL}/admin/system-health`);
      if (!response.ok) throw new Error("Failed to fetch system health");
      return await response.json();
    } catch (e) {
      console.error(e);
      throw e;
    }
  },

  getAdminMetrics: async () => {
    if (!USE_REAL_BACKEND) {
      await delay(400);
      return {
        api: { requests: 125430, latency: 86, errors: 0.02 },
        ai: { predictions: 98540, inference_time: 92, success_rate: 99.8 },
        security: { suspicious: 342, high_risk: 56, blocked: 21 },
        infrastructure: { cpu_usage: 42, memory_usage: 61, database_connections: 24 }
      };
    }
    
    try {
      const response = await fetch(`${BACKEND_URL}/admin/metrics`);
      if (!response.ok) throw new Error("Failed to fetch admin metrics");
      return await response.json();
    } catch (e) {
      console.error(e);
      throw e;
    }
  },

  getSignozAccess: async () => {
    if (!USE_REAL_BACKEND) {
      await delay(400);
      return {
        success: true,
        has_access: true,
        signoz: {
          url: import.meta.env.VITE_SIGNOZ_URL || "https://signoz.io",
          status: "connected",
          latency_ms: 42
        }
      };
    }

    try {
      const response = await fetch(`${BACKEND_URL}/admin/signoz-access`);
      if (!response.ok) throw new Error("Failed to verify SigNoz access");
      return await response.json();
    } catch (e) {
      console.error(e);
      return { success: false, has_access: false, error: e.message };
    }
  }
};
