/* ═══════════════════════════════════════════
   MuleNet AI — Comprehensive Mock Data Layer
   ═══════════════════════════════════════════ */

// ── Helper to generate dates ──
const now = new Date();
const ago = (minutes) => new Date(now - minutes * 60000).toISOString();
const daysAgo = (days) => new Date(now - days * 86400000).toISOString();

// ── High Risk Accounts ──
export const accounts = [
  { id: 'ACC-847291', name: 'Rajesh Kumar Sharma', type: 'Savings', branch: 'Mumbai - Andheri West', opened: '2024-01-14', status: 'Active', riskScore: 94, classification: 'CRITICAL', confidence: 97.3, lastSeen: ago(2), alertLevel: 'HIGH', modelUsed: 'Stacking Ensemble', trustScore: 23 },
  { id: 'ACC-291847', name: 'Priya Nair', type: 'Current', branch: 'Chennai - T Nagar', opened: '2023-11-08', status: 'Active', riskScore: 81, classification: 'SUSPICIOUS', confidence: 89.1, lastSeen: ago(8), alertLevel: 'MEDIUM', modelUsed: 'Stacking Ensemble', trustScore: 34 },
  { id: 'ACC-738291', name: 'Amit Patel', type: 'Savings', branch: 'Delhi - Connaught Place', opened: '2024-03-22', status: 'Active', riskScore: 87, classification: 'CRITICAL', confidence: 93.7, lastSeen: ago(5), alertLevel: 'HIGH', modelUsed: 'Stacking Ensemble', trustScore: 19 },
  { id: 'ACC-482916', name: 'Sunita Devi', type: 'Savings', branch: 'Kolkata - Salt Lake', opened: '2023-09-15', status: 'Active', riskScore: 76, classification: 'SUSPICIOUS', confidence: 85.4, lastSeen: ago(12), alertLevel: 'MEDIUM', modelUsed: 'Stacking Ensemble', trustScore: 38 },
  { id: 'ACC-619283', name: 'Mohammed Irfan', type: 'Current', branch: 'Hyderabad - Banjara Hills', opened: '2024-02-01', status: 'Active', riskScore: 91, classification: 'CRITICAL', confidence: 95.8, lastSeen: ago(3), alertLevel: 'HIGH', modelUsed: 'Stacking Ensemble', trustScore: 15 },
  { id: 'ACC-384729', name: 'Deepika Reddy', type: 'Savings', branch: 'Bangalore - Koramangala', opened: '2023-12-10', status: 'Active', riskScore: 68, classification: 'SUSPICIOUS', confidence: 82.6, lastSeen: ago(18), alertLevel: 'MEDIUM', modelUsed: 'Stacking Ensemble', trustScore: 42 },
  { id: 'ACC-927184', name: 'Vikram Singh', type: 'Current', branch: 'Pune - Kothrud', opened: '2024-04-05', status: 'Active', riskScore: 83, classification: 'CRITICAL', confidence: 91.2, lastSeen: ago(7), alertLevel: 'HIGH', modelUsed: 'Stacking Ensemble', trustScore: 22 },
  { id: 'ACC-158293', name: 'Lakshmi Menon', type: 'Savings', branch: 'Kochi - MG Road', opened: '2023-08-20', status: 'Active', riskScore: 54, classification: 'SUSPICIOUS', confidence: 78.9, lastSeen: ago(25), alertLevel: 'MEDIUM', modelUsed: 'Stacking Ensemble', trustScore: 51 },
  { id: 'ACC-642819', name: 'Arjun Mehta', type: 'Current', branch: 'Mumbai - Bandra', opened: '2024-01-30', status: 'Active', riskScore: 72, classification: 'SUSPICIOUS', confidence: 84.3, lastSeen: ago(14), alertLevel: 'MEDIUM', modelUsed: 'Stacking Ensemble', trustScore: 36 },
  { id: 'ACC-839174', name: 'Kavita Joshi', type: 'Savings', branch: 'Jaipur - MI Road', opened: '2023-10-12', status: 'Active', riskScore: 89, classification: 'CRITICAL', confidence: 94.5, lastSeen: ago(4), alertLevel: 'HIGH', modelUsed: 'Stacking Ensemble', trustScore: 17 },
  { id: 'ACC-472918', name: 'Suresh Iyer', type: 'Savings', branch: 'Chennai - Adyar', opened: '2024-05-18', status: 'Active', riskScore: 45, classification: 'WATCHLIST', confidence: 72.1, lastSeen: ago(30), alertLevel: 'LOW', modelUsed: 'Stacking Ensemble', trustScore: 58 },
  { id: 'ACC-293847', name: 'Neha Gupta', type: 'Current', branch: 'Delhi - Karol Bagh', opened: '2023-07-25', status: 'Active', riskScore: 38, classification: 'WATCHLIST', confidence: 68.4, lastSeen: ago(45), alertLevel: 'LOW', modelUsed: 'Stacking Ensemble', trustScore: 63 },
  { id: 'ACC-718394', name: 'Ramesh Babu', type: 'Savings', branch: 'Hyderabad - Madhapur', opened: '2024-02-14', status: 'Active', riskScore: 62, classification: 'SUSPICIOUS', confidence: 81.7, lastSeen: ago(20), alertLevel: 'MEDIUM', modelUsed: 'Stacking Ensemble', trustScore: 44 },
  { id: 'ACC-584291', name: 'Anjali Deshmukh', type: 'Current', branch: 'Pune - Hinjewadi', opened: '2023-11-30', status: 'Active', riskScore: 15, classification: 'SAFE', confidence: 94.2, lastSeen: ago(60), alertLevel: 'NONE', modelUsed: 'Stacking Ensemble', trustScore: 87 },
  { id: 'ACC-391827', name: 'Karthik Rajan', type: 'Savings', branch: 'Bangalore - Whitefield', opened: '2024-03-10', status: 'Active', riskScore: 85, classification: 'CRITICAL', confidence: 92.8, lastSeen: ago(6), alertLevel: 'HIGH', modelUsed: 'Stacking Ensemble', trustScore: 20 },
  { id: 'ACC-829147', name: 'Fatima Begum', type: 'Savings', branch: 'Lucknow - Hazratganj', opened: '2023-06-18', status: 'Active', riskScore: 28, classification: 'WATCHLIST', confidence: 65.9, lastSeen: ago(90), alertLevel: 'LOW', modelUsed: 'Stacking Ensemble', trustScore: 71 },
  { id: 'ACC-174829', name: 'Anil Kapoor', type: 'Current', branch: 'Mumbai - Dadar', opened: '2024-04-22', status: 'Active', riskScore: 77, classification: 'SUSPICIOUS', confidence: 86.1, lastSeen: ago(10), alertLevel: 'MEDIUM', modelUsed: 'Stacking Ensemble', trustScore: 31 },
  { id: 'ACC-639281', name: 'Meera Bhat', type: 'Savings', branch: 'Ahmedabad - CG Road', opened: '2023-09-05', status: 'Active', riskScore: 12, classification: 'SAFE', confidence: 96.1, lastSeen: ago(120), alertLevel: 'NONE', modelUsed: 'Stacking Ensemble', trustScore: 91 },
  { id: 'ACC-481927', name: 'Rohit Verma', type: 'Current', branch: 'Chandigarh - Sector 17', opened: '2024-01-08', status: 'Active', riskScore: 92, classification: 'CRITICAL', confidence: 96.4, lastSeen: ago(1), alertLevel: 'HIGH', modelUsed: 'Stacking Ensemble', trustScore: 14 },
  { id: 'ACC-728194', name: 'Pooja Saxena', type: 'Savings', branch: 'Indore - Vijay Nagar', opened: '2023-12-28', status: 'Active', riskScore: 33, classification: 'WATCHLIST', confidence: 69.8, lastSeen: ago(55), alertLevel: 'LOW', modelUsed: 'Stacking Ensemble', trustScore: 67 },
];

