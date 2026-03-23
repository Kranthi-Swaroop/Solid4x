import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './video.css';

export default function VideoArena() {
  const [url, setUrl] = useState('');
  const [lang, setLang] = useState('hi');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const handleProcess = async () => {
    if (!url) return;
    setLoading(true);
    setError('');
    setData(null);

    try {
      const res = await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/content/process-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, target_language: lang }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to process video');
      }

      const result = await res.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="video-arena-container">
      <header className="video-header">
        <h1>Multimodal Content Processor</h1>
        <p>Distraction-free learning with AI-generated notes & Indic dubbing.</p>
      </header>

      <div className="video-controls">
        <input
          type="text"
          placeholder="Paste YouTube URL here..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="url-input"
        />
        <select value={lang} onChange={(e) => setLang(e.target.value)} className="lang-select">
          <option value="hi">Hindi (हिन्दी)</option>
          <option value="te">Telugu (తెలుగు)</option>
          <option value="ta">Tamil (தமிழ்)</option>
          <option value="bn">Bengali (বাংলা)</option>
        </select>
        <button onClick={handleProcess} disabled={loading || !url} className="process-btn">
          {loading ? 'Processing AI Dub & Notes...' : 'Process Video'}
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {data && (
        <div className="workspace-grid">
          <div className="player-section">
            <div className="player-wrapper">
              <iframe
                src={`https://www.youtube.com/embed/${data.video_id}?rel=0&modestbranding=1&iv_load_policy=3`}
                title="YouTube Video"
                className="react-player"
                width="100%"
                height="100%"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>

            {data.audio_url && (
              <div className="audio-section">
                <h3>Indic Summary Audio ({lang.toUpperCase()})</h3>
                <audio controls src={data.audio_url} className="audio-player">
                  Your browser does not support the audio element.
                </audio>
                <div className="translation-box">
                  <p>{data.translated_summary}</p>
                </div>
              </div>
            )}
          </div>

          <div className="notes-section">
            <h2>AI Structured Notes</h2>
            <div className="markdown-content">
              <ReactMarkdown>{data.notes_markdown}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
