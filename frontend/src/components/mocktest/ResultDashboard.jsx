import React, { useState } from 'react';
import SubjectReport from './SubjectReport';
import AnswerReview from './AnswerReview';
import { calcSubjectScore, analyzeConceptStrength, qualityOfTimeSpent } from './utils/analytics';
import './mocktest.css';

export default function ResultDashboard({ allQuestions, answers, times, questionsBySubject, onPracticeSimilar }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showReview, setShowReview] = useState(false);

  const subjects = ['Physics', 'Chemistry', 'Mathematics'];

  // Calculate overall stats
  let totalScore = 0;
  let totalCorrect = 0;
  let totalIncorrect = 0;
  let totalUnattempted = 0;
  let totalSeconds = 0;

  const subjectStats = {};

  subjects.forEach(sub => {
    const qList = questionsBySubject[sub] || [];
    const stats = calcSubjectScore(qList, answers, times);
    
    totalScore += stats.marks;
    totalCorrect += stats.correct;
    totalIncorrect += stats.incorrect;
    totalUnattempted += stats.unattempted;
    totalSeconds += stats.subjectTime;

    subjectStats[sub] = stats;
  });

  const accuracy = (totalCorrect + totalIncorrect) > 0 
    ? Math.round((totalCorrect / (totalCorrect + totalIncorrect)) * 100)
    : 0;

  const formatTime = (sec) => {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    return `${m}m ${s}s`;
  };

  const overallQuality = qualityOfTimeSpent(allQuestions, answers, times);
  const conceptData = analyzeConceptStrength(allQuestions, answers, times);
  const conceptStrength = {
    strong: conceptData.filter(c => c.strength === 'strong').map(c => c.topic),
    weak:   conceptData.filter(c => c.strength === 'weak').map(c => c.topic),
    poor:   conceptData.filter(c => c.strength === 'poor').map(c => c.topic)
  };

  if (showReview) {
    let reviewQuestions = allQuestions;
    if (activeTab !== 'overview') { // Changed from 'Overall' to 'overview'
      reviewQuestions = questionsBySubject[activeTab] || [];
    }
    return (
      <div className="mocktest-root">
      <div className="jee-results-page">
        <div className="jee-results-header">
          <h2>Test Review — {activeTab === 'overview' ? 'All Subjects' : activeTab}</h2> {/* Changed from 'Overall' to 'overview' */}
          <button className="jee-btn-nav" onClick={() => setShowReview(false)}>Back to Dashboard</button>
        </div>
        <AnswerReview questions={reviewQuestions} answers={answers} times={times} onPracticeSimilar={onPracticeSimilar} />
      </div>
      </div>
    );
  }

  return (
    <div className="mocktest-root">
    <div className="jee-results-page">
      <div className="jee-results-header">
        <h2>Test Completed — JEE Main Mock Test</h2>
        <p>{new Date().toLocaleString()}</p>
      </div>

      <div className="jee-results-tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''} 
          onClick={() => setActiveTab('overview')}
        >
          Overall
        </button>
        {subjects.map(sub => (
          <button 
            key={sub}
            className={activeTab === sub ? 'active' : ''} 
            onClick={() => setActiveTab(sub)}
          >
            {sub}
          </button>
        ))}
      </div>

      <div className="jee-results-content">
        {activeTab === 'overview' && (
          <div className="jee-overall-tab">
            <div className="jee-score-card">
              <h3>{totalScore} <span style={{ fontSize: '1.2rem', color: '#64748b' }}>/ 300</span></h3>
              <p>Total Score</p>
            </div>

            <div className="jee-stat-row">
              <div className="jee-stat-box correct">
                <div className="val">{totalCorrect}</div>
                <div className="lbl">Total Correct</div>
              </div>
              <div className="jee-stat-box incorrect">
                <div className="val">{totalIncorrect}</div>
                <div className="lbl">Total Incorrect</div>
              </div>
              <div className="jee-stat-box unattempted">
                <div className="val">{totalUnattempted}</div>
                <div className="lbl">Unattempted</div>
              </div>
              <div className="jee-stat-box neutral">
                <div className="val">{accuracy}%</div>
                <div className="lbl">Accuracy</div>
              </div>
              <div className="jee-stat-box neutral">
                <div className="val">{formatTime(totalSeconds)}</div>
                <div className="lbl">Time Taken</div>
              </div>
              <div className="jee-stat-box neutral">
                <div className="val">{overallQuality}</div>
                <div className="lbl">Quality of Time Score</div>
              </div>
            </div>

            <div className="jee-time-chart">
              <h3>Subject-wise Time</h3>
              {subjects.map(sub => {
                const subSec = subjectStats[sub]?.subjectTime || 0;
                const pct = totalSeconds > 0 ? (subSec / totalSeconds) * 100 : 0;
                return (
                  <div className="jee-chart-row" key={sub}>
                    <div className="jee-chart-lbl">{sub}</div>
                    <div className="jee-chart-bar-bg">
                      <div className="jee-chart-bar-fg" style={{ width: `${pct}%`, backgroundColor: '#3b82f6' }}></div>
                    </div>
                    <div className="jee-chart-val">{formatTime(subSec)}</div>
                  </div>
                );
              })}
            </div>

            <div className="jee-concept-strength">
              <h3>Concept Strength Summary</h3>
              <div className="jee-concept-cols">
                <div className="jee-concept-col strong">
                  <h4>Strong</h4>
                  {conceptStrength.strong?.map((c, i) => <div key={i} className="jee-chip green">{c}</div>)}
                </div>
                <div className="jee-concept-col weak">
                  <h4>Weak</h4>
                  {conceptStrength.weak?.map((c, i) => <div key={i} className="jee-chip orange">{c}</div>)}
                </div>
                <div className="jee-concept-col poor">
                  <h4>Poor</h4>
                  {conceptStrength.poor?.map((c, i) => <div key={i} className="jee-chip red">{c}</div>)}
                </div>
              </div>
            </div>
            
             <div style={{ marginTop: '30px', textAlign: 'center' }}>
                <button className="jee-btn-nav submit" onClick={() => setShowReview(true)}>Review All Answers</button>
            </div>
          </div>
        )}

        {subjects.includes(activeTab) && (
          <SubjectReport 
            subjectName={activeTab} 
            questions={questionsBySubject[activeTab] || []} 
            answers={answers} 
            times={times} 
            onViewReview={() => setShowReview(true)}
          />
        )}
      </div>
    </div>
    </div>
  );
}