// ── SHAP Values per Account ──
export const shapData = {
  'ACC-847291': {
    baseValue: 0.31,
    finalValue: 1.60,
    probability: 0.94,
    features: [
      { feature: 'F527', value: 0.42, label: 'Unusually high transaction velocity', direction: 'risk' },
      { feature: 'F1692', value: 0.31, label: 'Matches historical mule account behavior', direction: 'risk' },
      { feature: 'F3043', value: 0.24, label: 'Rapid fund outflow pattern detected', direction: 'risk' },
      { feature: 'F3894', value: 0.19, label: 'Strong anomaly signal from isolation forest', direction: 'risk' },
      { feature: 'F321', value: 0.17, label: 'Concentrated fund clustering from few sources', direction: 'risk' },
      { feature: 'F2082', value: 0.11, label: 'High-frequency small transactions detected', direction: 'risk' },
      { feature: 'F2678', value: 0.08, label: 'Network centrality above threshold', direction: 'risk' },
      { feature: 'F670', value: -0.09, label: 'Established account age (reducing risk)', direction: 'safe' },
      { feature: 'F115', value: -0.06, label: 'Moderate balance stability', direction: 'safe' },
      { feature: 'F2582', value: -0.04, label: 'Some pattern consistency', direction: 'safe' },
    ],
  },
  'ACC-291847': {
    baseValue: 0.31,
    finalValue: 1.18,
    probability: 0.81,
    features: [
      { feature: 'F3043', value: 0.28, label: 'Significant outflow-to-inflow imbalance', direction: 'risk' },
      { feature: 'F527', value: 0.22, label: 'Above-average transaction velocity', direction: 'risk' },
      { feature: 'F1692', value: 0.18, label: 'Partial mule behavior pattern match', direction: 'risk' },
      { feature: 'F2737', value: 0.14, label: 'Recent dormancy reactivation', direction: 'risk' },
      { feature: 'F3894', value: 0.11, label: 'Moderate anomaly signal', direction: 'risk' },
      { feature: 'F670', value: -0.12, label: 'Long account history (reducing risk)', direction: 'safe' },
      { feature: 'F115', value: -0.08, label: 'Reasonable balance stability', direction: 'safe' },
    ],
  },
};

