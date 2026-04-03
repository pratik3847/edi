import React, { useState } from 'react';
import { EDISegment } from '../data/mockData';

interface SegmentTreeProps {
  segments: EDISegment[];
  activeErrorSegmentId: string | null;
  onElementClick: (segmentId: string, elementIndex: number, currentValue: string) => void;
  fixedSegmentIds: string[];
}

export default function SegmentTree({ segments, activeErrorSegmentId, onElementClick, fixedSegmentIds }: SegmentTreeProps) {
  return (
    <div className="w-full bg-[rgba(10,10,12,0.4)] backdrop-blur-md border border-[rgba(255,255,255,0.05)] rounded-2xl p-6 h-full overflow-y-auto">
      <h3 className="text-xl font-bold text-white mb-6 border-b border-[rgba(255,255,255,0.1)] pb-4">EDI Structure</h3>
      
      <div className="flex flex-col gap-3">
        {segments.map((seg) => {
          const hasError = activeErrorSegmentId === seg.id;
          const hasFix = fixedSegmentIds.includes(seg.id);
          
          let borderColor = 'border-[rgba(255,255,255,0.05)]';
          if (hasError) borderColor = 'border-accentRed shadow-[0_0_15px_rgba(255,59,48,0.2)] bg-[rgba(255,59,48,0.02)]';
          if (hasFix) borderColor = 'border-accentGreen shadow-[0_0_15px_rgba(52,199,89,0.2)] bg-[rgba(52,199,89,0.02)]';

          return (
            <div 
              key={seg.id} 
              className={`rounded-xl border ${borderColor} p-4 transition-all duration-300`}
            >
              <div className="flex items-center mb-3">
                <span className={`px-2 py-1 rounded bg-white/10 text-white font-mono text-sm mr-3 font-bold`}>
                  {seg.segmentId}
                </span>
                
                {hasError && <span className="text-xs font-semibold text-accentRed flex items-center"><span className="w-2 h-2 rounded-full bg-accentRed mr-2 animate-pulse"></span> Requires Attention</span>}
                {hasFix && <span className="text-xs font-semibold text-accentGreen flex items-center"><span className="w-2 h-2 rounded-full bg-accentGreen mr-2"></span> Resolved</span>}
              </div>
              
              <div className="flex flex-wrap gap-2 pl-[42px]">
                {seg.elements.map((el, idx) => (
                  <div 
                    key={idx}
                    onClick={() => onElementClick(seg.id, idx, el.value)}
                    className="flex flex-col cursor-pointer group"
                  >
                    <span className="text-[10px] text-gray-500 mb-1 ml-1 group-hover:text-accentBlue transition-colors">
                      {seg.segmentId}0{idx + 1}
                    </span>
                    <div className="px-3 py-1.5 rounded-lg bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.1)] font-mono text-sm text-gray-300 group-hover:border-accentBlue group-hover:text-white transition-all min-w-[32px] min-h-[34px] flex items-center justify-center">
                      {el.value || <span className="opacity-20">-</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
