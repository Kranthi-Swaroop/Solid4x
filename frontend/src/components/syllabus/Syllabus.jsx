import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStructuredSyllabus, getTotalTopicCount } from './syllabusData';
import './syllabus.css';

export default function Syllabus() {
  const navigate = useNavigate();
  const userId = localStorage.getItem('profileId') || '';

  const syllabusData = useMemo(() => getStructuredSyllabus(), []);
  const totalTopicCount = useMemo(() => getTotalTopicCount(), []);

  const [syllabus] = useState(syllabusData);
  const [completed, setCompleted] = useState([]);
  const [weakTopics, setWeakTopics] = useState([]);
  const [totalTopics] = useState(totalTopicCount);
  const [loading, setLoading] = useState(true);
  const [expandedChapters, setExpandedChapters] = useState({});
  const [activeSubject, setActiveSubject] = useState(() => {
    const subjects = Object.keys(syllabusData);
    return subjects.length > 0 ? subjects[0] : '';
  });
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Only fetch progress from backend; syllabus structure is local
    fetch(`/api/v1/syllabus/progress/${userId}`)
      .then(r => r.ok ? r.json() : { completed: [], weak_topics: [] })
      .then(progressData => {
        setCompleted(progressData.completed || []);
        setWeakTopics(progressData.weak_topics || []);
      })
      .catch(() => {
        // If backend is unavailable, load from localStorage as fallback
        const saved = localStorage.getItem('syllabus_completed');
        const savedWeak = localStorage.getItem('syllabus_weak');
        if (saved) setCompleted(JSON.parse(saved));
        if (savedWeak) setWeakTopics(JSON.parse(savedWeak));
      })
      .finally(() => setLoading(false));
  }, [userId]);

  const makeKey = (subject, chapter, topic) => `${subject}|${chapter}|${topic}`;

  const isCompleted = (subject, chapter, topic) =>
    completed.includes(makeKey(subject, chapter, topic));

  const isWeak = (subject, chapter, topic) =>
    weakTopics.includes(makeKey(subject, chapter, topic));

  const toggleTopic = async (subject, chapter, topic) => {
    const key = makeKey(subject, chapter, topic);
    setCompleted(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
    try {
      const res = await fetch('/api/v1/syllabus/toggle', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, subject, chapter, topic }),
      });
      if (res.ok) {
        const data = await res.json();
        setCompleted(data.completed);
      }
    } catch (err) { console.error(err); }
  };

  const bulkToggle = async (keys, action) => {
    // Optimistic update
    setCompleted(prev => {
      const s = new Set(prev);
      if (action === 'select') keys.forEach(k => s.add(k));
      else keys.forEach(k => s.delete(k));
      return [...s];
    });
    try {
      const res = await fetch('/api/v1/syllabus/bulk-toggle', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, keys, action }),
      });
      if (res.ok) {
        const data = await res.json();
        setCompleted(data.completed);
      }
    } catch (err) { console.error(err); }
  };

  const selectAllChapter = (subject, chapter, topics) => {
    const keys = topics.map(t => makeKey(subject, chapter, t.name));
    const allDone = keys.every(k => completed.includes(k));
    bulkToggle(keys, allDone ? 'deselect' : 'select');
  };

  const selectAllSubject = (subject) => {
    const groups = syllabus[subject] || [];
    const keys = [];
    for (const g of groups)
      for (const ch of g.chapters)
        for (const t of ch.topics)
          keys.push(makeKey(subject, ch.chapter, t.name));
    const allDone = keys.every(k => completed.includes(k));
    bulkToggle(keys, allDone ? 'deselect' : 'select');
  };

  const setStrength = async (subject, chapter, topic, strength) => {
    const key = makeKey(subject, chapter, topic);
    // Optimistic
    if (strength === 'weak') {
      setWeakTopics(prev => prev.includes(key) ? prev : [...prev, key]);
    } else {
      setWeakTopics(prev => prev.filter(k => k !== key));
    }
    try {
      const res = await fetch('/api/v1/syllabus/set-strength', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, subject, chapter, topic, strength }),
      });
      if (res.ok) {
        const data = await res.json();
        setWeakTopics(data.weak_topics);
      }
    } catch (err) { console.error(err); }
  };

  const toggleChapter = (chapterKey) => {
    setExpandedChapters(prev => ({ ...prev, [chapterKey]: !prev[chapterKey] }));
  };

  // Stats
  const completedCount = completed.length;
  const coveragePct = totalTopics > 0 ? Math.round((completedCount / totalTopics) * 100) : 0;

  const subjectStats = useMemo(() => {
    const stats = {};
    for (const [subject, groups] of Object.entries(syllabus)) {
      let total = 0, done = 0;
      for (const group of groups) {
        for (const ch of group.chapters) {
          total += ch.topics.length;
          for (const t of ch.topics) {
            if (isCompleted(subject, ch.chapter, t.name)) done++;
          }
        }
      }
      stats[subject] = { total, done, pct: total > 0 ? Math.round((done / total) * 100) : 0 };
    }
    return stats;
  }, [syllabus, completed]);

  // Filtered chapters based on search
  const filteredGroups = useMemo(() => {
    const groups = syllabus[activeSubject] || [];
    if (!searchQuery.trim()) return groups;
    const q = searchQuery.toLowerCase();
    return groups.map(g => ({
      ...g,
      chapters: g.chapters
        .map(ch => ({
          ...ch,
          topics: ch.topics.filter(t =>
            t.name.toLowerCase().includes(q) || ch.chapter.toLowerCase().includes(q)
          ),
        }))
        .filter(ch => ch.topics.length > 0),
    })).filter(g => g.chapters.length > 0);
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
          <p className="syl-subtitle">Track your progress &amp; mark weak areas</p>
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
      {/* Subject-level select/deselect all */}
      {activeSubject && (() => {
        const st = subjectStats[activeSubject] || { done: 0, total: 0 };
        const allDone = st.done === st.total && st.total > 0;
        return (
          <div className="syl-bulk-bar">
            <button className="syl-bulk-btn" onClick={() => selectAllSubject(activeSubject)}>
              {allDone ? '☐ Deselect All' : '☑ Select All'} in {activeSubject}
            </button>
          </div>
        );
      })()}

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

      {/* ── Legend ── */}
      <div className="syl-legend">
        <span className="syl-legend-item"><span className="syl-legend-dot strong" /> Strong</span>
        <span className="syl-legend-item"><span className="syl-legend-dot weak" /> Weak</span>
        <span className="syl-legend-item"><span className="syl-legend-dot completed" /> Completed</span>
      </div>

      {/* ── Groups & Chapters ── */}
      {filteredGroups.map(group => (
        <div key={group.group} className="syl-group">
          <h2 className="syl-group-title">{group.group}</h2>
          <div className="syl-chapters">
            {group.chapters.map((ch, ci) => {
              const chKey = `${activeSubject}|${ch.chapter}`;
              const isOpen = expandedChapters[chKey] !== false;
              const chDone = ch.topics.filter(t => isCompleted(activeSubject, ch.chapter, t.name)).length;
              const chTotal = ch.topics.length;
              const chPct = chTotal > 0 ? Math.round((chDone / chTotal) * 100) : 0;
              const chWeak = ch.topics.filter(t => isWeak(activeSubject, ch.chapter, t.name)).length;

              return (
                <div className="syl-chapter" key={chKey}>
                  <div className="syl-chapter-header" onClick={() => toggleChapter(chKey)}>
                    <div className="syl-chapter-left">
                      <span className={`syl-chevron ${isOpen ? 'open' : ''}`}>▶</span>
                      <div>
                        <div className="syl-chapter-name">{ch.chapter}</div>
                        <div className="syl-chapter-meta">
                          {chDone}/{chTotal} done
                          {chWeak > 0 && <span className="syl-chapter-weak-badge"> · {chWeak} weak</span>}
                        </div>
                      </div>
                    </div>
                    <div className="syl-chapter-right">
                      <div className="syl-chapter-bar">
                        <div className="syl-chapter-bar-fill" style={{
                          width: `${chPct}%`,
                          background: chPct === 100 ? '#22c55e' : '#3b82f6',
                        }} />
                      </div>
                      <span className="syl-chapter-pct">{chPct}%</span>
                    </div>
                  </div>

                  {isOpen && (
                    <div className="syl-topics">
                      <div className="syl-ch-bulk-bar">
                        <button
                          className="syl-ch-bulk-btn"
                          onClick={(e) => { e.stopPropagation(); selectAllChapter(activeSubject, ch.chapter, ch.topics); }}
                        >
                          {chDone === chTotal ? '☐ Deselect All' : '☑ Select All'}
                        </button>
                      </div>
                      {ch.topics.map(topic => {
                        const done = isCompleted(activeSubject, ch.chapter, topic.name);
                        const weak = isWeak(activeSubject, ch.chapter, topic.name);
                        const strong = !weak && done;

                        return (
                          <div key={topic.slug} className={`syl-topic ${done ? 'done' : ''} ${weak ? 'is-weak' : ''}`}>
                            <label className="syl-topic-checkbox">
                              <input
                                type="checkbox"
                                checked={done}
                                onChange={() => toggleTopic(activeSubject, ch.chapter, topic.name)}
                              />
                              <span className="syl-topic-check">{done ? '✓' : ''}</span>
                            </label>
                            <span className="syl-topic-text">{topic.name}</span>
                            <div className="syl-strength-btns">
                              <button
                                className={`syl-str-btn strong ${!weak ? 'active' : ''}`}
                                onClick={() => setStrength(activeSubject, ch.chapter, topic.name, 'strong')}
                                title="Mark as Strong"
                              >💪 Strong</button>
                              <button
                                className={`syl-str-btn weak ${weak ? 'active' : ''}`}
                                onClick={() => setStrength(activeSubject, ch.chapter, topic.name, 'weak')}
                                title="Mark as Weak"
                              >⚠️ Weak</button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