// Generate default SHAP for any account
export function getShapForAccount(accountId) {
  if (shapData[accountId]) return shapData[accountId];
  const account = accounts.find(a => a.id === accountId);
  const score = account?.riskScore || 50;
  const factor = score / 100;
  return {
    baseValue: 0.31,
    finalValue: 0.31 + factor * 1.4,
    probability: score / 100,
    features: [
      { feature: 'F527', value: +(factor * 0.4).toFixed(2), label: 'Transaction velocity indicator', direction: 'risk' },
      { feature: 'F1692', value: +(factor * 0.3).toFixed(2), label: 'Behavioral pattern match score', direction: 'risk' },
      { feature: 'F3043', value: +(factor * 0.22).toFixed(2), label: 'Fund outflow pattern', direction: 'risk' },
      { feature: 'F3894', value: +(factor * 0.18).toFixed(2), label: 'Anomaly detection signal', direction: 'risk' },
      { feature: 'F321', value: +(factor * 0.15).toFixed(2), label: 'Fund concentration metric', direction: 'risk' },
      { feature: 'F670', value: -0.08, label: 'Account age factor', direction: 'safe' },
      { feature: 'F115', value: -0.05, label: 'Balance stability', direction: 'safe' },
    ],
  };
}

// ── Behavior Radar Data ──
export const behaviorRadarData = {
  'ACC-847291': {
    current: [92, 88, 94, 74, 85, 89],
    baseline: [35, 40, 30, 20, 15, 25],
  },
  'ACC-291847': {
    current: [78, 72, 81, 45, 68, 75],
    baseline: [35, 40, 30, 20, 15, 25],
  },
};

export function getBehaviorRadar(accountId) {
  if (behaviorRadarData[accountId]) return behaviorRadarData[accountId];
  const account = accounts.find(a => a.id === accountId);
  const f = (account?.riskScore || 50) / 100;
  return {
    current: [
      Math.round(f * 95 + Math.random() * 5),
      Math.round(f * 85 + Math.random() * 10),
      Math.round(f * 90 + Math.random() * 8),
      Math.round(f * 70 + Math.random() * 15),
      Math.round(f * 80 + Math.random() * 10),
      Math.round(f * 85 + Math.random() * 10),
    ],
    baseline: [35, 40, 30, 20, 15, 25],
  };
}

// ── KPI Data ──
export const kpiData = [
  { id: 'total-accounts', label: 'Total Accounts', value: 247831, trend: '+3.2%', trendDir: 'up', icon: 'Users', sparkline: [42, 45, 48, 44, 52, 55, 58] },
  { id: 'monitoring', label: 'Under Monitoring', value: 18429, trend: '+8.1%', trendDir: 'up', icon: 'Eye', sparkline: [32, 34, 38, 36, 40, 42, 45] },
  { id: 'suspicious', label: 'Suspicious Accounts', value: 4219, trend: '+12.4%', trendDir: 'up', icon: 'AlertTriangle', color: 'warning', sparkline: [18, 22, 24, 28, 30, 35, 38] },
  { id: 'critical', label: 'Critical Accounts', value: 1847, trend: '+6.7%', trendDir: 'up', icon: 'ShieldAlert', color: 'critical', sparkline: [12, 14, 13, 16, 15, 18, 20] },
  { id: 'active-alerts', label: 'Active Alerts', value: 342, trend: '+18.2%', trendDir: 'up', icon: 'Bell', color: 'critical', pulse: true, sparkline: [20, 24, 28, 22, 30, 34, 38] },
  { id: 'investigations', label: 'Open Investigations', value: 89, trend: '-4.3%', trendDir: 'down', icon: 'Search', color: 'accent', sparkline: [15, 14, 12, 13, 11, 10, 9] },
  { id: 'avg-risk', label: 'Avg Risk Score', value: 47.3, trend: '+2.1', trendDir: 'up', icon: 'Gauge', sparkline: [40, 42, 44, 43, 45, 46, 47] },
  { id: 'loss-prevented', label: 'Loss Prevented (₹)', value: 123000000, formatted: '12.3 Cr', trend: '+22.8%', trendDir: 'up', icon: 'Shield', color: 'accent', sparkline: [60, 65, 68, 72, 78, 82, 90] },
];

