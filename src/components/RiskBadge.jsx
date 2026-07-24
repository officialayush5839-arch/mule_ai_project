import React from 'react';
import { getRiskClass } from '../lib/utils';

export default function RiskBadge({ classification }) {
  if (!classification) return null;
  
  const classSuffix = getRiskClass(classification);

  return (
    <span className={`risk-badge risk-badge--${classSuffix}`}>
      <span className={`risk-dot risk-dot--${classSuffix}`}></span>
      {classification}
    </span>
  );
}
