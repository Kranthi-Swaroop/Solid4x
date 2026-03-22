import React from 'react';
import './mocktest.css';

export default function QuestionGrid({ 
  allQuestions, activeSubject, currentQuestionId, 
  answers, markedForReview, visited, onJump 
}) {
  const subjectQuestions = allQuestions.filter(q => q.subject === activeSubject);

  const getStatusClass = (qId) => {
    if (!visited[qId]) return "not-visited";
    const isAns = answers[qId] !== undefined && answers[qId] !== null;
    const isMarked = markedForReview[qId];

    if (isAns && isMarked) return "ans-marked";
    if (!isAns && isMarked) return "marked";
    if (isAns && !isMarked) return "answered";
    return "not-answered";
  };

  return (
    <div className="jee-grid-panel">
      
      <div className="jee-legend">
        <div className="jee-legend-row">
          <div className="jee-legend-item"><span className="jee-badge not-visited"></span> Not Visited</div>
          <div className="jee-legend-item"><span className="jee-badge not-answered"></span> Not Answered</div>
        </div>
        <div className="jee-legend-row">
          <div className="jee-legend-item"><span className="jee-badge answered"></span> Answered</div>
          <div className="jee-legend-item"><span className="jee-badge marked"></span> Marked for Review</div>
        </div>
        <div className="jee-legend-row full">
          <div className="jee-legend-item"><span className="jee-badge ans-marked"></span> Answered & Marked for Review (will be considered for evaluation)</div>
        </div>
      </div>

      <div className="jee-grid-header">
        <h4>{activeSubject}</h4>
      </div>

      <div className="jee-grid-container">
        {subjectQuestions.map((q, idx) => {
          const status = getStatusClass(q.question_id);
          const isActive = q.question_id === currentQuestionId ? "active" : "";
          
          return (
            <button
              key={q.question_id}
              className={`jee-grid-btn ${status} ${isActive}`}
              onClick={() => onJump(q.global_index)}
            >
              <span className="jee-grid-index">{idx + 1}</span>
              {status === "ans-marked" && <span className="jee-dot"></span>}
            </button>
          );
        })}
      </div>

      <div className="jee-grid-footer">
        <button className="jee-btn-footer">Question Paper</button>
        <button className="jee-btn-footer">Instructions</button>
      </div>
    </div>
  );
}