// ── Risk Distribution ──
export const riskDistribution = [
  { name: 'SAFE', value: 34, color: '#10B981' },
  { name: 'WATCHLIST', value: 28, color: '#F59E0B' },
  { name: 'SUSPICIOUS', value: 24, color: '#8B5CF6' },
  { name: 'CRITICAL', value: 14, color: '#EF4444' },
];

// ── Risk Timeline (30 days) ──
export const riskTimeline = Array.from({ length: 30 }, (_, i) => {
  const date = new Date(now - (29 - i) * 86400000);
  return {
    date: date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    safe: Math.floor(32 + Math.random() * 6),
    watchlist: Math.floor(26 + Math.random() * 6),
    suspicious: Math.floor(22 + Math.random() * 6),
    critical: Math.floor(12 + Math.random() * 5),
  };
});

// ── AI Insights Feed ──
export const aiInsights = [
  { id: 1, type: 'critical', title: 'Risk Spike Detected', time: ago(2), description: '17 newly activated accounts show rapid fund movement patterns. Possible mule recruitment wave in progress.', action: 'Investigate Cluster', icon: 'AlertTriangle' },
  { id: 2, type: 'warning', title: 'Behavioral Anomaly', time: ago(15), description: 'Cluster of 43 accounts share identical transaction timing signatures across 3 different banks. Network effect likely.', action: 'View Pattern', icon: 'Activity' },
  { id: 3, type: 'info', title: 'Model Confidence Update', time: ago(45), description: 'Ensemble model confidence improved by 2.1% after incorporating latest behavioral data. 89 accounts reclassified.', action: 'View Details', icon: 'TrendingUp' },
  { id: 4, type: 'critical', title: 'Velocity Breach', time: ago(60), description: 'ACC-481927 exceeded 5x normal velocity threshold. ₹15.2L moved through account in 4 hours.', action: 'View Account', icon: 'Zap' },
  { id: 5, type: 'warning', title: 'Dormancy Activation Alert', time: ago(120), description: '8 dormant accounts (>180 days inactive) simultaneously activated and received identical deposit amounts.', action: 'Investigate', icon: 'Clock' },
];

// ── Alerts ──
export const alerts = [
  { id: 'ALT-2847', accountId: 'ACC-847291', priority: 'CRITICAL', timestamp: ago(2), riskScore: 94, confidence: 97.3, trigger: 'Risk threshold breach (>80) combined with velocity spike and behavioral pattern match', evidence: ['F527 = 4.2x above account mean', 'F1692 matches confirmed mule template', 'Isolation Forest anomaly score: 0.94'], status: 'active' },
  { id: 'ALT-2846', accountId: 'ACC-481927', priority: 'CRITICAL', timestamp: ago(5), riskScore: 92, confidence: 96.4, trigger: 'Velocity spike detected — ₹15.2L moved in 4 hours', evidence: ['Transaction velocity 5.1x above normal', 'Outflow ratio: 0.97 (near complete pass-through)', 'Network connection to 3 flagged accounts'], status: 'active' },
  { id: 'ALT-2845', accountId: 'ACC-619283', priority: 'CRITICAL', timestamp: ago(8), riskScore: 91, confidence: 95.8, trigger: 'Multiple high-risk signals converged', evidence: ['Behavioral pattern 91% match to mule template', 'Dormancy reactivation after 147 days', 'Connected to known fraud cluster #4'], status: 'active' },
  { id: 'ALT-2844', accountId: 'ACC-738291', priority: 'HIGH', timestamp: ago(12), riskScore: 87, confidence: 93.7, trigger: 'Rapid risk score escalation (+32 points in 7 days)', evidence: ['F3043 outflow dominance ratio: 0.91', 'New connections to 5 suspicious accounts', 'Transaction frequency 3.8x above baseline'], status: 'active' },
  { id: 'ALT-2843', accountId: 'ACC-839174', priority: 'HIGH', timestamp: ago(18), riskScore: 89, confidence: 94.5, trigger: 'Behavioral anomaly combined with network risk', evidence: ['Anomaly score 0.91 (top 1.2%)', 'Network risk composite 0.84', 'Fund concentration from 2 sources only'], status: 'active' },
  { id: 'ALT-2842', accountId: 'ACC-927184', priority: 'HIGH', timestamp: ago(25), riskScore: 83, confidence: 91.2, trigger: 'Velocity spike with mule pattern characteristics', evidence: ['23 transactions in 48 hours', '94% outward transfer within 6 hours', 'Matches FATF mule typology pattern'], status: 'active' },
  { id: 'ALT-2841', accountId: 'ACC-291847', priority: 'MEDIUM', timestamp: ago(35), riskScore: 81, confidence: 89.1, trigger: 'Risk score crossed suspicious threshold', evidence: ['Outflow dominance increasing trend', 'Partial mule pattern match (72%)', 'Connected to watchlisted accounts'], status: 'active' },
  { id: 'ALT-2840', accountId: 'ACC-174829', priority: 'MEDIUM', timestamp: ago(42), riskScore: 77, confidence: 86.1, trigger: 'Network exposure and velocity increase', evidence: ['3 new connections to flagged accounts', 'Transaction velocity +2.4x above mean', 'Account behavior deviation 68th percentile'], status: 'active' },
  { id: 'ALT-2839', accountId: 'ACC-482916', priority: 'MEDIUM', timestamp: ago(55), riskScore: 76, confidence: 85.4, trigger: 'Cluster assignment changed to suspicious group', evidence: ['Moved from Cluster 2 to Cluster 3', 'Transaction timing signature changed', 'Inflow source diversity decreased'], status: 'active' },
  { id: 'ALT-2838', accountId: 'ACC-642819', priority: 'MEDIUM', timestamp: ago(68), riskScore: 72, confidence: 84.3, trigger: 'Multiple moderate risk signals', evidence: ['Velocity ratio 2.8x', 'Small transaction frequency spike', 'Behavioral deviation increasing'], status: 'active' },
  { id: 'ALT-2837', accountId: 'ACC-472918', priority: 'LOW', timestamp: ago(85), riskScore: 45, confidence: 72.1, trigger: 'Watchlist threshold approached', evidence: ['Risk score trending upward (+8 in 7 days)', 'New transaction pattern emerging', 'Monitoring recommended'], status: 'active' },
  { id: 'ALT-2836', accountId: 'ACC-293847', priority: 'LOW', timestamp: ago(120), riskScore: 38, confidence: 68.4, trigger: 'Minor behavioral change detected', evidence: ['Transaction frequency slightly elevated', 'New recipient added', 'Within normal variance'], status: 'active' },
];

