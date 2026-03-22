import React, { useState } from 'react';
import { scoreQuestion } from './utils/scoring';
import './mocktest.css';

export default function AnswerReview({ questions, answers, times }) {
  const [sortBy, setSortBy] = useState('number'); // 'number', 'time', 'verdict'
  const [expandedQs, setExpandedQs] = useState({});

  const toggleExpand = (id) => {
    setExpandedQs(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const formatTime = (sec) => {
    if (!sec) return '0s';
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  };

  const getReviewData = () => {
    return questions.map(q => {
      const ans = answers[q.question_id];
      const timeSpent = times[q.question_id] || 0;
      const result = scoreQuestion(q, ans);
      return { q, ans, timeSpent, result };
    });
  };

  let reviewList = getReviewData();

  if (sortBy === 'time') {
    reviewList.sort((a, b) => b.timeSpent - a.timeSpent);
  } else if (sortBy === 'verdict') {
    const order = { correct: 1, incorrect: 2, unattempted: 3 };
    reviewList.sort((a, b) => {
      if (order[a.result.verdict] !== order[b.result.verdict]) {
        return order[a.result.verdict] - order[b.result.verdict];
      }
      return a.q.global_index - b.q.global_index;
    });
  }

  return (
    <div className="jee-answer-review">
      <div className="jee-review-controls">
        <label>Sort by: </label>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="number">Question Number</option>
          <option value="time">Time Spent</option>
          <option value="verdict">Verdict</option>
        </select>
      </div>

      <div className="jee-review-list">
        {reviewList.map(({ q, ans, timeSpent, result }) => {
          const isExpanded = expandedQs[q.question_id];

          return (
            <div key={q.question_id} className="jee-review-card">
              <div className="jee-review-card-header">
                <div className="jee-rc-meta">
                  <span className="jee-rc-num">Q{q.global_index}</span>
                  <span className="jee-rc-chip">{q.topic || q.chapter}</span>
                  <span className={`jee-rc-diff ${q.difficulty}`}>{q.difficulty}</span>
                </div>
                <div className="jee-rc-stats">
                  <span className="jee-rc-time">⏱ {formatTime(timeSpent)}</span>
                  <span className={`jee-rc-verdict ${result.verdict}`}>
                    {result.verdict === 'correct' ? 'Correct ✓' : 
                     result.verdict === 'incorrect' ? 'Incorrect ✗' : 'Unattempted —'}
                  </span>
                  <span className={`jee-rc-marks ${result.marks > 0 ? 'pos' : result.marks < 0 ? 'neg' : 'zero'}`}>
                    {result.marks > 0 ? `+${result.marks}` : result.marks}
                  </span>
                </div>
              </div>

              <div className={`jee-rc-question ${isExpanded ? 'expanded' : 'collapsed'}`}>
                <div dangerouslySetInnerHTML={{ __html: q.question_text }} />
              </div>
              <button className="jee-rc-expand-btn" onClick={() => toggleExpand(q.question_id)}>
                {isExpanded ? 'Show Less' : 'Show Full Question'}
              </button>

              <div className="jee-rc-answers">
                {q.type === 'mcq' ? (
                  <div className="jee-rc-mcq-grid">
                    {q.options?.map((opt, idx) => {
                      const id = opt.identifier;
                      const content = opt.content;
                      const isCorrect = q.correct_options.includes(id);
                      const isSelected = ans === id;
                      
                      let optionClass = '';
                      if (isCorrect) optionClass = 'correct-opt';
                      else if (isSelected && !isCorrect) optionClass = 'wrong-opt';

                      return (
                        <div key={idx} className={`jee-rc-mcq-option ${optionClass}`}>
                          <div className="jee-rc-letter">{id}</div>
                          <div className="jee-rc-content" dangerouslySetInnerHTML={{ __html: content }} />
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="jee-rc-integer-ans">
                    <p><strong>Your answer:</strong> {ans !== undefined && ans !== null && ans !== '' ? ans : '—'}</p>
                    <p><strong>Correct answer:</strong> {q.correct_answer}</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
