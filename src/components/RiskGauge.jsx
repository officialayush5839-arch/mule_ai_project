import React from 'react';
import ReactECharts from 'echarts-for-react';
import { getRiskColor, getRiskClassification } from '../lib/utils';

export default function RiskGauge({ score = 0 }) {
  const classification = getRiskClassification(score);
  const color = getRiskColor(classification);

  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        radius: '100%',
        center: ['50%', '70%'],
        pointer: {
          show: true,
          width: 5,
          length: '70%',
          itemStyle: {
            color: '#1e293b'
          }
        },
        progress: {
          show: true,
          overlap: false,
          roundCap: true,
          itemStyle: {
            color: color
          }
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 12,
            color: [[1, '#e2e8f0']]
          }
        },
        splitLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          show: true,
          distance: -20,
          formatter: function (value) {
            if (value === 0) return 'SAFE';
            if (value === 50) return 'WATCH';
            if (value === 100) return 'CRIT';
            return '';
          },
          color: '#94a3b8',
          fontSize: 10,
          fontWeight: 600
        },
        data: [
          {
            value: score,
            name: classification
          }
        ],
        title: {
          show: true,
          offsetCenter: [0, '25%'],
          fontSize: 12,
          fontWeight: 700,
          color: color,
          fontFamily: 'Inter'
        },
        detail: {
          show: true,
          offsetCenter: [0, '-10%'],
          valueAnimation: true,
          formatter: function (value) {
            return Math.round(value) + '';
          },
          fontSize: 32,
          fontWeight: 800,
          color: '#0f172a',
          fontFamily: 'JetBrains Mono'
        }
      }
    ]
  };

  return (
    <div className="gauge-container" style={{ width: '100%', height: '140px', position: 'relative' }}>
      <ReactECharts 
        option={option} 
        style={{ height: '100%', width: '100%' }}
        opts={{ notMerge: true }} 
      />
    </div>
  );
}