// ── Risk Score History (30 days for ACC-847291) ──
export const riskScoreHistory = {
  'ACC-847291': Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    date: new Date(now - (29 - i) * 86400000).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    score: i < 15 ? Math.floor(35 + i * 2 + Math.random() * 5) : Math.floor(60 + (i - 15) * 2.3 + Math.random() * 3),
  })),
};

export function getRiskHistory(accountId) {
  if (riskScoreHistory[accountId]) return riskScoreHistory[accountId];
  const account = accounts.find(a => a.id === accountId);
  const finalScore = account?.riskScore || 50;
  return Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    date: new Date(now - (29 - i) * 86400000).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    score: Math.floor((finalScore * 0.4) + (finalScore * 0.6 * (i / 29)) + (Math.random() * 8 - 4)),
  }));
}

// ── Risk Score Breakdown ──
export const riskBreakdown = {
  'ACC-847291': {
    lgbmProbability: 0.96, lgbmWeight: 0.40, lgbmContribution: 38.4,
    anomalyScore: 0.92, anomalyWeight: 0.30, anomalyContribution: 27.6,
    behavioralRisk: 0.88, behavioralWeight: 0.20, behavioralContribution: 17.6,
    networkRisk: 0.74, networkWeight: 0.10, networkContribution: 7.4,
    penaltyVelocitySpike: 3.0,
    penaltyDormancyActivation: 0.0,
    penaltyNetworkCluster: 0.0,
    finalScore: 94.0,
  },
};

export function getRiskBreakdown(accountId) {
  if (riskBreakdown[accountId]) return riskBreakdown[accountId];
  const account = accounts.find(a => a.id === accountId);
  const s = (account?.riskScore || 50) / 100;
  return {
    lgbmProbability: +(s * 1.02).toFixed(2), lgbmWeight: 0.40, lgbmContribution: +(s * 40).toFixed(1),
    anomalyScore: +(s * 0.96).toFixed(2), anomalyWeight: 0.30, anomalyContribution: +(s * 29).toFixed(1),
    behavioralRisk: +(s * 0.92).toFixed(2), behavioralWeight: 0.20, behavioralContribution: +(s * 18).toFixed(1),
    networkRisk: +(s * 0.78).toFixed(2), networkWeight: 0.10, networkContribution: +(s * 8).toFixed(1),
    penaltyVelocitySpike: s > 0.7 ? 3.0 : 0,
    penaltyDormancyActivation: s > 0.85 ? 2.0 : 0,
    penaltyNetworkCluster: 0,
    finalScore: account?.riskScore || 50,
  };
}

// ── Future Risk Prediction ──
export const futurePrediction = {
  'ACC-847291': { today: 94, day1: 95, day3: 96, day7: 97, trend: 'Escalating', confidence: 3, recommendation: 'IMMEDIATE ACTION REQUIRED' },
};

