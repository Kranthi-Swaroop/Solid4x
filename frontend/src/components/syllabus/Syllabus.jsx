import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import './syllabus.css';

export default function Syllabus() {
  const navigate = useNavigate();
  const userId = localStorage.getItem('profileId') || '';

  const [syllabus, setSyllabus] = useState({});
  const [completed, setCompleted] = useState([]);
  const [totalTopics, setTotalTopics] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expandedChapters, setExpandedChapters] = useState({});
  const [activeSubject, setActiveSubject] = useState('Physics');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    Promise.all([
      fetch('/syllabus/full').then(r => r.json()),
      fetch(`/syllabus/progress/${userId}`).then(r => r.json()),
    ])
      .then(([syllabusData, progressData]) => {
        setSyllabus(syllabusData);
        setCompleted(progressData.completed || []);
        setTotalTopics(progressData.total_topics || 0);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [userId]);

  const isCompleted = (subject, chapter, topic) =>
    completed.includes(`${subject}|${chapter}|${topic}`);

  const toggleTopic = async (subject, chapter, topic) => {
    const key = `${subject}|${chapter}|${topic}`;
    // Optimistic update
    setCompleted(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );

    try {
      const res = await fetch('/syllabus/toggle', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, subject, chapter, topic }),
      });
      if (res.ok) {
        const data = await res.json();
        setCompleted(data.completed);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const toggleChapter = (chapterKey) => {
    setExpandedChapters(prev => ({ ...prev, [chapterKey]: !prev[chapterKey] }));
  };

  // Stats
  const completedCount = completed.length;
  const coveragePct = totalTopics > 0 ? Math.round((completedCount / totalTopics) * 100) : 0;

  const subjectStats = useMemo(() => {
    const stats = {};
    const subjects = Object.keys(syllabus);
    for (const subject of subjects) {
      const chapters = syllabus[subject] || [];
      let total = 0;
      let done = 0;
      for (const ch of chapters) {
        total += ch.topics.length;
        for (const t of ch.topics) {
          if (isCompleted(subject, ch.chapter, t)) done++;
        }
      }
      stats[subject] = { total, done, pct: total > 0 ? Math.round((done / total) * 100) : 0 };
    }
    return stats;
  }, [syllabus, completed]);

  // Filtered chapters based on search
  const filteredChapters = useMemo(() => {
    const chapters = syllabus[activeSubject] || [];
    if (!searchQuery.trim()) return chapters;
    const q = searchQuery.toLowerCase();
    return chapters
      .map(ch => ({
        ...ch,
        topics: ch.topics.filter(t =>
          t.toLowerCase().includes(q) || ch.chapter.toLowerCase().includes(q)
        ),
      }))
      .filter(ch => ch.topics.length > 0);
  }, [syllabus, activeSubject, searchQuery]);

  if (loading) {
    return (
      <div className="syl-loading">
        <div className="syl-loading-icon">📚</div>
        Loading syllabus...
      </div>
    );
  }

  return (
    <div className="syl-root">
      {/* ── Header ── */}
      <div className="syl-header">
        <div>
          <button className="syl-back-btn" onClick={() => navigate('/')}>← Dashboard</button>
          <h1 className="syl-title">JEE Syllabus Tracker</h1>
          <p className="syl-subtitle">Track your progress across every topic</p>
        </div>
        <div className="syl-overall-progress">
          <div className="syl-overall-ring">
            <svg width="80" height="80" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="34" fill="none" stroke="#e2e8f0" strokeWidth="8" />
              <circle cx="40" cy="40" r="34" fill="none" stroke="#8b5cf6" strokeWidth="8"
                strokeDasharray={`${(coveragePct / 100) * 213.6} ${213.6}`}
                strokeLinecap="round" transform="rotate(-90 40 40)" />
            </svg>
            <div className="syl-ring-text">{coveragePct}%</div>
          </div>
          <div className="syl-overall-info">
            <div className="syl-overall-label">Overall Progress</div>
            <div className="syl-overall-counts">{completedCount} / {totalTopics} topics</div>
          </div>
        </div>
      </div>

      {/* ── Subject Tabs ── */}
      <div className="syl-subject-tabs">
        {Object.keys(syllabus).map(subject => {
          const st = subjectStats[subject] || { done: 0, total: 0, pct: 0 };
          return (
            <button
              key={subject}
              className={`syl-tab ${activeSubject === subject ? 'active' : ''}`}
              onClick={() => setActiveSubject(subject)}
            >
              <div className="syl-tab-name">{subject}</div>
              <div className="syl-tab-progress">
                <div className="syl-tab-bar">
                  <div className="syl-tab-bar-fill" style={{ width: `${st.pct}%` }} />
                </div>
                <span className="syl-tab-pct">{st.done}/{st.total}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* ── Search ── */}
      <div className="syl-search-bar">
        <span>🔍</span>
        <input
          type="text"
          placeholder={`Search topics in ${activeSubject}...`}
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
      </div>

      {/* ── Chapters ── */}
      <div className="syl-chapters">
        {filteredChapters.map((ch, ci) => {
          const chKey = `${activeSubject}|${ch.chapter}`;
          const isOpen = expandedChapters[chKey] !== false; // default open
          const chapterDone = ch.topics.filter(t => isCompleted(activeSubject, ch.chapter, t)).length;
          const chapterTotal = ch.topics.length;
          const chapterPct = chapterTotal > 0 ? Math.round((chapterDone / chapterTotal) * 100) : 0;

          return (
            <div className="syl-chapter" key={chKey}>
              <div className="syl-chapter-header" onClick={() => toggleChapter(chKey)}>
                <div className="syl-chapter-left">
                  <span className={`syl-chevron ${isOpen ? 'open' : ''}`}>▶</span>
                  <div>
                    <div className="syl-chapter-name">
                      {ci + 1}. {ch.chapter}
                    </div>
                    <div className="syl-chapter-meta">{chapterDone}/{chapterTotal} topics completed</div>
                  </div>
                </div>
                <div className="syl-chapter-right">
                  <div className="syl-chapter-bar">
                    <div
                      className="syl-chapter-bar-fill"
                      style={{
                        width: `${chapterPct}%`,
                        background: chapterPct === 100 ? '#22c55e' : '#3b82f6',
                      }}
                    />
                  </div>
                  <span className="syl-chapter-pct">{chapterPct}%</span>
                </div>
              </div>

              {isOpen && (
                <div className="syl-topics">
                  {ch.topics.map(topic => {
                    const done = isCompleted(activeSubject, ch.chapter, topic);
                    return (
                      <label key={topic} className={`syl-topic ${done ? 'done' : ''}`}>
                        <input
                          type="checkbox"
                          checked={done}
                          onChange={() => toggleTopic(activeSubject, ch.chapter, topic)}
                        />
                        <span className="syl-topic-check">{done ? '✓' : ''}</span>
                        <span className="syl-topic-text">{topic}</span>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
