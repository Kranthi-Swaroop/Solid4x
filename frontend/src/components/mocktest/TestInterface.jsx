import React, { useState, useEffect } from 'react';
import SubjectTabs from './SubjectTabs';
import QuestionGrid from './QuestionGrid';
import QuestionPanel from './QuestionPanel';
import './mocktest.css';

export default function TestInterface({ 
  allQuestions, answers, markedForReview, visited, timeLeft, 
  onAnswer, onMark, onNavigate, onSubmit, getNumericalAttempted 
}) {
  const [activeSubject, setActiveSubject] = useState('Physics');
  const [currentIndex, setCurrentIndex] = useState(0); // 0-indexed in allQuestions

  const currentQuestion = allQuestions[currentIndex] || {};
  const currentQId = currentQuestion.question_id;

  // Initialize first question visit on mount
  useEffect(() => {
    if (allQuestions.length > 0 && currentQId) {
      if (!activeSubject) setActiveSubject(allQuestions[0].subject);
      onNavigate(currentQId);
    }
  }, []); // Run once

  const handleSubjectChange = (subject) => {
    setActiveSubject(subject);
    const firstQIndex = allQuestions.findIndex(q => q.subject === subject);
    if (firstQIndex !== -1) {
      setCurrentIndex(firstQIndex);
      onNavigate(allQuestions[firstQIndex].question_id);
    }
  };

  const handleJumpToQuestion = (globalIndex) => { // globalIndex is 1-based
    const targetIdx = globalIndex - 1;
    setCurrentIndex(targetIdx);
    const q = allQuestions[targetIdx];
    if (q.subject !== activeSubject) setActiveSubject(q.subject);
    onNavigate(q.question_id);
  };

  const goNext = () => {
    if (currentIndex < allQuestions.length - 1) {
      const nextIdx = currentIndex + 1;
      setCurrentIndex(nextIdx);
      const nextQ = allQuestions[nextIdx];
      if (nextQ.subject !== activeSubject) setActiveSubject(nextQ.subject);
      onNavigate(nextQ.question_id);
    }
  };

  const goBack = () => {
    if (currentIndex > 0) {
      const prevIdx = currentIndex - 1;
      setCurrentIndex(prevIdx);
      const prevQ = allQuestions[prevIdx];
      if (prevQ.subject !== activeSubject) setActiveSubject(prevQ.subject);
      onNavigate(prevQ.question_id);
    }
  };

  const handleSaveAndNext = () => goNext();
  
  const handleClear = () => onAnswer(currentQId, null);

  const handleSaveAndMarkReview = () => {
    if (!markedForReview[currentQId]) onMark(currentQId);
    goNext();
  };

  const handleMarkReviewAndNext = () => {
    if (!markedForReview[currentQId]) onMark(currentQId);
    goNext();
  };

  const formatSecs = (s) => {
    const hh = Math.floor(s / 3600).toString().padStart(2, '0');
    const mm = Math.floor((s % 3600) / 60).toString().padStart(2, '0');
    const ss = (s % 60).toString().padStart(2, '0');
    return `${hh}:${mm}:${ss}`;
  };

  return (
    <div className="mocktest-root">
      {/* TOP BAR */}
      <header className="jee-top-bar">
        <div className="jee-top-left">
          <div className="jee-avatar"></div>
          <div className="jee-cand-info">
            <span className="jee-cand-name">Candidate Name</span>
            <span className="jee-exam-name">JEE Main</span>
            <span className="jee-subject-name">{activeSubject}</span>
          </div>
        </div>
        <div className="jee-top-center">
          <SubjectTabs 
            allQuestions={allQuestions}
            activeSubject={activeSubject} 
            onSelect={handleSubjectChange} 
          />
        </div>
        <div className="jee-top-right">
          <div className="jee-timer">Time Left: <span>{formatSecs(timeLeft)}</span></div>
          <select className="jee-lang-select" defaultValue="en">
            <option value="en">English</option>
            <option value="hi">Hindi</option>
          </select>
        </div>
      </header>

      {/* WORKSPACE */}
      <div className="jee-workspace">
        <div className="jee-left-panel">
          <QuestionPanel 
            question={currentQuestion}
            answer={answers[currentQId]}
            onAnswer={onAnswer}
            total={allQuestions.length}
            onSaveAndNext={handleSaveAndNext}
            onClear={handleClear}
            onSaveAndMark={handleSaveAndMarkReview}
            onMarkAndNext={handleMarkReviewAndNext}
            onBack={goBack}
            onGoNext={goNext}
            onSubmit={onSubmit}
            isFirst={currentIndex === 0}
            isLast={currentIndex === allQuestions.length - 1}
            numericalLocked={currentQuestion.type === 'integer' && getNumericalAttempted(activeSubject) >= 5 && !(answers[currentQId] !== undefined && answers[currentQId] !== null && answers[currentQId] !== '')}
          />
        </div>
        <div className="jee-right-panel">
          <QuestionGrid 
            allQuestions={allQuestions}
            activeSubject={activeSubject}
            currentQuestionId={currentQId}
            answers={answers}
            markedForReview={markedForReview}
            visited={visited}
            onJump={handleJumpToQuestion}
          />
        </div>
      </div>
    </div>
  );
}
