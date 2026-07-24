/* ── Utility Functions for MuleNet AI ── */

/**
 * Format number in Indian numbering system (e.g., 2,47,831)
 */
export function formatIndianNumber(num) {
  if (num == null) return '0';
  const str = Math.floor(num).toString();
  if (str.length <= 3) return str;
  
  let lastThree = str.substring(str.length - 3);
  let rest = str.substring(0, str.length - 3);
  if (rest !== '') {
    lastThree = ',' + lastThree;
  }
  return rest.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;
}

/**
 * Format currency in Indian style (₹12.3 Cr, ₹4.5 L, etc.)
 */
export function formatIndianCurrency(amount) {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)} Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)} L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount}`;
}

/**
 * Get risk classification from score
 */
export function getRiskClassification(score) {
  if (score <= 20) return 'SAFE';
  if (score <= 50) return 'WATCHLIST';
  if (score <= 80) return 'SUSPICIOUS';
  return 'CRITICAL';
}

/**
 * Get risk color based on classification
 */
export function getRiskColor(classification) {
  const colors = {
    SAFE: '#10B981',
    WATCHLIST: '#F59E0B',
    SUSPICIOUS: '#8B5CF6',
    CRITICAL: '#EF4444',
  };
  return colors[classification] || colors.SAFE;
}

/**
 * Get risk background color
 */
export function getRiskBg(classification) {
  const bgs = {
    SAFE: '#ECFDF5',
    WATCHLIST: '#FFFBEB',
    SUSPICIOUS: '#F5F3FF',
    CRITICAL: '#FEF2F2',
  };
  return bgs[classification] || bgs.SAFE;
}

/**
 * Get risk CSS class suffix
 */
export function getRiskClass(classification) {
  return classification?.toLowerCase() || 'safe';
}

/**
 * Format time ago string
 */
export function timeAgo(date) {
  const now = new Date();
  const d = new Date(date);
  const seconds = Math.floor((now - d) / 1000);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return d.toLocaleDateString('en-IN');
}

/**
 * Animated counter hook data generator
 */
export function animateValue(start, end, duration, callback) {
  const startTime = performance.now();
  
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (end - start) * eased);
    
    callback(current);
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  
  requestAnimationFrame(update);
}

/**
 * Generate a random ID
 */
export function generateId(prefix = 'ACC') {
  return `${prefix}-${Math.floor(100000 + Math.random() * 900000)}`;
}

/**
 * Format percentage
 */
export function formatPercent(value, decimals = 1) {
  return `${Number(value).toFixed(decimals)}%`;
}

/**
 * Format score
 */
export function formatScore(value) {
  return Number(value).toFixed(1);
}

/**
 * Clamp a value between min and max
 */
export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

/**
 * Generate sparkline data points
 */
export function generateSparkline(points = 7, min = 20, max = 80) {
  return Array.from({ length: points }, () => 
    Math.floor(Math.random() * (max - min) + min)
  );
}

/**
 * Get alert priority from risk score
 */
export function getAlertPriority(riskScore) {
  if (riskScore > 80) return 'CRITICAL';
  if (riskScore > 60) return 'HIGH';
  if (riskScore > 40) return 'MEDIUM';
  return 'LOW';
}

/**
 * Feature name to plain English mapping
 */
export const FEATURE_LABELS = {
  F115: 'Account balance stability',
  F321: 'Fund source concentration',
  F527: 'Transaction velocity',
  F531: 'Transaction frequency burst',
  F670: 'Account age factor',
  F1692: 'Mule behavior pattern match',
  F2082: 'High-frequency small transactions',
  F2122: 'Behavioral deviation index',
  F2582: 'Pattern consistency score',
  F2678: 'Network centrality measure',
  F2737: 'Dormancy period length',
  F2956: 'Inflow volume metric',
  F3043: 'Rapid fund outflow pattern',
  F3836: 'Cross-bank transfer activity',
  F3887: 'Network risk signal 1',
  F3889: 'Network risk signal 2',
  F3891: 'Network risk signal 3',
  F3894: 'Anomaly detection signal',
  velocity_ratio: 'Transaction velocity ratio',
  concentration_score: 'Fund concentration score',
  outflow_dominance: 'Outflow dominance ratio',
  dormancy_activation: 'Dormancy activation signal',
  network_risk_composite: 'Network risk composite',
  behavior_anomaly_score: 'Behavioral anomaly score',
};

/**
 * Get feature label
 */
export function getFeatureLabel(featureId) {
  return FEATURE_LABELS[featureId] || featureId;
}
