import React from 'react';
import './mocktest.css';

const SUBJECTS = ['Physics', 'Chemistry', 'Mathematics'];

export default function SubjectTabs({ allQuestions, activeSubject, onSelect }) {
  const getCount = (sub) => allQuestions.filter(q => q.subject === sub).length;

  return (
    <div className="jee-subject-tabs">
      {SUBJECTS.map(sub => (
        <button
          key={sub}
          className={`jee-tab-btn ${activeSubject === sub ? 'active' : ''}`}
          onClick={() => onSelect(sub)}
        >
          <div className="jee-tab-title">{sub}</div>
          <div className="jee-tab-count">{getCount(sub)} Questions</div>
        </button>
      ))}
    </div>
  );
}
