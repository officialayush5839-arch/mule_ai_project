import React from 'react';
import ReactECharts from 'echarts-for-react';

export default function BehaviorRadar({ current = [], baseline = [] }) {
  const option = {
    color: ['#3b82f6', '#ef4444'], // Blue baseline, Red current risk
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderWidth: 0,
      textStyle: { color: '#fff', fontSize: 12 }
    },
    legend: {
      data: ['Typical Profile', 'Current Profile'],
      bottom: 0,
      icon: 'circle',
      textStyle: {
        color: '#64748b',
        fontWeight: 600,
        fontSize: 11
      }
    },
    radar: {
      indicator: [
        { name: 'Velocity (F527)', max: 100 },
        { name: 'Outflow (F3043)', max: 100 },
        { name: 'Concentration (F321)', max: 100 },
        { name: 'Pattern (F1692)', max: 100 },
        { name: 'Centrality (F2678)', max: 100 },
        { name: 'Anomaly (F3894)', max: 100 }
      ],
      center: ['50%', '42%'],
      radius: '65%',
      axisName: {
        color: '#64748b',
        fontWeight: 600,
        fontSize: 10
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(248, 250, 252, 0.4)', 'rgba(241, 245, 249, 0.4)'],
          shadowColor: 'rgba(0, 0, 0, 0.05)',
          shadowBlur: 10
        }
      },
      axisLine: {
        lineStyle: {
          color: '#e2e8f0'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0'
        }
      }
    },
    series: [
      {
        name: 'Behavioral Deviation Radar',
        type: 'radar',
        data: [
          {
            value: baseline,
            name: 'Typical Profile',
            areaStyle: {
              color: 'rgba(59, 130, 246, 0.15)'
            },
            lineStyle: {
              type: 'dashed',
              width: 1.5
            },
            itemStyle: {
              opacity: 0
            }
          },
          {
            value: current,
            name: 'Current Profile',
            areaStyle: {
              color: 'rgba(239, 68, 68, 0.25)'
            },
            lineStyle: {
              width: 2.5
            },
            itemStyle: {
              color: '#ef4444'
            }
          }
        ]
      }
    ]
  };

  return (
    <div style={{ width: '100%', height: '230px' }}>
      <ReactECharts 
        option={option} 
        style={{ height: '100%', width: '100%' }}
        opts={{ notMerge: true }}
      />
    </div>
  );
}
