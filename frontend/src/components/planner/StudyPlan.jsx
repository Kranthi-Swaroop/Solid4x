import { useState, useEffect, useCallback, useMemo } from "react";
import SessionCard from "./SessionCard";
import "./planner.css";

/** Format "2026-03-24" → "Monday, Mar 24" */
function formatDate(isoDate) {
  const d = new Date(isoDate + "T00:00:00");
  return d.toLocaleDateString("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}

/** Group flat sessions array into { date: [session, ...] } map */
function groupByDate(sessions) {
  return sessions.reduce((acc, s) => {
    const key = s.date;
    if (!acc[key]) acc[key] = [];
    acc[key].push(s);
    return acc;
  }, {});
}

const SUBJECT_ICONS = {
  Mathematics: "📐",
  Physics: "⚡",
  Chemistry: "🧪",
};
const SUBJECT_COLORS = {
  Mathematics: "#e67e22",
  Physics: "#3498db",
  Chemistry: "#9b59b6",
};

export default function StudyPlan({ profileId, profile }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [focusTopics, setFocusTopics] = useState([]);
  const [showFocus, setShowFocus] = useState(false);

  // Filters
  const [filterSubject, setFilterSubject] = useState("All");
  const [filterChapter, setFilterChapter] = useState("All");
  const [filterType, setFilterType] = useState("All"); // All | Weak | Incomplete
  const [visibleCount, setVisibleCount] = useState(20);

  const userId = localStorage.getItem('profileId') || profileId;

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/planner/plan/${profileId}`);
      if (!res.ok) throw new Error("Failed to load sessions.");
      const data = await res.json();
      setSessions(data.sessions ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [profileId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  useEffect(() => {
    if (!userId) return;
    fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/syllabus/weak/${userId}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setFocusTopics(data.focus_topics || []);
      })
      .catch(() => { });
  }, [userId]);

  const handleMark = async (sessionId, status) => {
    try {
      await fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/planner/session/${sessionId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (status === "missed") {
        await fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/planner/rebalance/${profileId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(profile),
        });
      }
    } catch {
    } finally {
      fetchSessions();
    }
  };

  const markComplete = async (topic) => {
    setFocusTopics(prev => prev.filter(t =>
      !(t.subject === topic.subject && t.chapter === topic.chapter && t.topic === topic.topic)
    ));
    try {
      await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/syllabus/toggle', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          subject: topic.subject,
          chapter: topic.chapter,
          topic: topic.topic,
        }),
      });
    } catch (err) { console.error(err); }
  };

  const handleRebalance = async () => {
    setLoading(true);
    try {
      await fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/planner/rebalance/${profileId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
    } catch {
    } finally {
      fetchSessions();
    }
  };

  // Progress
  const total = sessions.length;
  const done = sessions.filter((s) => s.status === "done").length;
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  const grouped = groupByDate(sessions);
  const sortedDates = Object.keys(grouped).sort();

  // Focus stats
  const weakCount = focusTopics.filter(t => t.is_weak).length;
  const incompleteCount = focusTopics.filter(t => !t.is_weak && t.is_incomplete).length;

  // Unique subjects & chapters for filters
  const subjects = useMemo(() => [...new Set(focusTopics.map(t => t.subject))], [focusTopics]);
  const chapters = useMemo(() => {
    const filtered = filterSubject === "All" ? focusTopics : focusTopics.filter(t => t.subject === filterSubject);
    return [...new Set(filtered.map(t => t.chapter))];
  }, [focusTopics, filterSubject]);

  // Filtered topics
  const filteredTopics = useMemo(() => {
    let list = focusTopics;
    if (filterSubject !== "All") list = list.filter(t => t.subject === filterSubject);
    if (filterChapter !== "All") list = list.filter(t => t.chapter === filterChapter);
    if (filterType === "Weak") list = list.filter(t => t.is_incomplete);
    if (filterType === "Completed") list = list.filter(t => t.is_completed);
    return list;
  }, [focusTopics, filterSubject, filterChapter, filterType]);

  // Reset chapter filter when subject changes
  useEffect(() => { setFilterChapter("All"); setVisibleCount(20); }, [filterSubject]);
  useEffect(() => { setVisibleCount(20); }, [filterChapter, filterType]);

  return (
    <div className="planner-module">
      {/* Top bar */}
      <div className="sp-topbar">
        <h2 className="sp-heading">Your 7-Day JEE Plan</h2>
        <div className="sp-progress-wrap">
          <p className="sp-progress-label">
            {done} of {total} sessions complete
          </p>
          <div className="sp-progress-track" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
            <div className="sp-progress-fill" style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>

      {/* ── Focus Areas ── */}
      {focusTopics.length > 0 && (
        <div className="sp-focus-section">
          <div className="sp-focus-header" onClick={() => setShowFocus(!showFocus)}>
            <h3 className="sp-focus-title">
              📌 Focus Areas
              <span className="sp-focus-badge weak">{weakCount} weak</span>
              <span className="sp-focus-badge incomplete">{incompleteCount} to cover</span>
            </h3>
            <span className="sp-focus-toggle">{showFocus ? '▲ Hide' : '▼ Show'}</span>
          </div>

          {showFocus && (
            <div className="sp-focus-body">
              {/* ── Filter Bar ── */}
              <div className="sp-filter-bar">
                {/* Subject pills */}
                <div className="sp-filter-row">
                  <span className="sp-filter-label">Subject</span>
                  <div className="sp-filter-pills">
                    <button
                      className={`sp-pill-btn ${filterSubject === 'All' ? 'active' : ''}`}
                      onClick={() => setFilterSubject('All')}
                    >All</button>
                    {subjects.map(s => (
                      <button
                        key={s}
                        className={`sp-pill-btn ${filterSubject === s ? 'active' : ''}`}
                        style={filterSubject === s ? { background: SUBJECT_COLORS[s] || '#3b82f6', borderColor: SUBJECT_COLORS[s] || '#3b82f6', color: '#fff' } : {}}
                        onClick={() => setFilterSubject(s)}
                      >{SUBJECT_ICONS[s] || '📚'} {s}</button>
                    ))}
                  </div>
                </div>

                {/* Chapter dropdown */}
                <div className="sp-filter-row">
                  <span className="sp-filter-label">Chapter</span>
                  <select
                    className="sp-filter-select"
                    value={filterChapter}
                    onChange={e => setFilterChapter(e.target.value)}
                  >
                    <option value="All">All Chapters ({chapters.length})</option>
                    {chapters.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                {/* Type filter */}
                <div className="sp-filter-row">
                  <span className="sp-filter-label">Status</span>
                  <div className="sp-filter-pills">
                    {['All', 'Weak', 'Completed'].map(t => (
                      <button
                        key={t}
                        className={`sp-pill-btn sm ${filterType === t ? 'active' : ''}`}
                        onClick={() => setFilterType(t)}
                      >{t === 'Weak' ? '⚠️ ' : t === 'Completed' ? '✓ ' : ''}{t}</button>
                    ))}
                  </div>
                </div>
              </div>

              {/* ── Results count ── */}
              <div className="sp-focus-results-bar">
                <span>{filteredTopics.length} topic{filteredTopics.length !== 1 ? 's' : ''} found</span>
              </div>

              {/* ── Topic Cards ── */}
              <div className="sp-focus-cards">
                {filteredTopics.slice(0, visibleCount).map((t, i) => (
                  <div
                    key={i}
                    className="sp-focus-card"
                    style={{ borderLeftColor: t.is_completed ? '#22c55e' : '#f59e0b' }}
                  >
                    <div className="sp-fc-top">
                      <span
                        className="sp-fc-subject-badge"
                        style={{ background: SUBJECT_COLORS[t.subject] || '#64748b' }}
                      >{SUBJECT_ICONS[t.subject] || '📚'} {t.subject}</span>
                      <span className={`sp-fc-status ${t.is_completed ? 'completed' : 'weak'}`}>
                        {t.is_completed ? '✓ Completed · Weak' : '⚠️ Weak'}
                      </span>
                    </div>
                    <div className="sp-fc-topic">{t.topic}</div>
                    <div className="sp-fc-bottom">
                      <div className="sp-fc-chapter">{t.chapter}</div>
                      {!t.is_completed && (
                        <button
                          className="sp-fc-complete-btn"
                          onClick={() => markComplete(t)}
                          title="Mark as completed"
                        >✓ Done</button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Show more */}
              {filteredTopics.length > visibleCount && (
                <button
                  className="sp-focus-show-more"
                  onClick={() => setVisibleCount(prev => prev + 20)}
                >
                  Show more ({filteredTopics.length - visibleCount} remaining)
                </button>
              )}

              {filteredTopics.length === 0 && (
                <p className="sp-focus-empty">No topics match current filters.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && <p className="sp-error">{error}</p>}

      {/* Loading */}
      {loading && (
        <div className="sp-loading">
          <span className="btn-spinner btn-spinner--dark" />
          Loading your plan…
        </div>
      )}

      {/* Grouped session days */}
      {!loading && !error && (
        <div className="sp-days">
          {sortedDates.length === 0 && (
            <p className="sp-empty">No sessions found. Try rebalancing.</p>
          )}
          {sortedDates.map((date) => (
            <div key={date} className="sp-day-section">
              <h3 className="sp-date-heading">{formatDate(date)}</h3>
              <div className="sp-cards-row">
                {grouped[date].map((session) => (
                  <SessionCard
                    key={session._id}
                    session={session}
                    onMark={handleMark}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Floating rebalance button */}
      <button
        id="sp-rebalance-btn"
        className="sp-fab"
        onClick={handleRebalance}
        disabled={loading}
        title="Rebalance Plan"
      >
        ↻ Rebalance Plan
      </button>
    </div>
  );
}

