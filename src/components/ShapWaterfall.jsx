import React from 'react';
import ReactECharts from 'echarts-for-react';
import { getFeatureLabel } from '../lib/utils';

export default function ShapWaterfall({ features = [] }) {
  // Sort features by impact (absolute value) desc
  const sorted = [...features].sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  
  const yData = sorted.map(f => getFeatureLabel(f.feature));
  const seriesData = sorted.map(f => {
    return {
      value: f.value,
      itemStyle: {
        color: f.direction === 'risk' ? '#EF4444' : '#10B981',
        borderRadius: 4
      }
    };
  });

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderWidth: 0,
      textStyle: { color: '#fff', fontSize: 12 },
      formatter: function (params) {
        const item = params[0];
        const label = item.name;
        const val = item.value;
        const impact = val > 0 ? `Risk contribution: +${val.toFixed(2)}` : `Risk reduction: ${val.toFixed(2)}`;
        return `<b>${label}</b><br/>${impact}`;
      }
    },
    grid: {
      left: '3%',
      right: '8%',
      top: '4%',
      bottom: '4%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      position: 'top',
      splitLine: {
        lineStyle: { type: 'dashed', color: '#e2e8f0' }
      },
      axisLabel: {
        formatter: '{value}',
        color: '#64748b',
        fontWeight: 600,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'category',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#475569',
        fontWeight: 600,
        fontSize: 10,
        width: 140,
        overflow: 'truncate'
      },
      data: yData,
      inverse: true
    },
    series: [
      {
        name: 'SHAP Value',
        type: 'bar',
        barWidth: 14,
        data: seriesData
      }
    ]
  };

  return (
    <div style={{ width: '100%', height: '240px' }}>
      <ReactECharts 
        option={option} 
        style={{ height: '100%', width: '100%' }}
        opts={{ notMerge: true }}
      />
    </div>
  );
}
