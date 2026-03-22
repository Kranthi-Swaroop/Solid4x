import { useState, useEffect } from "react";
import "./retention.css";

export default function TopicPicker({ profileId, onAdded }) {
  const [allTopics, setAllTopics] = useState({});
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetch("/retention/topics-list")
      .then(res => res.ok ? res.json() : {})
      .then(data => setAllTopics(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const toggleTopic = (topic, subject) => {
    setSelected(prev => {
      const exists = prev.find(t => t.topic === topic && t.subject === subject);
      if (exists) return prev.filter(t => !(t.topic === topic && t.subject === subject));
      return [...prev, { topic, subject }];
    });
  };

  const isSelected = (topic, subject) =>
    selected.some(t => t.topic === topic && t.subject === subject);

  const handleSubmit = async () => {
    if (selected.length === 0) return;
    setSubmitting(true);
    try {
      await fetch("/retention/add-topics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: profileId, topics: selected }),
      });
      setSelected([]);
      onAdded();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div style={{ padding: '20px', color: '#64748b' }}>Loading topics...</div>;

  return (
    <div className="ret-topic-picker">
      <h4 className="ret-picker-title">Select Topics to Track</h4>
      <p className="ret-picker-desc">Choose topics you want to review with spaced repetition.</p>
      <div className="ret-picker-grid">
        {Object.entries(allTopics).map(([subject, topics]) => (
          <div key={subject} className="ret-picker-col">
            <h5 className="ret-picker-subject">{subject}</h5>
            <div className="ret-picker-chips">
              {topics.map(topic => (
                <button
                  key={topic}
                  className={`ret-picker-chip ${isSelected(topic, subject) ? 'selected' : ''}`}
                  onClick={() => toggleTopic(topic, subject)}
                >
                  {isSelected(topic, subject) ? '✓ ' : ''}{topic}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      {selected.length > 0 && (
        <div className="ret-picker-footer">
          <span>{selected.length} topic{selected.length > 1 ? 's' : ''} selected</span>
          <button className="ret-btn-start" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Adding...' : `Add ${selected.length} Topic${selected.length > 1 ? 's' : ''}`}
          </button>
        </div>
      )}
    </div>
  );
}
