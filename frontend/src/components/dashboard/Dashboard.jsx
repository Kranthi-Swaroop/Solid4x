import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './dashboard.css';
import Chatbot from '../chatbot/Chatbot';

export default function Dashboard() {
  const navigate = useNavigate();
  const userId = localStorage.getItem('profileId') || '';
  const fallbackName = localStorage.getItem('studentName') || 'Student';

  const [stats, setStats] = useState(null);
  const [syllabusProg, setSyllabusProg] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) { setLoading(false); return; }
    Promise.all([
      fetch(`/dashboard/stats/${userId}`).then(r => r.ok ? r.json() : null),
      fetch(`/syllabus/progress/${userId}`).then(r => r.ok ? r.json() : null),
    ])
      .then(([dashData, sylData]) => {
        if (dashData) setStats(dashData);
        if (sylData) setSyllabusProg(sylData);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId]);

  // Derived values
  const studentName = stats?.student_name || fallbackName;
  const targetExam = stats?.target_exam || localStorage.getItem('targetExam') || 'JEE Advanced';
  const examDate = stats?.exam_date || '2026-05-24';
  const streak = stats?.streak || 0;

  const studyCompleted = stats?.study_goal?.completed || 0;
  const studyTarget = stats?.study_goal?.target || 8;
  const studyPct = studyTarget ? Math.round((studyCompleted / studyTarget) * 100) : 0;

  const flashcardsDue = stats?.flashcards_due || 0;
  const dueBreakdown = stats?.due_breakdown || {};
  const mockAvg = stats?.mock_test_avg || 0;
  const syllabusCoverage = syllabusProg?.coverage || stats?.syllabus_coverage || 0;
  const coveragePct = Math.round(syllabusCoverage * 100);
  const completedTopics = syllabusProg?.completed_count || 0;
  const totalSyllabusTopics = syllabusProg?.total_topics || 0;

  const todayPlan = stats?.today_plan || [];

  // Days until exam
  const daysLeft = Math.max(0, Math.ceil((new Date(examDate) - new Date()) / (1000 * 60 * 60 * 24)));

  // Mark a task as done
  const handleTaskToggle = async (index, currentDone) => {
    try {
      await fetch(`/planner/today/${userId}/task`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_index: index, done: !currentDone }),
      });
      // Refresh stats
      const res = await fetch(`/dashboard/stats/${userId}`);
      if (res.ok) setStats(await res.json());
    } catch (err) { console.error(err); }
  };

  const initials = studentName.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);

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
          <Link to="/syllabus">
            <span className="dash-nav-icon">📊</span> Syllabus Tracker
          </Link>
        </nav>

        <div className="dash-countdown">
          <div className="dash-countdown-label">Target Countdown</div>
          <div className="dash-countdown-days">{daysLeft}</div>
          <div className="dash-countdown-unit">Days to {targetExam}</div>
        </div>

        <button className="dash-logout-btn" onClick={() => {
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('studentName');
          localStorage.removeItem('token');
          window.location.href = '/login';
        }}>
          <span>🚪</span> Log Out
        </button>
      </aside>

      {/* ===== MAIN ===== */}
      <div className="dash-main">
        {/* ===== HEADER ===== */}
        <header className="dash-header">
          <div className="dash-welcome">
            <h2>Welcome back, {studentName}!</h2>
            <p>Your target: {targetExam}.</p>
          </div>
          <div className="dash-header-right">
            <div className="dash-search">
              <span style={{ color: '#94a3b8' }}>🔍</span>
              <input type="text" placeholder="Search..." />
            </div>
            {streak > 0 && (
              <div className="dash-streak">
                🔥 Daily Streak: {streak} Days
              </div>
            )}
            <div className="dash-notif">
              🔔
              {flashcardsDue > 0 && <div className="dash-notif-dot" />}
            </div>
            <div className="dash-avatar">{initials}</div>
          </div>
        </header>

        {/* ===== CONTENT ===== */}
        <div className="dash-content">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⏳</div>
              Loading your dashboard...
            </div>
          ) : (
            <>
              {/* ----- Quick Stats ----- */}
              <div>
                <h3 className="dash-section-title">Quick Stats Overview</h3>
                <div className="dash-stats-row">
                  {/* Today's Study Goal */}
                  <div className="dash-stat-card study-goal">
                    <div className="dash-stat-label">Today's Study Goal</div>
                    <div className="dash-stat-value" style={{ fontSize: '1.3rem' }}>
                      {studyCompleted} hrs <span style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 500 }}>/ {studyTarget} hrs</span>
                    </div>
                    <div className="dash-progress-bar">
                      <div className="dash-progress-fill" style={{ width: `${studyPct}%`, background: 'linear-gradient(90deg, #3b82f6, #60a5fa)' }} />
                    </div>
                  </div>

                  {/* Flashcards Due */}
                  <div className="dash-stat-card flashcards" onClick={() => navigate('/retention')} style={{ cursor: 'pointer' }}>
                    <div className="dash-stat-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                      Flashcards Due
                      {flashcardsDue > 0 && <span style={{ color: '#f59e0b', fontSize: '1.1rem' }}>⚠</span>}
                    </div>
                    <div style={{ color: '#f59e0b', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>Spaced Repetition</div>
                    <div className="dash-stat-value">{flashcardsDue} <span style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 500 }}>cards for review</span></div>
                  </div>

                  {/* Average Mock Score */}
                  <div className="dash-stat-card mock-score">
                    <div className="dash-stat-label">Average Mock Test Score</div>
                    <div className="dash-stat-value">{mockAvg}<span style={{ fontSize: '0.9rem', color: '#94a3b8', fontWeight: 500 }}>/300</span></div>
                  </div>

                  {/* Syllabus Coverage */}
                  <div className="dash-stat-card syllabus" onClick={() => navigate('/syllabus')} style={{ cursor: 'pointer' }}>
                    <div className="dash-stat-label">Syllabus Coverage</div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div>
                        <div className="dash-stat-value">{coveragePct}%</div>
                        <div className="dash-stat-sub">{completedTopics}/{totalSyllabusTopics} topics</div>
                      </div>
                      <div className="dash-radial">
                        <svg width="52" height="52" viewBox="0 0 52 52">
                          <circle cx="26" cy="26" r="22" fill="none" stroke="#e2e8f0" strokeWidth="5" />
                          <circle cx="26" cy="26" r="22" fill="none" stroke="#8b5cf6" strokeWidth="5" strokeDasharray={`${(coveragePct / 100) * 138.2} ${138.2}`} strokeLinecap="round" />
                        </svg>
                        <div className="dash-radial-text">{coveragePct}%</div>
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
                  {todayPlan.length === 0 ? (
                    <p style={{ color: '#94a3b8', textAlign: 'center', padding: '20px' }}>
                      Complete onboarding to get your personalized study plan.
                      <br />
                      <button onClick={() => navigate('/planner')} style={{ marginTop: '10px', padding: '8px 18px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                        Set Up Plan →
                      </button>
                    </p>
                  ) : (
                    <div className="dash-timeline">
                      {todayPlan.map((task, i) => (
                        <div className="dash-timeline-item" key={i}>
                          <div
                            className={`dash-tl-check ${task.done ? 'done' : ''}`}
                            onClick={() => handleTaskToggle(i, task.done)}
                            style={{ cursor: 'pointer' }}
                          >
                            {task.done ? '✓' : ''}
                          </div>
                          <div className="dash-tl-time">{task.time} {parseInt(task.time) < 12 ? '' : ''}</div>
                          <div className="dash-tl-text">
                            <strong>{task.subject}</strong> — {task.topic} ({task.type})
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Spaced Rep Quick Actions */}
                <div className="dash-card dash-sr-card">
                  <h3 className="dash-section-title">Spaced Repetition</h3>
                  {flashcardsDue > 0 ? (
                    <>
                      <p className="dash-sr-desc">You have <strong>{flashcardsDue}</strong> cards due for review today.</p>
                      <div className="dash-sr-breakdown">
                        {Object.entries(dueBreakdown).map(([subject, count]) => (
                          <div className="dash-sr-item" key={subject}>
                            <div className="dash-sr-dot" style={{ background: subject === 'Physics' ? '#3b82f6' : subject === 'Chemistry' ? '#f59e0b' : '#8b5cf6' }} />
                            <span><strong>{count}</strong> {subject} cards pending</span>
                          </div>
                        ))}
                      </div>
                      <button className="dash-sr-btn" onClick={() => navigate('/retention')}>
                        Start Daily Review
                      </button>
                    </>
                  ) : (
                    <>
                      <p className="dash-sr-desc">No cards due right now. Add topics to start tracking your retention.</p>
                      <button className="dash-sr-btn" onClick={() => navigate('/retention')}>
                        Manage Topics
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* ----- Row 3: Mock + Recommendations ----- */}
              <div className="dash-split-row r50-50">
                <div className="dash-card">
                  <h3 className="dash-section-title">Mock Test Performance</h3>
                  {mockAvg > 0 ? (
                    <>
                      <div className="dash-mock-stats">
                        <div className="dash-mock-stat">
                          <div className="dash-mock-stat-val">{mockAvg}<span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>/300</span></div>
                          <div className="dash-mock-stat-lbl">Average Score</div>
                        </div>
                      </div>
                      <button className="dash-detail-btn" onClick={() => navigate('/mocktest')}>
                        View Test History →
                      </button>
                    </>
                  ) : (
                    <p style={{ color: '#94a3b8' }}>Take your first mock test to see your performance here.
                      <br />
                      <button className="dash-detail-btn" onClick={() => navigate('/mocktest')} style={{ marginTop: '10px' }}>
                        Start Mock Test →
                      </button>
                    </p>
                  )}
                </div>

                <div className="dash-card">
                  <h3 className="dash-section-title">Quick Actions</h3>
                  <div className="dash-upcoming-item">
                    <div className="dash-upcoming-info">
                      <h4>Take Mock Test</h4>
                      <p>Full Syllabus Practice (3 hrs)</p>
                    </div>
                    <button className="dash-attempt-btn" onClick={() => navigate('/mocktest')}>Start</button>
                  </div>
                  <div className="dash-upcoming-item">
                    <div className="dash-upcoming-info">
                      <h4>Review Flashcards</h4>
                      <p>{flashcardsDue} cards due today</p>
                    </div>
                    <button className="dash-attempt-btn" onClick={() => navigate('/retention')}>Review</button>
                  </div>
                  <div className="dash-ai-rec">
                    <span className="dash-ai-badge">AI</span>
                    <span className="dash-ai-text">Use the AI Tutor chatbot (bottom-right) to ask any JEE doubt!</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      <Chatbot />
    </div>
  );
}
