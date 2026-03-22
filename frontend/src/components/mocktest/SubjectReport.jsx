import React from 'react';
import { calcSubjectScore, qualityOfTimeSpent } from './utils/analytics';
import './mocktest.css';

export default function SubjectReport({ subjectName, questions, answers, times, onViewReview }) {
  const stats = calcSubjectScore(questions, answers, times);
  const qos = qualityOfTimeSpent(questions, answers, times);
  
  const formatTime = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}m ${s}s`;
  };

  const accuracy = (stats.correct + stats.incorrect) > 0 
    ? Math.round((stats.correct / (stats.correct + stats.incorrect)) * 100)
    : 0;

  const mcqQuestions = questions.filter(q => q.type === 'mcq');
  const intQuestions = questions.filter(q => q.type === 'integer');
  const mcqStats = calcSubjectScore(mcqQuestions, answers, times);
  const intStats = calcSubjectScore(intQuestions, answers, times);

  return (
    <div className="jee-subject-report">
      <div className="jee-score-card">
        <h3>{stats.marks} <span style={{ fontSize: '1.2rem', color: '#64748b' }}>/ 100</span></h3>
        <p>{subjectName} Score</p>
      </div>

      <div className="jee-stat-row">
        <div className="jee-stat-box neutral">
          <div className="val">{stats.correct} / {stats.incorrect} / {stats.unattempted}</div>
          <div className="lbl">C / I / U</div>
        </div>
        <div className="jee-stat-box correct">
          <div className="val">+{stats.correct * 4}</div>
          <div className="lbl">Positive Marks</div>
        </div>
        <div className="jee-stat-box incorrect">
          <div className="val">-{stats.incorrect}</div>
          <div className="lbl">Negative Marks</div>
        </div>
        <div className="jee-stat-box neutral">
          <div className="val">{accuracy}%</div>
          <div className="lbl">Accuracy</div>
        </div>
        <div className="jee-stat-box neutral">
          <div className="val">{qos}</div>
          <div className="lbl">Quality of Time Score</div>
        </div>
        <div className="jee-stat-box neutral">
          <div className="val">{formatTime(stats.subjectTime)}</div>
          <div className="lbl">Time Spent</div>
        </div>
      </div>

      <div className="jee-section-stats">
        <div className="jee-section-card">
          <h4>MCQ Section</h4>
          <p>Questions: {mcqQuestions.length}</p>
          <p>Correct: {mcqStats.correct}</p>
          <p>Incorrect: {mcqStats.incorrect}</p>
          <p>Score: {mcqStats.marks}</p>
        </div>
        <div className="jee-section-card">
          <h4>Integer Section</h4>
          <p>Questions: {intQuestions.length}</p>
          <p>Correct: {intStats.correct}</p>
          <p>Incorrect: {intStats.incorrect}</p>
          <p>Score: {intStats.marks}</p>
        </div>
      </div>

      <div style={{ marginTop: '30px', textAlign: 'center' }}>
        <button className="jee-btn-nav submit" onClick={onViewReview}>View All Answers ({subjectName})</button>
      </div>
    </div>
  );
}
