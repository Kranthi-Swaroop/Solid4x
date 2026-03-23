import { useState, useEffect } from "react";
import SpacedRepetitionPractice from "./SpacedRepetitionPractice";
import "./retention.css";

function ConfirmModal({ topic, onConfirm, onCancel }) {
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ background: '#fff', borderRadius: '16px', padding: '35px', maxWidth: '450px', width: '90%', boxShadow: '0 20px 60px rgba(0,0,0,0.3)', textAlign: 'center' }}>
        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📝</div>
        <h2 style={{ margin: '0 0 10px 0', color: '#343a40' }}>Start Practice Session?</h2>
        <p style={{ color: '#6c757d', fontSize: '1.05rem', lineHeight: '1.6', margin: '0 0 25px 0' }}>
          You'll be given <strong>5 questions</strong> on <strong style={{ color: '#007bff' }}>{topic}</strong>.
          Your results will update your knowledge graph.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button onClick={onCancel} style={{ padding: '12px 30px', background: '#e9ecef', color: '#495057', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: '600', cursor: 'pointer' }}>Cancel</button>
          <button onClick={onConfirm} style={{ padding: '12px 30px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: '600', cursor: 'pointer' }}>Begin Practice →</button>
        </div>
      </div>
    </div>
  );
}

function getStatusLabel(strength, retention, tab) {
  if (strength === null || strength === undefined) return { text: 'Not Started', color: '#adb5bd', bg: '#f1f3f5' };

  if (tab === 'due') {
    if (retention < 0.2) return { text: 'Critical', color: '#dc3545', bg: '#f8d7da' };
    if (retention < 0.4) return { text: 'Fading Fast', color: '#e85d04', bg: '#fff3cd' };
    if (retention < 0.55) return { text: 'Needs Review', color: '#fd7e14', bg: '#fff8e1' };
    return { text: 'Review Soon', color: '#e6a817', bg: '#fffde7' };
  }
  if (tab === 'mastered') {
    if (strength >= 5.0) return { text: 'Expert', color: '#1b5e20', bg: '#c8e6c9' };
    if (strength >= 4.0) return { text: 'Strong', color: '#2e7d32', bg: '#d4edda' };
    return { text: 'Mastered', color: '#28a745', bg: '#e8f5e9' };
  }
  if (tab === 'weak') {
    if (strength === 0) return { text: 'No Progress', color: '#b71c1c', bg: '#ffebee' };
    if (strength < 0.5) return { text: 'Struggling', color: '#e83e8c', bg: '#fce4ec' };
    if (strength < 1.0) return { text: 'Needs Work', color: '#e65100', bg: '#fff3e0' };
    return { text: 'Almost There', color: '#f57c00', bg: '#fff8e1' };
  }
  return { text: 'Not Started', color: '#adb5bd', bg: '#f1f3f5' };
}

function getProgressWidth(strength, retention, tab) {
  if (tab === 'due') {
    return retention != null ? Math.max(3, retention * 100) : 0;
  }
  if (tab === 'mastered') {
    return strength ? Math.min(100, (strength / 6.0) * 100) : 0;
  }
  if (tab === 'weak') {
    return strength ? Math.max(3, Math.min(100, (strength / 1.5) * 100)) : 3;
  }
  return 0;
}

function getProgressColor(strength, retention, tab) {
  if (tab === 'due') {
    if (retention < 0.2) return '#dc3545';
    if (retention < 0.4) return '#e85d04';
    if (retention < 0.55) return '#fd7e14';
    return '#e6a817';
  }
  if (tab === 'mastered') {
    if (strength >= 5.0) return '#1b5e20';
    if (strength >= 4.0) return '#2e7d32';
    return '#43a047';
  }
  if (tab === 'weak') {
    if (strength === 0) return '#ef5350';
    if (strength < 0.5) return '#e83e8c';
    if (strength < 1.0) return '#ff9800';
    return '#f57c00';
  }
  return '#adb5bd';
}

function buildTree(topics) {
  const tree = {};
  for (const t of topics) {
    const subj = t.subject || 'Unknown';
    const chap = t.chapter || 'Unknown';
    if (!tree[subj]) tree[subj] = {};
    if (!tree[subj][chap]) tree[subj][chap] = [];
    tree[subj][chap].push(t);
  }
  return tree;
}

