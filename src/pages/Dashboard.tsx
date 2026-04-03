import React from 'react';
import Navbar from '../components/Navbar';
import UploadCard from '../components/UploadCard';
import { mockRecentSessions } from '../data/mockData';

export default function Dashboard() {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed': return 'text-accentBlue bg-[rgba(0,80,255,0.1)] border-[rgba(0,80,255,0.3)]';
      case 'errors': return 'text-accentRed bg-[rgba(255,59,48,0.1)] border-[rgba(255,59,48,0.3)]';
      case 'fixed': return 'text-accentGreen bg-[rgba(52,199,89,0.1)] border-[rgba(52,199,89,0.3)]';
      default: return 'text-gray-400 bg-gray-800 border-gray-700';
    }
  };

  return (
    <>
      {/* Background Overlays - reusing global logic */}
      <div className="bg-overlay intelligence-glow opacity-30"></div>
      
      <div className="min-h-screen pt-24 px-6 md:px-12 pb-20">
        <div className="max-w-6xl mx-auto">
          
          <header className="mb-12 text-center md:text-left">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500">John</span>
            </h1>
            <p className="text-xl text-gray-400">Ready to ingest and validate your next batch of EDI data.</p>
          </header>

          <section className="mb-16">
            <UploadCard />
          </section>

          <section>
            <h3 className="text-2xl font-bold text-white mb-6">Recent Sessions</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {mockRecentSessions.map((session) => (
                <div 
                  key={session.id}
                  className="bg-[rgba(10,10,12,0.6)] backdrop-blur-md border border-[rgba(255,255,255,0.05)] rounded-2xl p-6 hover:border-[rgba(255,255,255,0.15)] transition-all cursor-pointer hover:transform hover:-translate-y-1"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                      <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(session.status)} capitalize`}>
                      {session.status}
                    </span>
                  </div>
                  <h4 className="text-lg font-semibold text-white mb-1 truncate">{session.filename}</h4>
                  <p className="text-sm text-gray-500">{session.date}</p>
                </div>
              ))}
            </div>
          </section>

        </div>
      </div>
    </>
  );
}