export function getFuturePrediction(accountId) {
  if (futurePrediction[accountId]) return futurePrediction[accountId];
  const account = accounts.find(a => a.id === accountId);
  const s = account?.riskScore || 50;
  const trend = s > 70 ? 'Escalating' : s > 40 ? 'Stable' : 'Declining';
  return {
    today: s, day1: Math.min(s + 1, 100), day3: Math.min(s + 2, 100), day7: Math.min(s + 3, 100),
    trend, confidence: 3,
    recommendation: s > 80 ? 'IMMEDIATE ACTION REQUIRED' : s > 60 ? 'ENHANCED MONITORING' : 'STANDARD MONITORING',
  };
}

// ── Transaction Trend (30 days) ──
export function getTransactionTrend(accountId) {
  const account = accounts.find(a => a.id === accountId);
  const f = (account?.riskScore || 50) / 100;
  return Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    date: new Date(now - (29 - i) * 86400000).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }),
    volume: Math.floor((f * 800000) + Math.random() * 200000 + (i > 20 ? f * 500000 : 0)),
    count: Math.floor((f * 15) + Math.random() * 8 + (i > 20 ? f * 10 : 0)),
  }));
}

// ── Anomaly Detection Results ──
export const anomalyModels = [
  { name: 'Isolation Forest', anomalies: 1247, threshold: 0.65, precision: 0.89, recall: 0.84, icon: 'TreePine' },
  { name: 'Autoencoder', anomalies: 1089, threshold: 0.08, precision: 0.86, recall: 0.81, icon: 'Brain' },
  { name: 'Local Outlier Factor', anomalies: 1183, threshold: 1.5, precision: 0.83, recall: 0.79, icon: 'Target' },
];

export const anomalyScatter = Array.from({ length: 200 }, (_, i) => {
  const isAnomaly = i < 40;
  const severity = isAnomaly ? (i < 10 ? 'critical' : i < 20 ? 'high' : i < 30 ? 'medium' : 'low') : 'normal';
  return {
    id: `ACC-${100000 + i}`,
    x: isAnomaly ? (Math.random() * 4 + 3) : (Math.random() * 6 - 3),
    y: isAnomaly ? (Math.random() * 4 + 2) : (Math.random() * 6 - 3),
    severity,
    ifScore: isAnomaly ? +(0.65 + Math.random() * 0.35).toFixed(2) : +(Math.random() * 0.5).toFixed(2),
    aeScore: isAnomaly ? +(0.60 + Math.random() * 0.40).toFixed(2) : +(Math.random() * 0.45).toFixed(2),
    lofScore: isAnomaly ? +(0.55 + Math.random() * 0.45).toFixed(2) : +(Math.random() * 0.40).toFixed(2),
    combined: isAnomaly ? +(0.65 + Math.random() * 0.35).toFixed(2) : +(Math.random() * 0.40).toFixed(2),
  };
});

export const anomalyRankings = anomalyScatter
  .filter(a => a.severity !== 'normal')
  .sort((a, b) => b.combined - a.combined)
  .slice(0, 15)
  .map((a, i) => ({ ...a, rank: i + 1 }));

// ── Global SHAP Feature Importance ──
export const globalFeatureImportance = [
  { feature: 'F527', importance: 0.342, label: 'Transaction velocity' },
  { feature: 'F1692', importance: 0.298, label: 'Mule behavior pattern' },
  { feature: 'F3043', importance: 0.271, label: 'Rapid fund outflow' },
  { feature: 'F3894', importance: 0.245, label: 'Anomaly detection signal' },
  { feature: 'F321', importance: 0.218, label: 'Fund concentration' },
  { feature: 'F2082', importance: 0.194, label: 'High-freq small transactions' },
  { feature: 'F2678', importance: 0.178, label: 'Network centrality' },
  { feature: 'F2737', importance: 0.162, label: 'Dormancy period' },
  { feature: 'F531', importance: 0.149, label: 'Transaction frequency burst' },
  { feature: 'F3887', importance: 0.138, label: 'Network risk signal 1' },
  { feature: 'F2122', importance: 0.125, label: 'Behavioral deviation' },
  { feature: 'F670', importance: 0.112, label: 'Account age factor' },
  { feature: 'F3889', importance: 0.098, label: 'Network risk signal 2' },
  { feature: 'F2956', importance: 0.087, label: 'Inflow volume' },
  { feature: 'F115', importance: 0.076, label: 'Balance stability' },
  { feature: 'velocity_ratio', importance: 0.068, label: 'Velocity ratio' },
  { feature: 'F3836', importance: 0.059, label: 'Cross-bank transfers' },
  { feature: 'F2582', importance: 0.051, label: 'Pattern consistency' },
  { feature: 'F3891', importance: 0.044, label: 'Network risk signal 3' },
  { feature: 'outflow_dominance', importance: 0.038, label: 'Outflow dominance' },
];

