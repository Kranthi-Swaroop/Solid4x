import React, { useState, useRef, useEffect } from 'react';
import './chatbot.css';

const SUGGESTIONS = [
  "Explain Newton's laws of motion",
  "What is Le Chatelier's principle?",
  "Derive the quadratic formula",
  "Explain electromagnetic induction",
];

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    const query = text || input.trim();
    if (!query || loading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error (${res.status})`);
      }

      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'ai',
        text: data.answer,
        sources: data.sources,
        numChunks: data.num_chunks,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'ai',
        text: `Sorry, I couldn't process your question right now.\n\nError: ${err.message}`,
        sources: [],
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating toggle */}
      <button
        className={`chatbot-toggle ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="AI Tutor"
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <div className="chatbot-header-icon">🎓</div>
            <div className="chatbot-header-info">
              <h4>AI Tutor</h4>
              <p>Ask any JEE doubt — powered by RAG</p>
            </div>
          </div>

          <div className="chatbot-messages">
            {messages.length === 0 && !loading && (
              <div className="chatbot-welcome">
                <div className="chatbot-welcome-icon">🤖</div>
                <h4>Hi! I'm your AI Tutor</h4>
                <p>Ask me any JEE Physics, Chemistry, or Math doubt. I'll answer from your textbooks.</p>
                <div className="chatbot-suggestions">
                  {SUGGESTIONS.map((s, i) => (
                    <button 
                      key={i} 
                      className="chatbot-suggestion"
                      onClick={() => sendMessage(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`chatbot-msg ${msg.role}`}>
                {msg.text}
                {msg.role === 'ai' && msg.sources && msg.sources.length > 0 && (
                  <div className="chatbot-sources">
                    {msg.sources.map((s, j) => (
                      <span key={j} className="chatbot-source-chip">📚 {s}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="chatbot-loading">
                <div className="chatbot-dot" />
                <div className="chatbot-dot" />
                <div className="chatbot-dot" />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chatbot-input-bar">
            <input
              type="text"
              placeholder="Ask a JEE doubt..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button 
              className="chatbot-send-btn" 
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}
