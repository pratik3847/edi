import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function UploadCard() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = () => {
    if (!file) return;
    setIsProcessing(true);
    
    // Simulate upload delay and redirect to mock session
    setTimeout(() => {
      setIsProcessing(false);
      navigate('/session/sess_mock_1234');
    }, 1500);
  };

  return (
    <div 
      className={`relative w-full max-w-2xl mx-auto rounded-3xl border transition-all duration-300 ${
        isDragging 
          ? 'border-accentCyan bg-[rgba(0,214,255,0.05)] shadow-[0_0_30px_rgba(0,214,255,0.2)]' 
          : 'border-[rgba(255,255,255,0.1)] bg-[rgba(10,10,12,0.6)]'
      } backdrop-blur-xl p-10 text-center flex flex-col items-center justify-center min-h-[300px]`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {!file ? (
        <>
          <div className="w-16 h-16 rounded-full bg-[rgba(255,255,255,0.05)] flex items-center justify-center mb-6">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">Upload EDI File</h3>
          <p className="text-gray-400 mb-6">Drag and drop your .edi, .txt, or .json file here, or click to browse.</p>
          <label className="btn btn-primary cursor-pointer">
            Browse Files
            <input type="file" className="hidden" onChange={(e) => e.target.files && setFile(e.target.files[0])} />
          </label>
        </>
      ) : (
        <>
          <div className="w-16 h-16 rounded-full bg-accentBlue/20 flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(0,80,255,0.3)]">
            <svg className="w-8 h-8 text-accentBlue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">{file.name}</h3>
          <p className="text-gray-400 mb-8">{(file.size / 1024).toFixed(1)} KB</p>
          
          <div className="flex gap-4">
            <button 
              className="px-6 py-2 rounded-full border border-gray-600 text-white hover:bg-white/10 transition"
              onClick={() => setFile(null)}
              disabled={isProcessing}
            >
              Cancel
            </button>
            <button 
              className="btn btn-primary min-w-[120px]"
              onClick={handleUpload}
              disabled={isProcessing}
            >
              {isProcessing ? 'Parsing...' : 'Analyze File'}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
