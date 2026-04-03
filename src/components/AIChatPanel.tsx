import React, { useState } from 'react';

export default function AIChatPanel() {
  const [messages, setMessages] = useState<{role: 'ai' | 'user', text: string}[]>([
    { role: 'ai', text: 'Hello! I am your EDI Intelligence Assistant. How can I help clarify your validation errors today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: `Based on standard HIPAA layout logic, fixing the missing segment you referenced requires appending the primary identification code sequence directly to standard X12 formatting limits. I recommend applying the suggested Fix.` 
      }]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="w-full bg-[rgba(10,10,12,0.6)] backdrop-blur-xl border border-accentBlue/20 rounded-2xl flex flex-col h-full max-h-[500px]">
      <div className="p-4 border-b border-[rgba(255,255,255,0.1)] flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-accentBlue/20 flex items-center justify-center">
          <svg className="w-4 h-4 text-accentCyan" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h3 className="font-bold text-white text-sm">EDI Intelligence Agent</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
              msg.role === 'user' 
                ? 'bg-accentBlue text-white rounded-br-none' 
                : 'bg-white/10 text-gray-200 rounded-bl-none border border-white/5'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
             <div className="bg-white/5 border border-white/5 rounded-2xl rounded-bl-none px-4 py-3 flex gap-1">
               <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
               <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></span>
               <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></span>
             </div>
          </div>
        )}
      </div>

      <div className="p-3 border-t border-[rgba(255,255,255,0.05)] bg-black/20 rounded-b-2xl">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about this error..."
            className="w-full bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.1)] text-white text-sm rounded-full pl-4 pr-10 py-2 focus:outline-none focus:border-accentCyan/50 transition-colors"
          />
          <button 
             type="submit"
             disabled={!input.trim() || isTyping}
             className="absolute right-2 p-1.5 rounded-full text-accentCyan hover:bg-accentCyan/10 transition disabled:opacity-50"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