export default function RetentionDashboard({ profileId }) {
  const [activeTopic, setActiveTopic] = useState(null);
  const [pendingTopic, setPendingTopic] = useState(null); // for confirmation popup
  const [topicStatus, setTopicStatus] = useState({ due: [], mastered: [], weak: [], unpracticed: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('due');
  const [expandedSubjects, setExpandedSubjects] = useState({});
  const [expandedChapters, setExpandedChapters] = useState({});

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/repetition/topics/status', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setTopicStatus({
          due: data.due || [],
          mastered: data.mastered || [],
          weak: data.weak || [],
          unpracticed: data.unpracticed || []
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDashboardData(); }, [profileId, activeTopic]);

  if (activeTopic) {
    return <SpacedRepetitionPractice topic={activeTopic} onClose={() => setActiveTopic(null)} />;
  }

  const toggleSubject = (key) => setExpandedSubjects(prev => ({ ...prev, [key]: !prev[key] }));
  const toggleChapter = (key) => setExpandedChapters(prev => ({ ...prev, [key]: !prev[key] }));

  const tabs = [
    { key: 'due', label: '⚠️ Due for Review', count: topicStatus.due.length, color: '#fd7e14' },
    { key: 'weak', label: '🔴 Weak Areas', count: topicStatus.weak.length, color: '#dc3545' },
    { key: 'mastered', label: '✅ Mastered', count: topicStatus.mastered.length, color: '#28a745' },
    { key: 'unpracticed', label: '📌 Unexplored', count: topicStatus.unpracticed.length, color: '#6c757d' },
  ];

  const currentTopics = topicStatus[activeTab] || [];
  const tree = buildTree(currentTopics);
  const subjectOrder = ['physics', 'chemistry', 'mathematics'];
  const sortedSubjects = Object.keys(tree).sort((a, b) => {
    const ai = subjectOrder.indexOf(a.toLowerCase()), bi = subjectOrder.indexOf(b.toLowerCase());
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
  });

  const subjectIcons = { physics: '⚛️', chemistry: '🧪', mathematics: '📐' };

  const renderTopicRow = (t) => {
    const label = getStatusLabel(t.strength, t.retention, activeTab);
    const pw = getProgressWidth(t.strength, t.retention, activeTab);
    const pc = getProgressColor(t.strength, t.retention, activeTab);
    const displayName = (t.topic || '').replace(/-/g, ' ');

    return (
      <div
        key={t.topic}
        onClick={() => setPendingTopic(t.topic)}
        style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '12px 16px', background: '#fff', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.15s', border: '1px solid #e9ecef' }}
        onMouseOver={e => { e.currentTarget.style.background = '#f8f9fa'; e.currentTarget.style.borderColor = '#007bff40'; }}
        onMouseOut={e => { e.currentTarget.style.background = '#fff'; e.currentTarget.style.borderColor = '#e9ecef'; }}
      >
        <div style={{ flex: 1, fontWeight: 500, color: '#343a40', textTransform: 'capitalize', fontSize: '0.95rem' }}>{displayName}</div>
        <div style={{ width: '120px', height: '6px', background: '#e9ecef', borderRadius: '3px', overflow: 'hidden', flexShrink: 0 }}>
          <div style={{ width: `${pw}%`, height: '100%', background: pc, borderRadius: '3px', transition: 'width 0.3s' }} />
        </div>
        <span style={{ background: label.bg, color: label.color, padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 600, whiteSpace: 'nowrap', minWidth: '90px', textAlign: 'center' }}>
          {label.text}
        </span>
        <span style={{ color: '#adb5bd', fontSize: '0.85rem' }}>→</span>
      </div>
    );
  };

  if (loading) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: '#6c757d' }}><h2>Loading Knowledge Graph...</h2></div>;
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto', minHeight: '100vh' }}>
      {pendingTopic && (
        <ConfirmModal
          topic={pendingTopic}
          onConfirm={() => { setActiveTopic(pendingTopic); setPendingTopic(null); }}
          onCancel={() => setPendingTopic(null)}
        />
      )}

      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ margin: '0 0 5px 0', color: '#212529', fontSize: '1.8rem' }}>Spaced Repetition Dashboard</h1>
        <p style={{ margin: 0, color: '#6c757d' }}>Track your progress across all JEE topics. Click any topic to practice 5 questions.</p>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '30px' }}>
        {tabs.map(tab => (
          <div
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '18px 16px', borderRadius: '12px', cursor: 'pointer', textAlign: 'center',
              background: activeTab === tab.key ? tab.color : '#fff',
              color: activeTab === tab.key ? '#fff' : '#495057',
              border: activeTab === tab.key ? 'none' : '1px solid #dee2e6',
              transition: 'all 0.2s', fontWeight: 600
            }}
          >
            <div style={{ fontSize: '1.8rem', marginBottom: '4px' }}>{tab.count}</div>
            <div style={{ fontSize: '0.85rem' }}>{tab.label}</div>
          </div>
        ))}
      </div>

      {/* Nested Tree */}
      {sortedSubjects.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', background: '#fff', borderRadius: '12px', border: '1px solid #e9ecef' }}>
          <p style={{ color: '#adb5bd', fontSize: '1.1rem' }}>No topics found in this category.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {sortedSubjects.map(subj => {
            const subjKey = `${activeTab}-${subj}`;
            const isSubjOpen = expandedSubjects[subjKey] !== false; // default open
            const chapters = tree[subj];
            const icon = subjectIcons[subj.toLowerCase()] || '📖';
            const totalTopics = Object.values(chapters).reduce((s, arr) => s + arr.length, 0);

            return (
              <div key={subj} style={{ background: '#fff', borderRadius: '12px', border: '1px solid #e9ecef', overflow: 'hidden' }}>
                <div
                  onClick={() => toggleSubject(subjKey)}
                  style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 20px', cursor: 'pointer', background: '#f8f9fa', borderBottom: isSubjOpen ? '1px solid #e9ecef' : 'none' }}
                >
                  <span style={{ fontSize: '1.3rem' }}>{icon}</span>
                  <h2 style={{ margin: 0, flex: 1, fontSize: '1.15rem', color: '#212529', textTransform: 'capitalize' }}>{subj}</h2>
                  <span style={{ background: '#e9ecef', color: '#495057', padding: '3px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 600 }}>{totalTopics} topics</span>
                  <span style={{ color: '#adb5bd', transform: isSubjOpen ? 'rotate(90deg)' : 'rotate(0)', transition: 'transform 0.2s', fontSize: '1.2rem' }}>▶</span>
                </div>

                {isSubjOpen && (
                  <div style={{ padding: '10px 20px' }}>
                    {Object.keys(chapters).sort().map(chap => {
                      const chapKey = `${activeTab}-${subj}-${chap}`;
                      const isChapOpen = expandedChapters[chapKey] ?? false;
                      const topics = chapters[chap];
                      const displayChap = chap.replace(/-/g, ' ');

                      return (
                        <div key={chap} style={{ marginBottom: '6px' }}>
                          <div
                            onClick={() => toggleChapter(chapKey)}
                            style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px', cursor: 'pointer', borderRadius: '6px', background: isChapOpen ? '#f1f3f5' : 'transparent', transition: 'background 0.15s' }}
                            onMouseOver={e => { if (!isChapOpen) e.currentTarget.style.background = '#f8f9fa'; }}
                            onMouseOut={e => { if (!isChapOpen) e.currentTarget.style.background = 'transparent'; }}
                          >
                            <span style={{ color: '#adb5bd', transform: isChapOpen ? 'rotate(90deg)' : 'rotate(0)', transition: 'transform 0.2s', fontSize: '0.8rem' }}>▶</span>
                            <span style={{ flex: 1, fontWeight: 600, color: '#495057', textTransform: 'capitalize', fontSize: '0.95rem' }}>{displayChap}</span>
                            <span style={{ color: '#adb5bd', fontSize: '0.8rem' }}>{topics.length} topic{topics.length !== 1 ? 's' : ''}</span>
                          </div>

                          {isChapOpen && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', padding: '8px 0 8px 30px' }}>
                              {topics.map(t => renderTopicRow(t))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
