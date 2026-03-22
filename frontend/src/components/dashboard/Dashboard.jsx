import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './dashboard.css';

export default function Dashboard() {
  const navigate = useNavigate();

  // Calculate days until JEE Advanced 2026 (approx May 2026)
  const targetDate = new Date('2026-05-24');
  const today = new Date();
  const daysLeft = Math.max(0, Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24)));

  // Demo student data
  const studentName = "Aryan Sharma";
  const streak = 15;

  return (
    <div className="dashboard-root">
      {/* ===== SIDEBAR ===== */}
      <aside className="dash-sidebar">
        <div className="dash-brand">
          <div className="dash-brand-icon">S4</div>
          <div className="dash-brand-name">Solid4x Prep</div>
        </div>

        <nav className="dash-nav">
          <Link to="/" className="active">
            <span className="dash-nav-icon">🏠</span> Dashboard
          </Link>
          <Link to="/planner">
            <span className="dash-nav-icon">📅</span> Study Planner
          </Link>
          <Link to="/retention">
            <span className="dash-nav-icon">🧠</span> Spaced Repetition
          </Link>
          <Link to="/mocktest">
            <span className="dash-nav-icon">📝</span> Mock Tests
          </Link>
          <Link to="/" style={{ opacity: 0.5, pointerEvents: 'none' }}>
            <span className="dash-nav-icon">📊</span> Performance Analytics
          </Link>
        </nav>

        <div className="dash-countdown">
          <div className="dash-countdown-label">Target Countdown</div>
          <div className="dash-countdown-days">{daysLeft}</div>
          <div className="dash-countdown-unit">Days to JEE Advanced 2026</div>
        </div>
      </aside>

      {/* ===== MAIN ===== */}
      <div className="dash-main">
        {/* ===== HEADER ===== */}
        <header className="dash-header">
          <div className="dash-welcome">
            <h2>Welcome back, {studentName}!</h2>
            <p>Your target: JEE Advanced 2026.</p>
          </div>
          <div className="dash-header-right">
            <div className="dash-search">
              <span style={{ color: '#94a3b8' }}>🔍</span>
              <input type="text" placeholder="Search..." />
            </div>
            <div className="dash-streak">
              🔥 Daily Streak: {streak} Days
            </div>
            <div className="dash-notif">
              🔔
              <div className="dash-notif-dot" />
            </div>
            <div className="dash-avatar">AS</div>
          </div>
        </header>

        {/* ===== CONTENT ===== */}
        <div className="dash-content">
          {/* ----- Quick Stats ----- */}
          <div>
            <h3 className="dash-section-title">Quick Stats Overview</h3>
            <div className="dash-stats-row">
              {/* Today's Study Goal */}
              <div className="dash-stat-card study-goal">
                <div className="dash-stat-label">Today's Study Goal</div>
                <div className="dash-stat-value" style={{ fontSize: '1.3rem' }}>6.5 hrs <span style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 500 }}>/ 8 hrs</span></div>
                <div className="dash-progress-bar">
                  <div className="dash-progress-fill" style={{ width: '81%', background: 'linear-gradient(90deg, #3b82f6, #60a5fa)' }} />
                </div>
              </div>

              {/* Flashcards Due */}
              <div className="dash-stat-card flashcards" onClick={() => navigate('/retention')} style={{ cursor: 'pointer' }}>
                <div className="dash-stat-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  Flashcards Due
                  <span style={{ color: '#f59e0b', fontSize: '1.1rem' }}>⚠</span>
                </div>
                <div style={{ color: '#f59e0b', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>Spaced Repetition</div>
                <div className="dash-stat-value">42 <span style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 500 }}>cards for review</span></div>
              </div>

              {/* Average Mock Score */}
              <div className="dash-stat-card mock-score">
                <div className="dash-stat-label">Average Mock Test Score</div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div className="dash-stat-value">185<span style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 500 }}>/300</span></div>
                  <div className="dash-mini-trend">
                    {[40, 55, 45, 65, 50, 75, 60, 80, 70, 85].map((h, i) => (
                      <div key={i} className="dash-mini-bar" style={{ height: `${h}%` }} />
                    ))}
                  </div>
                </div>
              </div>

              {/* Syllabus Coverage */}
              <div className="dash-stat-card syllabus">
                <div className="dash-stat-label">Syllabus Coverage</div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div className="dash-stat-value">65%</div>
                    <div className="dash-stat-sub">completed</div>
                  </div>
                  <div className="dash-radial">
                    <svg width="52" height="52" viewBox="0 0 52 52">
                      <circle cx="26" cy="26" r="22" fill="none" stroke="#e2e8f0" strokeWidth="5" />
                      <circle cx="26" cy="26" r="22" fill="none" stroke="#8b5cf6" strokeWidth="5" strokeDasharray={`${0.65 * 138.2} ${138.2}`} strokeLinecap="round" />
                    </svg>
                    <div className="dash-radial-text">65%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ----- Row 2: Plan + Spaced Rep ----- */}
          <div className="dash-split-row r60-40">
            {/* Today's Master Plan */}
            <div className="dash-card">
              <h3 className="dash-section-title">Today's Master Plan</h3>
              <div className="dash-timeline">
                <div className="dash-timeline-item">
                  <div className="dash-tl-check" />
                  <div className="dash-tl-time">08:00 AM</div>
                  <div className="dash-tl-text"><strong>Physics</strong> — Rotation (Theory)</div>
                </div>
                <div className="dash-timeline-item">
                  <div className="dash-tl-check done">✓</div>
                  <div className="dash-tl-time">11:00 AM</div>
                  <div className="dash-tl-text"><strong>Chemistry</strong> — Spaced Repetition Session</div>
                  <button className="dash-tl-action" onClick={() => navigate('/retention')}>Start Reviewing</button>
                </div>
                <div className="dash-timeline-item">
                  <div className="dash-tl-check" />
                  <div className="dash-tl-time">01:00 PM</div>
                  <div className="dash-tl-text"><strong>Mathematics</strong> — Calculus Practice</div>
                </div>
                <div className="dash-timeline-item">
                  <div className="dash-tl-check" />
                  <div className="dash-tl-time">03:00 PM</div>
                  <div className="dash-tl-text"><strong>Physics</strong> — Kinematics Problem Solving</div>
                </div>
                <div className="dash-timeline-item">
                  <div className="dash-tl-check" />
                  <div className="dash-tl-time">05:00 PM</div>
                  <div className="dash-tl-text"><strong>Mock Test</strong> — Full Syllabus Practice</div>
                  <button className="dash-tl-action" onClick={() => navigate('/mocktest')}>Start Test</button>
                </div>
              </div>
            </div>

            {/* Spaced Rep Quick Actions */}
            <div className="dash-card dash-sr-card">
              <h3 className="dash-section-title">Spaced Repetition Quick Actions</h3>
              <p className="dash-sr-desc">Complete your daily reviews to maintain your retention streak.</p>
              <div className="dash-sr-breakdown">
                <div className="dash-sr-item">
                  <div className="dash-sr-dot" style={{ background: '#3b82f6' }} />
                  <span><strong>12</strong> Physics flashcards pending</span>
                </div>
                <div className="dash-sr-item">
                  <div className="dash-sr-dot" style={{ background: '#f59e0b' }} />
                  <span><strong>20</strong> Organic Chemistry flashcards pending</span>
                </div>
                <div className="dash-sr-item">
                  <div className="dash-sr-dot" style={{ background: '#8b5cf6' }} />
                  <span><strong>10</strong> Math flashcards pending</span>
                </div>
              </div>
              <button className="dash-sr-btn" onClick={() => navigate('/retention')}>
                Start Daily Review
              </button>
            </div>
          </div>

          {/* ----- Row 3: Mock Performance + Upcoming ----- */}
          <div className="dash-split-row r50-50">
            {/* Recent Mock Performance */}
            <div className="dash-card">
              <h3 className="dash-section-title">Recent Mock Test Performance</h3>
              <div className="dash-mock-header">
                <p className="dash-mock-title">Full Syllabus Test 4</p>
              </div>
              <div className="dash-mock-stats">
                <div className="dash-mock-stat">
                  <div className="dash-mock-stat-val">210<span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>/300</span></div>
                  <div className="dash-mock-stat-lbl">Score</div>
                </div>
                <div className="dash-mock-stat">
                  <div className="dash-mock-stat-val">88%</div>
                  <div className="dash-mock-stat-lbl">Accuracy</div>
                </div>
                <div className="dash-mock-stat">
                  <div className="dash-mock-stat-val">95.2</div>
                  <div className="dash-mock-stat-lbl">Percentile</div>
                </div>
              </div>
              <div className="dash-concept-pills">
                <div className="dash-pill strong">Strong: Kinematics</div>
                <div className="dash-pill strong">Strong: Organic Chemistry</div>
                <div className="dash-pill weak">Weak: Thermodynamics</div>
              </div>
              <button className="dash-detail-btn" onClick={() => navigate('/mocktest')}>
                View Detailed Analysis →
              </button>
            </div>

            {/* Upcoming Tests */}
            <div className="dash-card">
              <h3 className="dash-section-title">Upcoming Tests & Recommendations</h3>
              <div className="dash-upcoming-item">
                <div className="dash-upcoming-info">
                  <h4>Full Syllabus Test 5</h4>
                  <p>Next scheduled Mock Test</p>
                </div>
                <button className="dash-attempt-btn" onClick={() => navigate('/mocktest')}>Attempt Now</button>
              </div>
              <div className="dash-upcoming-item">
                <div className="dash-upcoming-info">
                  <h4>Physics — Rotation & Gravitation</h4>
                  <p>Chapter-wise Mock Test</p>
                </div>
                <button className="dash-attempt-btn" onClick={() => navigate('/mocktest')}>Attempt Now</button>
              </div>
              <div className="dash-ai-rec">
                <span className="dash-ai-badge">AI</span>
                <span className="dash-ai-text">Based on your recent test, we recommend reviewing <strong>Rotational Mechanics</strong> and <strong>Thermodynamics</strong>.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
