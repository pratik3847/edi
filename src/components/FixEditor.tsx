import React, { useState, useEffect } from 'react';

interface FixEditorProps {
  segmentId: string;
  elementIndex: number;
  currentValue: string;
  onApply: (newValue: string) => void;
  onCancel: () => void;
}

export default function FixEditor({ segmentId, elementIndex, currentValue, onApply, onCancel }: FixEditorProps) {
  const [value, setValue] = useState(currentValue);

  // Reset local state if the selected element changes externally
  useEffect(() => {
    setValue(currentValue);
  }, [segmentId, elementIndex, currentValue]);

  return (
    <div className="bg-[rgba(10,10,12,0.95)] backdrop-blur-xl border border-accentBlue/40 shadow-[0_30px_60px_rgba(0,0,0,0.8),0_0_30px_rgba(0,80,255,0.15)] rounded-2xl p-6 fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-md z-50 animate-in slide-in-from-bottom-10 fade-in duration-300">
      
      <div className="flex justify-between items-center mb-4">
        <h4 className="text-white font-bold flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accentBlue"></span>
          Fixing <span className="font-mono text-accentBlue opacity-80 bg-accentBlue/10 px-2 py-0.5 rounded">{segmentId}0{elementIndex + 1}</span>
        </h4>
        <button onClick={onCancel} className="text-gray-500 hover:text-white transition">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex flex-col gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wider">Original Value</label>
          <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 font-mono text-sm text-gray-400 opacity-60 line-through">
            {currentValue || 'EMPTY'}
          </div>
        </div>

        <div>
           <label className="block text-xs font-semibold text-accentBlue mb-1 uppercase tracking-wider">New Value</label>
           <input 
             type="text" 
             value={value}
             onChange={(e) => setValue(e.target.value)}
             className="w-full px-4 py-3 rounded-xl bg-[rgba(0,80,255,0.05)] border border-accentBlue/50 text-white font-mono text-lg focus:outline-none focus:border-accentBlue focus:shadow-[0_0_20px_rgba(0,80,255,0.3)] transition-all"
             autoFocus
           />
        </div>

        <div className="flex gap-3 mt-2">
          <button 
            className="flex-1 py-3 rounded-xl border border-gray-600 text-white hover:bg-white/5 transition font-semibold"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button 
            className="flex-1 py-3 rounded-xl bg-accentGreen hover:bg-[#2eaa4c] text-black transition font-bold shadow-[0_0_20px_rgba(52,199,89,0.3)]"
            onClick={() => onApply(value)}
          >
            Apply Fix
          </button>
        </div>
      </div>
    </div>
  );
}