// ── Cluster Data ──
export const clusters = [
  { id: 1, name: 'Low-risk behavioral segment', count: 847, color: '#3B82F6', risk: 'LOW', confidence: 0.94, features: ['Stable transaction patterns', 'Consistent balance levels', 'Long account history', 'Diverse transaction recipients'] },
  { id: 2, name: 'Dormant account pattern', count: 234, color: '#F59E0B', risk: 'MEDIUM', confidence: 0.87, features: ['Extended inactivity periods', 'Recent reactivation signals', 'Small initial deposits', 'Limited transaction history'] },
  { id: 3, name: 'Rapid-transfer signature', count: 189, color: '#8B5CF6', risk: 'HIGH', confidence: 0.91, features: ['High F527 (velocity)', 'Rapid outflow patterns', 'Multiple recipients', 'Short holding periods'] },
  { id: 4, name: 'High-velocity pass-through', count: 67, color: '#EF4444', risk: 'CRITICAL', confidence: 0.91, features: ['High F527 (velocity)', 'Low F321 (source diversity)', 'Spike in F3043 (outflows)', 'Short account lifespan'] },
  { id: 5, name: 'Emerging unknown pattern', count: 23, color: '#6B7280', risk: 'REVIEW', confidence: 0.72, features: ['Novel transaction topology', 'Cross-bank connections', 'Unusual timing patterns', 'Requires manual review'] },
];

export const clusterScatter = [];
clusters.forEach(cluster => {
  const cx = cluster.id * 2.5 - 3;
  const cy = cluster.id * 1.8 - 4;
  for (let i = 0; i < Math.min(cluster.count, 50); i++) {
    clusterScatter.push({
      x: cx + (Math.random() * 3 - 1.5),
      y: cy + (Math.random() * 3 - 1.5),
      cluster: cluster.id,
      color: cluster.color,
      accountId: `ACC-${cluster.id}${String(i).padStart(4, '0')}`,
    });
  }
});

// ── Model Performance Metrics ──
export const modelMetrics = {
  accuracy: { value: 96.4, trend: '+0.3%' },
  precision: { value: 94.1, trend: '+0.5%' },
  recall: { value: 93.8, trend: '+0.2%' },
  f1Score: { value: 93.9, trend: '+0.4%' },
  rocAuc: { value: 0.987, trend: '+0.002' },
  prAuc: { value: 0.981, trend: '+0.003' },
};

export const confusionMatrix = {
  trueNegative: 41847,
  falsePositive: 487,
  falseNegative: 291,
  truePositive: 5184,
  fpr: 1.15,
  fnr: 5.31,
};

export const rocCurve = Array.from({ length: 50 }, (_, i) => {
  const fpr = i / 49;
  const tpr = Math.min(1, Math.pow(fpr, 0.15));
  return { fpr: +fpr.toFixed(3), tpr: +tpr.toFixed(3) };
});

export const baseModels = [
  { name: 'LightGBM', weight: 0.34, auc: 0.981 },
  { name: 'XGBoost', weight: 0.28, auc: 0.978 },
  { name: 'CatBoost', weight: 0.27, auc: 0.979 },
  { name: 'Random Forest', weight: 0.11, auc: 0.967 },
];

export const modelHealth = {
  status: 'HEALTHY',
  dataDrift: { level: 'Low', score: 0.82, action: 'No action needed' },
  conceptDrift: { level: 'Low', score: 0.85, action: 'No action needed' },
  predictionDist: { level: 'Stable', score: 0.88, action: 'No action needed' },
  lastRetrain: '3 days ago',
  nextScheduled: '7 days',
};

