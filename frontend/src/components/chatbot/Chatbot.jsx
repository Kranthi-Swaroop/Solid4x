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

  const [isListening, setIsListening] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const recognitionRef = useRef(null);
  const currentAudioRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const toggleMute = () => {
    setIsMuted(prev => {
      const nextMuted = !prev;
      if (nextMuted && currentAudioRef.current) {
        currentAudioRef.current.pause(); // Instantly kill playing audio
      }
      return nextMuted;
    });
  };

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'hi-IN'; // Native Hindi support

      recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setInput(finalTranscript);
          sendMessage(finalTranscript); // Auto-send when finished speaking
        }
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, [isListening]); // rebind if needed, but acts as init

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      setInput(''); // clear previous text before speaking
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const playVoiceResponse = (text) => {
    if (isMuted) return;
    
    if (currentAudioRef.current) {
      currentAudioRef.current.pause(); // stop previous audio if any
    }

    try {
      // Stream instantly by setting the native Audio source directly to our GET endpoint
      const encodedText = encodeURIComponent(text);
      const audioUrl = `/api/tts?text=${encodedText}`;
      const audio = new Audio(audioUrl);
      
      currentAudioRef.current = audio;
      audio.play().catch(err => console.error('Failed to play TTS audio', err));
    } catch (err) {
      console.error('Failed to setup native audio', err);
    }
  };

  const sendMessage = async (text) => {
    const query = text || input.trim();
    if (!query || loading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setLoading(true);
    
    // Stop listening if user hits send manually
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    }

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

      // Play the audio automatically
      playVoiceResponse(data.answer);

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
            <button 
              className="chatbot-mute-btn" 
              onClick={toggleMute}
              title={isMuted ? "Unmute Voice" : "Mute Voice"}
              style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '1.2rem', marginLeft: 'auto' }}
            >
              {isMuted ? '🔇' : '🔊'}
            </button>
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
            <button 
              className={`chatbot-mic-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleListening}
              title="Speak your doubt (Hindi/English)"
              style={{
                background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer',
                color: isListening ? '#ff4d4f' : '#64748b',
                padding: '0 8px',
                animation: isListening ? 'pulse 1.5s infinite' : 'none'
              }}
            >
              🎙️
            </button>
            <input
              type="text"
              placeholder="Ask a JEE doubt..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              style={{ flex: 1 }}
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
