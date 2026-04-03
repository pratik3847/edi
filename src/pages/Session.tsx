import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import SegmentTree from '../components/SegmentTree';
import ErrorPanel from '../components/ErrorPanel';
import FixEditor from '../components/FixEditor';
import EDIViewer from '../components/EDIViewer';
import AIChatPanel from '../components/AIChatPanel';
import { mockSession, mockErrors } from '../data/mockData';

export default function SessionPage() {
  const [activeErrorId, setActiveErrorId] = useState<string | null>(null);
  const [activeSegmentId, setActiveSegmentId] = useState<string | null>(null);
  const [fixedSegments, setFixedSegments] = useState<string[]>([]);
  const [showEDIViewer, setShowEDIViewer] = useState(false);
  
  // Fix overlay state
  const [editingElement, setEditingElement] = useState<{
    segmentId: string, 
    elementIndex: number, 
    value: string
  } | null>(null);

  // Mocks representing live manipulation array
  const [liveSegments, setLiveSegments] = useState(mockSession.segments);
  const [liveErrors, setLiveErrors] = useState(mockErrors);

  const handleSelectError = (errorId: string, segmentId: string) => {
    setActiveErrorId(errorId);
    setActiveSegmentId(segmentId);
  };

  const handleElementClick = (segmentId: string, elementIndex: number, currentValue: string) => {
    setEditingElement({ segmentId, elementIndex, value: currentValue });
  };

  const handleApplyFix = (newValue: string) => {
    if (!editingElement) return;

    // Apply mutation natively to mock state avoiding backend syncs for now
    const updatedSegments = liveSegments.map(seg => {
      if (seg.id === editingElement.segmentId) {
         const newElements = [...seg.elements];
         newElements[editingElement.elementIndex] = { value: newValue };
         return { ...seg, elements: newElements };
      }
      return seg;
    });

    setLiveSegments(updatedSegments);
    setFixedSegments(prev => [...prev, editingElement.segmentId]);
    
    // Clear out errors loosely matching segment
    setLiveErrors(prev => prev.filter(err => err.segmentId !== editingElement.segmentId));
    
    // Unset overlay
    setEditingElement(null);
    setActiveErrorId(null);
    setActiveSegmentId(null);
  };

  const generatedEDIString = liveSegments.map(seg => {
    const vals = seg.elements.map(el => el.value);
    return `${seg.segmentId}*${vals.join('*')}~`;
  }).join('\n');

  return (
    <>
      <div className="bg-overlay base-dim opacity-80"></div>
      {activeErrorId && <div className="bg-overlay validation-glow opacity-50 transition-opacity duration-500"></div>}
      
      <div className="h-screen w-full flex flex-col pt-20 px-4 md:px-8 pb-6">
        <header className="flex justify-between items-end mb-6 shrink-0">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Session: <span className="text-accentBlue">{mockSession.filename}</span></h1>
            <p className="text-sm text-gray-400">Processed Transaction: <span className="font-mono text-white bg-white/10 px-2 py-0.5 rounded">{mockSession.transactionType}</span></p>
          </div>
          <div className="flex gap-4">
             <button 
               onClick={() => setShowEDIViewer(!showEDIViewer)}
               className="btn btn-secondary text-sm border-white/20 hover:bg-white/10"
             >
               {showEDIViewer ? 'View Structure' : 'View Raw EDI'}
             </button>
             <button className="btn btn-primary text-sm flex items-center gap-2 shadow-[0_0_15px_rgba(255,255,255,0.2)]">
               Export Mappings
             </button>
          </div>
        </header>

        {/* Main Split Layout */}
        <div className="flex-1 min-h-0 flex flex-col md:flex-row gap-6 relative">
          
          {/* Left Column - Core Viewer */}
          <div className="w-full md:w-2/3 flex flex-col h-full gap-6">
            {!showEDIViewer ? (
              <SegmentTree 
                segments={liveSegments} 
                activeErrorSegmentId={activeSegmentId} 
                onElementClick={handleElementClick}
                fixedSegmentIds={fixedSegments}
              />
            ) : (
              <EDIViewer ediString={generatedEDIString} />
            )}
          </div>

          {/* Right Column - Validation & AI */}
          <div className="w-full md:w-1/3 flex flex-col h-full gap-6">
            <div className="flex-1 min-h-0">
              <ErrorPanel 
                errors={liveErrors} 
                onSelectError={handleSelectError} 
                activeErrorId={activeErrorId} 
              />
            </div>
            <div className="flex-1 min-h-[250px]">
              <AIChatPanel />
            </div>
          </div>

        </div>

        {/* Fix Popup Model */}
        {editingElement && (
          <FixEditor 
            segmentId={liveSegments.find(s => s.id === editingElement.segmentId)?.segmentId || 'UNK'}
            elementIndex={editingElement.elementIndex}
            currentValue={editingElement.value}
            onApply={handleApplyFix}
            onCancel={() => setEditingElement(null)}
          />
        )}
      </div>
    </>
  );
}