// ── Copilot Mock Responses ──
export const copilotResponses = {
  'why is ACC-847291 flagged': `Account **ACC-847291** has been classified as a **CRITICAL** mule account with **97.3% confidence**. Here's the breakdown:

**PRIMARY EVIDENCE:**
• **Transaction Velocity (F527):** 4.2× above branch average — the account received ₹8.4L across 23 transactions in 48 hours, then transferred 94% outward within 6 hours. Classic pass-through behavior.

• **Behavioral Pattern Match (F1692):** 87% similarity to confirmed mule accounts in training data. The inflow-then-rapid-outflow signature matches FATF typology for third-party mule accounts.

• **Anomaly Score:** 0.94/1.00 (Isolation Forest) — places this account in the top 0.8% of all accounts by behavioral deviation.

**RISK FACTORS SUMMARY:**
| Feature | SHAP Value | Impact |
|---------|-----------|--------|
| F527 | +0.42 | Velocity spike |
| F1692 | +0.31 | Mule pattern match |
| F3043 | +0.24 | Rapid outflow |
| F3894 | +0.19 | Anomaly confirmed |

**RECOMMENDATION:** FREEZE ACCOUNT immediately and escalate to the Financial Intelligence Unit. Document under PMLA Section 12 and file an STR with FIU-IND within 7 working days.

*Confidence: 97.3% | Model: Stacking Ensemble*`,

  'generate report': `# MULENET AI INVESTIGATION REPORT
---
**Account:** ACC-847291 | **Date:** ${new Date().toLocaleDateString('en-IN')} | **Analyst:** Ayush S.
**Risk Score:** 94/100 | **Classification:** CRITICAL | **Confidence:** 97.3%

## EXECUTIVE SUMMARY
Account ACC-847291 exhibits strong indicators of mule account behavior with a risk score of 94/100. The account shows classic pass-through patterns with high-velocity fund movement and rapid outflow, matching confirmed mule account templates with 87% similarity.

## RISK ASSESSMENT
- ⚠️ Risk score in CRITICAL zone (>80) for 12 consecutive days
- ⚠️ Transaction velocity 4.2× above branch average
- ⚠️ Outflow-to-inflow ratio of 0.94 (near-complete pass-through)
- ⚠️ Connected to 3 other flagged accounts in fraud network

## BEHAVIORAL ANALYSIS
- 23 transactions received in 48-hour window
- 94% of funds transferred outward within 6 hours
- Multiple recipients across different banks
- Transaction timing suggests automated behavior

## SHAP EVIDENCE
1. **F527 (+0.42):** Unusually high transaction velocity
2. **F1692 (+0.31):** Matches historical mule behavior
3. **F3043 (+0.24):** Rapid fund outflow pattern
4. **F3894 (+0.19):** Strong anomaly detection signal
5. **F321 (+0.17):** Concentrated fund sources

## RECOMMENDED ACTION
**FREEZE ACCOUNT** and escalate to FIU-IND. File STR under PMLA Section 12.

**CONFIDENCE LEVEL: 97.3%**`,

  'summarize alerts': `## Today's Alert Summary

📊 **Active Alerts: 342**

### By Priority:
| Priority | Count | Change |
|----------|-------|--------|
| 🔴 Critical | 47 | +5 today |
| 🟠 High | 128 | +12 today |
| 🟡 Medium | 101 | +3 today |
| 🟢 Low | 66 | -2 today |

### Top Critical Alerts:
1. **ALT-2847** — ACC-847291 — Risk 94 — Velocity spike + mule pattern
2. **ALT-2846** — ACC-481927 — Risk 92 — ₹15.2L moved in 4 hours
3. **ALT-2845** — ACC-619283 — Risk 91 — Multiple converging signals

### Key Trends:
- 🔺 17 new accounts flagged in last 24 hours
- 🔺 Velocity-based alerts up 34% vs. last week
- 🔺 Cluster 4 (known mule pattern) grew by 8 accounts
- ✅ 12 investigations closed, 8 confirmed as fraud

**Recommendation:** Focus on Cluster 4 growth and velocity-based alerts. Consider batch investigation for the 17 newly flagged accounts.`,

  'default': `I've analyzed the available data. Here's what I found:

Based on the current risk landscape, there are **342 active alerts** across the monitored accounts. The most concerning pattern is the recent spike in velocity-based alerts, which are up 34% compared to last week.

**Key observations:**
- 47 critical accounts require immediate attention
- Cluster 4 (known mule pattern) continues to grow
- Average risk score has increased by 2.1 points

Would you like me to:
- Deep dive into a specific account?
- Generate an investigation report?
- Analyze a particular fraud pattern?
- Summarize the alert queue?`,
};

// ── Landing Page Statistics ──
export const landingStats = [
  { label: 'Accounts Monitored', value: 247831 },
  { label: 'Suspicious', value: 4219 },
  { label: 'Fraud Nets', value: 147 },
  { label: 'Loss Prevented', value: '₹12.3 Cr' },
  { label: 'Avg Confidence', value: '94.7%' },
];

// ── Geographic Risk (Indian States) ──
export const geoRiskData = [
  { state: 'Maharashtra', risk: 78, accounts: 4821 },
  { state: 'Delhi', risk: 72, accounts: 3247 },
  { state: 'Tamil Nadu', risk: 65, accounts: 2891 },
  { state: 'Karnataka', risk: 61, accounts: 2654 },
  { state: 'Telangana', risk: 68, accounts: 2198 },
  { state: 'West Bengal', risk: 58, accounts: 1876 },
  { state: 'Gujarat', risk: 45, accounts: 1654 },
  { state: 'Rajasthan', risk: 42, accounts: 1432 },
  { state: 'Uttar Pradesh', risk: 55, accounts: 1987 },
  { state: 'Kerala', risk: 38, accounts: 1123 },
  { state: 'Madhya Pradesh', risk: 35, accounts: 987 },
  { state: 'Punjab', risk: 48, accounts: 1245 },
];
