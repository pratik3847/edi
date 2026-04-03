import React, { useState } from 'react';

interface EDIViewerProps {
  ediString: string;
}

export default function EDIViewer({ ediString }: EDIViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(ediString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([ediString], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'corrected_output.edi';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full bg-[rgba(10,10,12,0.9)] backdrop-blur-xl border border-[rgba(255,255,255,0.05)] rounded-2xl p-6 relative group h-full flex flex-col">
      <div className="flex justify-between items-center mb-4 border-b border-[rgba(255,255,255,0.1)] pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-3">
          <span className="w-3 h-3 rounded-full bg-accentCyan shadow-[0_0_10px_rgba(0,214,255,0.5)]"></span>
          Corrected EDI Output
        </h3>
        
        <div className="flex gap-2">
          <button 
            onClick={handleCopy}
            className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-semibold text-white transition flex items-center gap-2"
          >
            {copied ? (
              <span className="text-accentGreen flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Copied
              </span>
            ) : "Copy text"}
          </button>
          
          <button 
             onClick={handleDownload}
             className="px-3 py-1.5 rounded-lg border border-accentCyan/50 text-accentCyan hover:bg-accentCyan/10 text-xs font-semibold transition"
          >
             Download .edi
          </button>
        </div>
      </div>

      <div className="flex-1 bg-black/50 border border-white/5 rounded-xl p-4 overflow-auto font-mono text-sm text-gray-300 leading-relaxed whitespace-pre-wrap break-all shadow-inner">
        {ediString || "No EDI data generated yet..."}
      </div>
    </div>
  );
}
