import React from 'react';
import { EDIError } from '../data/mockData';

interface ErrorPanelProps {
  errors: EDIError[];
  onSelectError: (errorId: string, segmentId: string) => void;
  activeErrorId: string | null;
}

export default function ErrorPanel({ errors, onSelectError, activeErrorId }: ErrorPanelProps) {
  if (errors.length === 0) {
    return (
      <div className="bg-[rgba(10,10,12,0.4)] backdrop-blur-md border border-[rgba(255,255,255,0.05)] rounded-2xl p-6 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
        <div className="w-16 h-16 rounded-full bg-accentGreen/20 flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-accentGreen" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h4 className="text-xl font-bold text-white mb-2">No Errors Found</h4>
        <p className="text-gray-400 text-sm"> This file passed validation dynamically. </p>
      </div>
    );
  }

  return (
    <div className="bg-[rgba(10,10,12,0.4)] backdrop-blur-md border border-accentRed/30 shadow-[0_0_20px_rgba(255,59,48,0.05)] rounded-2xl p-6 h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-6 border-b border-[rgba(255,255,255,0.1)] pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-3">
          <span className="w-3 h-3 rounded-full bg-accentRed animate-pulse"></span>
          Validation Errors
        </h3>
        <span className="px-3 py-1 rounded-full bg-accentRed/20 text-accentRed font-bold text-xs">{errors.length} detected</span>
      </div>

      <div className="flex flex-col gap-4">
        {errors.map((err) => (
          <div 
            key={err.id}
            onClick={() => onSelectError(err.id, err.segmentId)}
            className={`cursor-pointer rounded-xl p-4 transition-all duration-200 border ${
              activeErrorId === err.id 
                ? 'border-accentRed bg-accentRed/10' 
                : 'border-[rgba(255,255,255,0.05)] bg-[rgba(255,255,255,0.02)] hover:border-accentRed/50 hover:bg-accentRed/5'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-accentRed/20 flex items-center justify-center flex-shrink-0 mt-1">
                <span className="text-accentRed font-bold text-xs">!</span>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 rounded bg-white/10 text-white font-mono text-[10px] font-bold">
                    {err.segmentName}
                  </span>
                  <span className="text-[10px] uppercase font-bold tracking-wider text-accentRed">
                    {err.severity} severity
                  </span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">{err.message}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
