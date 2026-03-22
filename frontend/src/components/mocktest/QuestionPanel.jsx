import React, { useEffect } from 'react';
import './mocktest.css';

export default function QuestionPanel({ 
  question, answer, onAnswer, total,
  onSaveAndNext, onClear, onSaveAndMark, onMarkAndNext,
  onBack, onGoNext, onSubmit, isFirst, isLast
}) {
  
  // MathJax injection and typesetting
  useEffect(() => {
    if (!document.getElementById('mathjax-script')) {
      const script = document.createElement('script');
      script.id = 'mathjax-script';
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
      script.async = true;
      document.head.appendChild(script);
    }
  }, []);

  useEffect(() => {
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise().catch(err => console.log("MathJax error:", err));
    }
  }, [question]);

  if (!question || !question.question_id) return <div className="jee-q-panel empty">Loading Question...</div>;

  const handleChange = (val) => {
    onAnswer(question.question_id, val);
  };

  const handleIntChange = (e) => {
    const val = e.target.value;
    // Allow only digits and minus sign
    if (val === '' || /^-?\d*$/.test(val)) {
      handleChange(val);
    }
  };

  const qNum = question.global_index;

  const diffColor = {
    easy: '#22c55e',
    medium: '#f59e0b',
    hard: '#ef4444'
  }[question.difficulty] || '#64748b';

  return (
    <div className="jee-q-panel">
      <div className="jee-q-header-complex">
        <div className="jee-q-headline">
          <span className="jee-q-number-title">Question {qNum} of {total}</span>
          <div className="jee-q-badges">
            <span className="jee-badge-year">JEE {question.year}</span>
            <span className="jee-badge-diff" style={{ backgroundColor: diffColor }}>
              {question.difficulty?.toUpperCase()}
            </span>
          </div>
        </div>
        <div className="jee-q-chapter">{question.chapter}</div>
      </div>
      
      <div className="jee-q-text-area">
        <div dangerouslySetInnerHTML={{ __html: question.question_text }} />
      </div>

      <div className="jee-q-options-area">
        {question.type === 'mcq' ? (
          <div className="jee-mcq-grid">
            {question.options?.map((opt, idx) => {
              // The JSON options array contains items like { identifier: 'A', content: '...' }
              // Wait, the dummy data in json has objects for options now.
              let id = opt.identifier;
              let content = opt.content;
              const isSelected = answer === id;
              
              return (
                <button 
                  key={idx}
                  className={`jee-mcq-option-btn ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleChange(id)}
                >
                  <div className="jee-mcq-letter">{id}</div>
                  <div className="jee-mcq-content" dangerouslySetInnerHTML={{ __html: content }} />
                </button>
              );
            })}
          </div>
        ) : (
          <div className="jee-integer-area">
            <input 
              type="text" 
              className="jee-int-input"
              placeholder="Enter integer answer" 
              value={answer || ''}
              onChange={handleIntChange}
            />
            <p className="jee-int-hint">Enter an integer value</p>
          </div>
        )}
      </div>

      <div className="jee-q-actions">
        <button className="jee-btn-action save-next" onClick={onSaveAndNext}>SAVE & NEXT</button>
        <button className="jee-btn-action clear" onClick={onClear}>CLEAR</button>
        <button className="jee-btn-action save-mark" onClick={onSaveAndMark}>SAVE & MARK FOR REVIEW</button>
        <button className="jee-btn-action mark-next" onClick={onMarkAndNext}>MARK FOR REVIEW & NEXT</button>
      </div>

      <div className="jee-q-nav-row">
        <div className="jee-nav-left">
          <button className="jee-btn-nav" onClick={onBack} disabled={isFirst}>&lt;&lt; BACK</button>
          <button className="jee-btn-nav" onClick={onGoNext} disabled={isLast}>NEXT &gt;&gt;</button>
        </div>
        <button className="jee-btn-nav submit" onClick={onSubmit}>SUBMIT</button>
      </div>
    </div>
  );
}
