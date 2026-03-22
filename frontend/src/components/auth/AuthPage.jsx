import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './auth.css';

export default function AuthPage({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    targetExam: 'JEE Advanced',
    targetYear: '2026'
  });
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (mode === 'signup') {
        const res = await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/users/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: formData.name,
            email: formData.email,
            password: formData.password
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || data.error || 'Signup failed');

        // Auto transition array to login
        setMode('login');
        setError('Architecture built successfully! Please log in securely.');
      } else {
        const params = new URLSearchParams();
        params.append('username', formData.email); // OAuth2 syntax mandates username mappings uniformly
        params.append('password', formData.password);

        const res = await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/users/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: params
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || data.error || 'Authenication denied structurally.');

        const token = data.access_token;
        localStorage.setItem('token', token);

        // Harvest User details natively via JWT decode pipeline
        const profileRes = await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/users/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const profileData = await profileRes.json();
        if (!profileRes.ok) throw new Error('Architecture boundary denied user payload fetch');

        localStorage.setItem('studentName', profileData.username);
        // Important: Use profileId natively throughout vectors/history
        localStorage.setItem('profileId', profileData.user_id);
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('targetExam', formData.targetExam || 'JEE Advanced');
        localStorage.setItem('targetYear', formData.targetYear || '2026');

        if (onLogin) onLogin(profileData.username);
        navigate('/');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-root">
      {/* ===== LEFT BRANDING PANEL ===== */}
      <div className="auth-left">
        <div className="auth-left-content">
          <div className="auth-brand-logo">
            <div className="auth-brand-icon">S4</div>
            <div className="auth-brand-text">Solid4x Prep</div>
          </div>
          <h1 className="auth-tagline">
            Ace Your <span>JEE / NEET</span> With Smart Preparation
          </h1>
          <p className="auth-subtitle">
            AI-powered study planner, spaced repetition, and full-length mock tests — everything you need to crack competitive exams.
          </p>
          <div className="auth-features">
            <div className="auth-feature">
              <div className="auth-feature-icon">📅</div>
              <span>Personalized AI study plans tailored to your schedule</span>
            </div>
            <div className="auth-feature">
              <div className="auth-feature-icon">🧠</div>
              <span>Spaced repetition flashcards for long-term retention</span>
            </div>
            <div className="auth-feature">
              <div className="auth-feature-icon">📝</div>
              <span>Full-length JEE mock tests with detailed analytics</span>
            </div>
            <div className="auth-feature">
              <div className="auth-feature-icon">📊</div>
              <span>Concept strength analysis & smart recommendations</span>
            </div>
          </div>
        </div>
      </div>

      {/* ===== RIGHT FORM PANEL ===== */}
      <div className="auth-right">
        <div className="auth-form-header">
          <h2>{mode === 'login' ? 'Welcome Back!' : 'Create Account'}</h2>
          <p>{mode === 'login' ? 'Log in to continue your preparation' : 'Start your journey to cracking competitive exams'}</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => setMode('login')}
          >
            Log In
          </button>
          <button
            className={`auth-tab ${mode === 'signup' ? 'active' : ''}`}
            onClick={() => setMode('signup')}
          >
            Create Account
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {error && (
            <div style={{ background: error.includes('successfully') ? '#d4edda' : '#f8d7da', color: error.includes('successfully') ? '#155724' : '#721c24', padding: '10px', borderRadius: '4px', marginBottom: '15px', fontSize: '0.9rem', border: `1px solid ${error.includes('successfully') ? '#c3e6cb' : '#f5c6cb'}` }}>
              {error}
            </div>
          )}
          {mode === 'signup' && (
            <div className="auth-field">
              <label>Full Name</label>
              <input
                type="text"
                name="name"
                placeholder="Aryan Sharma"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>
          )}

          <div className="auth-field">
            <label>Email Address</label>
            <input
              type="email"
              name="email"
              placeholder="aryan@example.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-field">
            <label>Password</label>
            <input
              type="password"
              name="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          {mode === 'signup' && (
            <div className="auth-row">
              <div className="auth-field">
                <label>Target Exam</label>
                <select name="targetExam" value={formData.targetExam} onChange={handleChange}>
                  <option>JEE Main</option>
                  <option>JEE Advanced</option>
                  <option>NEET</option>
                  <option>BITSAT</option>
                </select>
              </div>
              <div className="auth-field">
                <label>Target Year</label>
                <select name="targetYear" value={formData.targetYear} onChange={handleChange}>
                  <option>2026</option>
                  <option>2027</option>
                  <option>2028</option>
                </select>
              </div>
            </div>
          )}

          {mode === 'login' && (
            <div className="auth-remember">
              <label>
                <input type="checkbox" defaultChecked /> Remember me
              </label>
              <span className="auth-forgot">Forgot password?</span>
            </div>
          )}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? 'Processing Node...' : (mode === 'login' ? 'Log In' : 'Create Account')}
          </button>

          <div className="auth-divider">or continue with</div>

          <div className="auth-social">
            <button type="button" className="auth-social-btn">
              <span>🔵</span> Google
            </button>
            <button type="button" className="auth-social-btn">
              <span>⚫</span> GitHub
            </button>
          </div>

          <div className="auth-switch">
            {mode === 'login'
              ? <>Don't have an account? <span onClick={() => setMode('signup')}>Sign up</span></>
              : <>Already have an account? <span onClick={() => setMode('login')}>Log in</span></>
            }
          </div>
        </form>
      </div>
    </div>
  );
}
