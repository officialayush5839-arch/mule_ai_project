import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, Send, Sparkles, MessageSquare, ShieldAlert, Cpu, Download } from 'lucide-react';
import { api } from '../lib/api';
import AppLayout from '../components/AppLayout';

export default function Copilot() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('query');

  const chatEndRef = useRef(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I am your **FIU Audit Copilot**. I can help you deep dive into account telemetry, summarize active clusters, or prepare prosecution-ready Suspicious Transaction Reports (STRs). 
      
Choose a quick action below or type your forensic query.`
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Pre-fill query from search params on mount
  useEffect(() => {
    if (initialQuery) {
      handleSend(initialQuery);
      // Clean query params so it doesn't run repeatedly on hot reloads
      setSearchParams({});
    }
  }, [initialQuery]);

  const handleSend = async (messageText) => {
    const text = messageText || input;
    if (!text.trim()) return;

    // Add user message
    const userMsgId = `user-${Date.now()}`;
    setMessages(prev => [...prev, { id: userMsgId, role: 'user', content: text }]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await api.sendCopilotMessage(text);
      const aiMsgId = `ai-${Date.now()}`;
      setMessages(prev => [...prev, { id: aiMsgId, role: 'assistant', content: response }]);
    } catch (e) {
      setMessages(prev => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: 'Apologies. I encountered an error connecting to the intelligence node.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const presetQueries = [
    { label: 'Why is ACC-847291 flagged?', text: 'Why is ACC-847291 flagged' },
    { label: 'Generate prosecution report for ACC-847291', text: 'generate report' },
    { label: 'Summarize today\'s alerts', text: 'summarize alerts' }
  ];

  return (
    <AppLayout>
      <div className="page-header flex justify-between items-center w-full">
        <div>
          <h1 className="page-title">FIU Investigation Copilot</h1>
          <p className="page-subtitle">Natural language forensic interface linked to trained models and bank databases.</p>
        </div>
      </div>

      <div className="card copilot-container flex flex-col justify-between overflow-hidden w-full">
        {/* Chat Feed Window */}
        <div className="chat-feed-scroll" style={{ flex: 1, padding: '16px', overflowY: 'auto' }}>
          {messages.map((msg) => {
            const isAI = msg.role === 'assistant';
            return (
              <div 
                key={msg.id} 
                className={`chat-bubble-wrapper flex gap-12 ${isAI ? 'ai-bubble' : 'user-bubble flex-row-reverse'}`}
                style={{ marginBottom: '20px' }}
              >
                <div className={`chat-avatar flex items-center justify-center ${isAI ? 'bg-primary' : 'bg-secondary'}`}>
                  {isAI ? <Bot size={16} /> : 'AS'}
                </div>
                
                <div className="chat-content-card">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({node, ...props}) => <div className="table-responsive" style={{ margin: '12px 0' }}><table className="data-table" {...props} /></div>,
                      th: ({node, ...props}) => <th style={{ background: '#f1f5f9', padding: '8px' }} {...props} />,
                      td: ({node, ...props}) => <td style={{ padding: '8px' }} {...props} />
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
            );
          })}

          {isTyping && (
            <div className="chat-bubble-wrapper flex gap-12 ai-bubble" style={{ marginBottom: '20px' }}>
              <div className="chat-avatar bg-primary flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="chat-content-card typing-indicator-card">
                <div className="typing-dots flex gap-4">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Action Panel Footer */}
        <div className="copilot-footer border-top-divider flex flex-col gap-12" style={{ padding: '16px 20px', background: 'var(--surface-2)' }}>
          {/* Preset Chips */}
          <div className="preset-chips flex flex-wrap gap-8">
            {presetQueries.map((q, idx) => (
              <button 
                key={idx}
                className="chip-btn btn-ghost btn-sm"
                onClick={() => handleSend(q.text)}
              >
                <Sparkles size={12} className="text-primary" />
                <span>{q.label}</span>
              </button>
            ))}
          </div>

          {/* Form input field */}
          <form 
            className="chat-input-form flex gap-12"
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          >
            <input 
              type="text" 
              className="input" 
              placeholder="Ask copilot: 'Verify ACC-847291 balance volatility index', 'Generate report'..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button type="submit" className="btn btn-primary">
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>

      <style>{`
        .copilot-container {
          height: calc(100vh - var(--header-height) - 130px);
          display: flex;
          flex-direction: column;
          padding: 0 !important;
        }

        .chat-feed-scroll {
          background: #f8fafc;
        }

        .chat-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          color: #ffffff;
          font-size: 11px;
          font-weight: 700;
          flex-shrink: 0;
        }

        .chat-content-card {
          background: #ffffff;
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 12px 16px;
          max-width: 75%;
          font-size: 14px;
          color: var(--text-primary);
          line-height: 1.5;
        }

        .user-bubble .chat-content-card {
          background: var(--primary-light);
          border-color: rgba(37,99,235,0.15);
        }

        .typing-indicator-card {
          padding: 12px 20px;
        }

        .typing-dots span {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--text-muted);
          animation: bounce 1.2s infinite;
        }

        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }

        .chip-btn {
          border-radius: 9999px !important;
          font-size: 11px !important;
          padding: 4px 12px !important;
          border-color: var(--border) !important;
          background: #ffffff !important;
          color: var(--text-secondary) !important;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .chip-btn:hover {
          border-color: var(--primary) !important;
          color: var(--primary) !important;
          background: var(--primary-light) !important;
        }

        .chat-content-card h1, .chat-content-card h2, .chat-content-card h3 {
          font-size: 16px;
          font-weight: 700;
          margin-bottom: 8px;
          border-bottom: 1px solid var(--border);
          padding-bottom: 4px;
        }

        .chat-content-card ul {
          margin: 8px 0;
          padding-left: 20px;
        }

        .chat-content-card li {
          margin-bottom: 4px;
        }
      `}</style>
    </AppLayout>
  );
}
