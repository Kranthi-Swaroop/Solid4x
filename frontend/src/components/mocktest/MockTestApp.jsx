import React, { useState, useEffect, useRef, useCallback } from 'react';
import TestInterface from './TestInterface';
import ResultDashboard from './ResultDashboard';
import { TimeTracker } from './utils/timeTracker';
import './mocktest.css';

const TOTAL_TIME = 3 * 60 * 60; // 3 hours

export default function MockTestApp() {
  const [view, setView] = useState('dashboard');
  const [history, setHistory] = useState([]);
  const [ongoingTest, setOngoingTest] = useState(null);
  const [practiceQuestions, setPracticeQuestions] = useState([]);
  const [practiceAnswers, setPracticeAnswers] = useState({});
  const [practiceSubmitted, setPracticeSubmitted] = useState({});
  const [loading, setLoading] = useState(true);

  const [allQuestions, setAllQuestions] = useState([]);
  const [questionsBySubject, setQuestionsBySubject] = useState({});
  const [testId, setTestId] = useState(null);

  const [answers, setAnswers] = useState({});
  const [markedForReview, setMarkedForReview] = useState({});
  const [visited, setVisited] = useState({});
  const [timeLeft, setTimeLeft] = useState(TOTAL_TIME);
  const [resultData, setResultData] = useState(null);

  const trackerRef = useRef(new TimeTracker());
  const profileId = localStorage.getItem('profileId') || "test_user";

  useEffect(() => {
    fetchHistory();
    checkOngoing();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/tests/history/${profileId}`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data.reverse());
      }
    } catch (e) { console.error(e); }
  };

  const checkOngoing = async () => {
    try {
      const res = await fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/tests/ongoing/${profileId}`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.test_id) {
          setOngoingTest(data);
        }
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const loadTestPayload = (data) => {
    setTestId(data.test_id);
    let globalIndex = 0;
    const flatArr = [];
    const grouped = {};
    ['Physics', 'Chemistry', 'Mathematics'].forEach(sub => {
      const qList = data.questions_by_subject[sub] || [];
      const combined = qList.map(q => {
        globalIndex++;
        return { ...q, subject: sub, global_index: globalIndex };
      });
      grouped[sub] = combined;
      flatArr.push(...combined);
    });
    setAllQuestions(flatArr);
    setQuestionsBySubject(grouped);
  };

  const startNewTest = async () => {
    setLoading(true);
    setView('instructions');
    try {
      const res = await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/tests/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: profileId, subjects: ['Physics', 'Chemistry', 'Mathematics'] })
      });
      if (res.ok) {
        const data = await res.json();
        loadTestPayload(data);
        setTimeLeft(TOTAL_TIME);
        setView('test');
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const resumeOngoing = () => {
    if (ongoingTest) {
      loadTestPayload(ongoingTest);
      setTimeLeft(Math.floor(ongoingTest.time_left));
      setView('test');
    }
  };

  const getNumericalAttempted = useCallback((subject) => {
    return allQuestions
      .filter(q => q.subject === subject && q.type === 'integer')
      .filter(q => answers[q.question_id] !== undefined && answers[q.question_id] !== null && answers[q.question_id] !== '')
      .length;
  }, [allQuestions, answers]);

  // Ping timer heartbeat every 60 seconds protecting active browser session limits
  useEffect(() => {
    if (view !== 'test' || !testId) return;
    const pingTimer = setInterval(() => {
      fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/tests/ping/${testId}`, { method: 'POST' }).catch(e => console.error(e));
    }, 60000);
    return () => clearInterval(pingTimer);
  }, [view, testId]);

  useEffect(() => {
    if (view !== 'test') return;
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [view]);

  const handleAnswer = useCallback((question_id, value) => {
    const question = allQuestions.find(q => q.question_id === question_id);
    if (question && question.type === 'integer') {
      const currentAns = answers[question_id];
      const isAlreadyAnswered = currentAns !== undefined && currentAns !== null && currentAns !== '';
      const isNewAnswer = value !== null && value !== undefined && value !== '';
      if (!isAlreadyAnswered && isNewAnswer) {
        if (getNumericalAttempted(question.subject) >= 5) return;
      }
    }
    setAnswers(prev => ({ ...prev, [question_id]: value }));
    setVisited(prev => ({ ...prev, [question_id]: true }));
  }, [allQuestions, answers, getNumericalAttempted]);

  const handleMarkForReview = useCallback((question_id) => {
    setMarkedForReview(prev => ({ ...prev, [question_id]: !prev[question_id] }));
  }, []);

  const handleNavigate = useCallback((question_id) => {
    trackerRef.current.startQuestion(question_id);
    setVisited(prev => ({ ...prev, [question_id]: true }));
  }, []);

  const handleSubmit = useCallback(async () => {
    trackerRef.current.stopCurrent();
    const times = trackerRef.current.getAllTimes();

    const submissionAnswers = allQuestions.map(q => {
      const userAns = answers[q.question_id];
      const answered = userAns !== undefined && userAns !== null && userAns !== '';

      let isCorrect = false;
      if (answered) {
        if (q.correct_options && q.correct_options.length > 0) {
          isCorrect = q.correct_options.some(opt => String(opt).trim().toLowerCase() === String(userAns).trim().toLowerCase());
        } else if (q.options) {
          const correctOpt = q.options.find(o => o.is_correct);
          if (correctOpt) {
            isCorrect = String(correctOpt.value).trim().toLowerCase() === String(userAns).trim().toLowerCase() || String(correctOpt.id) === String(userAns);
          }
        } else if (q.answer) {
          isCorrect = String(q.answer).trim().toLowerCase() === String(userAns).trim().toLowerCase();
        }
      }
      return {
        question_id: q.question_id,
        is_correct: isCorrect,
        time_spent: times[q.question_id] || 0,
        selected_option: userAns === undefined || userAns === null ? '' : String(userAns)
      };
    });

    setLoading(true);
    try {
      const res = await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/tests/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: profileId,
          test_id: testId,
          answers: submissionAnswers
        })
      });
      if (res.ok) {
        const payload = await res.json();
        setResultData(payload);
        fetchHistory();
        setView('result');
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [allQuestions, answers, testId, profileId]);

  const viewHistoricalTest = (h) => {
    if (h.status !== 'completed') return;
    setTestId(h.test_id);
    const allQs = [];
    const subjectsMap = {};
    if (h.questions_by_subject) {
      Object.keys(h.questions_by_subject).forEach(subj => {
        subjectsMap[subj] = h.questions_by_subject[subj];
        allQs.push(...h.questions_by_subject[subj]);
      });
    }
    setAllQuestions(allQs);
    setQuestionsBySubject(subjectsMap);
    
    setAnswers(h.student_answers || {});
    // Populate tracker mock times dynamically if needed. Handled via h.student_times natively in AnswerReview component layout mapping.
    
    // Create an artificial map to restore trackers dynamically simulating metrics
    if (h.student_times) {
      Object.keys(h.student_times).forEach(qId => {
         trackerRef.current.times[qId] = h.student_times[qId];
      });
    }

    setResultData(h);
    setView('result');
  };

  const handlePracticeSimilar = async (questionId) => {
    setLoading(true);
    setPracticeAnswers({});
    setPracticeSubmitted({});
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`http://localhost:8000/api/v1/practice/similar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ question_id: questionId, limit: 3 })
      });
      if (res.ok) {
        const data = await res.json();
        setPracticeQuestions(data);
        setView('practice_similar');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const submitPracticeQuestion = async (q) => {
    const userAns = practiceAnswers[q.question_id];
    if (userAns === undefined || userAns === '') return;

    let isCorrect = false;
    if (q.type === 'mcq') {
       isCorrect = q.correct_options?.includes(userAns);
    } else {
       const correctVal = String(q.correct_answer || q.answer).trim().toLowerCase();
       isCorrect = correctVal === String(userAns).trim().toLowerCase();
    }

    setPracticeSubmitted(prev => ({ ...prev, [q.question_id]: isCorrect ? 'correct' : 'incorrect' }));

    try {
       const token = localStorage.getItem('token');
       await fetch(`http://localhost:8000/api/v1/practice/submit`, {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json',
               ...(token ? { 'Authorization': `Bearer ${token}` } : {})
           },
           body: JSON.stringify({
               user_id: profileId,
               question_id: q.question_id,
               is_correct: isCorrect,
               time_spent: 30
           })
       });
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    if (view === 'practice_similar' && window.MathJax) {
      setTimeout(() => {
        window.MathJax.typesetPromise().catch(err => console.error(err));
      }, 100);
    }
  }, [view, practiceQuestions]);

  if (loading && view === 'dashboard') return <div style={{ padding: '2rem' }}>Loading Secure Servers...</div>;

  if (view === 'dashboard') {
    return (
      <div style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto', fontFamily: 'sans-serif' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>JEE Mock Test Arena</h1>
        {ongoingTest && (
          <div style={{ background: '#ffeeba', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', border: '1px solid #ffdf7e' }}>
            <h3 style={{ color: '#856404' }}>⚠️ Ongoing Test Detected!</h3>
            <p style={{ color: '#856404' }}>You closed the secure browser interface during an active Mock Test. You have less than 10 minutes to reconnect before the simulation actively fails your progress.</p>
            <button onClick={resumeOngoing} style={{ background: '#d39e00', color: '#fff', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Resume Test Operations</button>
          </div>
        )}
        <div style={{ marginBottom: '2rem', background: '#f8f9fa', padding: '2rem', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <h2 style={{ fontSize: '1.8rem', color: '#343a40' }}>Commence New Mock Test</h2>
          <p style={{ fontSize: '1.1rem' }}>Strictly simulated 90-Question JEE Format (20 MCQs, 10 Numerical per Subject - Attempt any 5).</p>
          <p style={{ color: '#d9534f', fontWeight: 'bold' }}>Warning: This test strictly requires 3 unbroken hours. Severing the HTTP browser link abandons your payload in 10 minutes autonomously.</p>
          <button onClick={() => setView('instructions')} style={{ background: '#007bff', color: 'white', padding: '12px 24px', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px', fontSize: '1.1rem', fontWeight: 'bold', boxShadow: '0 2px 4px rgba(0,123,255,0.4)' }}>Proceed to Secure Platform</button>
        </div>

        <h2 style={{ fontSize: '1.8rem' }}>Historical Performance Cache</h2>
        {history.length === 0 ? <p>No completed architectures located.</p> : (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '15px', background: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
            <thead>
              <tr style={{ background: '#e9ecef', textAlign: 'left' }}>
                <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>Simulation Datetime</th>
                <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>Total Questions</th>
                <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>Aggregate Grade</th>
                <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6' }}>Network Flag</th>
              </tr>
            </thead>
            <tbody>
              {history.map(h => (
                <tr key={h.test_id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: '12px' }}>{new Date(h.created_at).toLocaleString()}</td>
                  <td style={{ padding: '12px' }}>{h.total_questions || 75}</td>
                  <td style={{ padding: '12px', color: (h.score > 100) ? '#28a745' : '#d9534f' }}><b>{h.score !== undefined ? `${h.score}/300` : 'Not Scored'}</b></td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ background: h.status === 'completed' ? '#d4edda' : (h.status === 'ongoing' ? '#fff3cd' : '#f8d7da'), padding: '4px 8px', borderRadius: '4px', fontSize: '0.9rem', color: h.status === 'completed' ? '#155724' : (h.status === 'ongoing' ? '#856404' : '#721c24') }}>
                      {h.status || 'unknown'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    {h.status === 'completed' && (
                       <button onClick={() => viewHistoricalTest(h)} style={{ background: '#007bff', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>View Report</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  }

  if (view === 'instructions') {
    return (
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif', background: '#fff', boxShadow: '0 4px 8px rgba(0,0,0,0.1)', borderRadius: '8px', marginTop: '40px' }}>
        <h2 style={{ borderBottom: '2px solid #007bff', paddingBottom: '10px' }}>Security Rules & Instructions</h2>
        <ul style={{ lineHeight: '1.8', fontSize: '1.1rem', marginTop: '20px' }}>
          <li><b>1.</b> The rigorous topological simulation operates continuously for exactly 180 mathematical minutes.</li>
          <li><b>2.</b> Subjects map precisely 20 standard MCQs and 10 Numerical constructs mathematically. You are permitted merely 5 integer attempts overall per subject.</li>
          <li><b>3.</b> System executes a strict +4/-1 Marking standard logically against your submitted vectors.</li>
          <li><b>4.</b> The testing architecture computationally pings standard HTTP tokens every 60s natively. Closing your interface permanently forfeits your score within exactly 10 minutes!</li>
        </ul>
        <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <button onClick={startNewTest} disabled={loading} style={{ background: '#28a745', color: 'white', padding: '15px 30px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '1.2rem', fontWeight: 'bold' }}>
            {loading ? 'Synthesizing Topology...' : 'Acknowledge Rules & Begin'}
          </button>
          <button onClick={() => setView('dashboard')} style={{ background: 'transparent', color: '#007bff', padding: '15px', border: 'none', cursor: 'pointer', marginLeft: '20px', fontSize: '1.1rem' }}>Abort Routine</button>
        </div>
      </div>
    );
  }

  if (view === 'test') {
    return (
      <div style={{ position: 'relative' }}>
        {loading && (
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(255,255,255,0.9)', zIndex: 9999, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
            <h2 style={{ color: '#007bff', fontSize: '2rem', marginBottom: '10px' }}>Evaluating Topology...</h2>
            <p style={{ fontSize: '1.2rem', color: '#343a40' }}>Crunching 90 Mathematical Vectors natively in the backend.</p>
            <div style={{ marginTop: '20px', width: '50px', height: '50px', border: '5px solid #f3f3f3', borderTop: '5px solid #007bff', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
            <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          </div>
        )}
        <TestInterface
          allQuestions={allQuestions}
          answers={answers}
          markedForReview={markedForReview}
          visited={visited}
          timeLeft={timeLeft}
          onAnswer={handleAnswer}
          onMark={handleMarkForReview}
          onNavigate={handleNavigate}
          onSubmit={handleSubmit}
          getNumericalAttempted={getNumericalAttempted}
        />
      </div>
    );
  }

  if (view === 'practice_similar') {
    return (
      <div style={{ padding: '2rem', background: '#f8f9fa', minHeight: '100vh' }}>
        <style dangerouslySetInnerHTML={{__html: `
          .jee-mcq-inline-math mjx-container[display="true"] {
            display: inline-block !important;
            margin: 0 !important;
          }
        `}} />
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '2rem', color: '#343a40', margin: 0 }}>Practice Similar Concept Vectors</h2>
            <button onClick={() => setView('result')} style={{ background: '#6c757d', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
              Back to Test Report
            </button>
          </div>
          
          {practiceQuestions.length === 0 && <p style={{ fontSize: '1.2rem', color: '#dc3545' }}>No active topological structures located...</p>}
          
          {practiceQuestions.map((q, idx) => (
             <div key={q.question_id} style={{ marginBottom: '30px', background: 'white', padding: '25px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', border: '1px solid #dee2e6' }}>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '15px' }}>
                  <span style={{ background: '#007bff', color: 'white', padding: '4px 12px', borderRadius: '20px', fontWeight: 'bold' }}>Variant {idx + 1}</span>
                  <span style={{ background: '#e9ecef', color: '#495057', padding: '4px 10px', borderRadius: '4px', fontSize: '0.9rem' }}>{q.chapter || 'Concept'}</span>
                  <span style={{ background: q.difficulty === 'EASY' ? '#d4edda' : q.difficulty === 'HARD' ? '#f8d7da' : '#fff3cd', color: q.difficulty === 'EASY' ? '#155724' : q.difficulty === 'HARD' ? '#721c24' : '#856404', padding: '4px 10px', borderRadius: '4px', fontSize: '0.9rem', fontWeight: 'bold' }}>{q.difficulty}</span>
                </div>
                
                <div dangerouslySetInnerHTML={{ __html: q.question_text }} style={{ fontSize: '1.1rem', color: '#212529', lineHeight: '1.6', marginBottom: '20px' }} />
                
                {q.type === 'mcq' ? (
                   <div style={{ display: 'grid', gap: '10px' }}>
                      {q.options?.map(opt => {
                         const isSelected = practiceAnswers[q.question_id] === opt.identifier;
                         const isSubmitted = !!practiceSubmitted[q.question_id];
                         const isCorrectOpt = q.correct_options?.includes(opt.identifier);
                         
                         let bg = '#f8f9fa';
                         let border = '1px solid #ced4da';
                         if (isSubmitted) {
                             if (isCorrectOpt) { bg = '#d4edda'; border = '2px solid #28a745'; }
                             else if (isSelected && !isCorrectOpt) { bg = '#f8d7da'; border = '2px solid #dc3545'; }
                         } else if (isSelected) {
                             bg = '#e2e6ea'; border = '2px solid #007bff';
                         }
                         
                         return (
                           <div 
                             key={opt.identifier} 
                             onClick={() => {
                                if (!isSubmitted) setPracticeAnswers(prev => ({ ...prev, [q.question_id]: opt.identifier }));
                             }}
                             style={{ display: 'flex', gap: '15px', alignItems: 'center', padding: '12px 15px', border, borderRadius: '8px', background: bg, cursor: isSubmitted ? 'default' : 'pointer', transition: 'all 0.2s' }}>
                              <strong style={{ color: '#495057', fontSize: '1.2rem', minWidth: '30px' }}>{opt.identifier})</strong>
                              <div className="jee-mcq-inline-math" dangerouslySetInnerHTML={{ __html: opt.content || '' }} style={{ flex: 1, color: '#343a40', overflowWrap: 'break-word' }} />
                           </div>
                         );
                      })}
                   </div>
                ) : (
                   <div style={{ padding: '15px', background: '#e9ecef', borderRadius: '8px', border: '1px solid #ced4da', color: '#495057' }}>
                      <input 
                         type="text" 
                         value={practiceAnswers[q.question_id] || ''} 
                         onChange={(e) => setPracticeAnswers(prev => ({ ...prev, [q.question_id]: e.target.value }))}
                         disabled={!!practiceSubmitted[q.question_id]}
                         placeholder="Enter numerical integer..." 
                         style={{ width: '100%', padding: '12px', fontSize: '1.1rem', border: '1px solid #ccc', borderRadius: '4px' }} 
                      />
                   </div>
                )}
                
                {!practiceSubmitted[q.question_id] ? (
                   <div style={{ marginTop: '20px' }}>
                      <button 
                        onClick={() => submitPracticeQuestion(q)} 
                        disabled={practiceAnswers[q.question_id] === undefined || String(practiceAnswers[q.question_id]).trim() === ''} 
                        style={{ background: '#007bff', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                        Submit Question Matrix
                      </button>
                   </div>
                ) : (
                   <div style={{ marginTop: '25px', padding: '20px', background: '#f8f9fa', borderRadius: '6px', border: practiceSubmitted[q.question_id] === 'correct' ? '2px solid #28a745' : '2px solid #dc3545' }}>
                      <h4 style={{ color: practiceSubmitted[q.question_id] === 'correct' ? '#28a745' : '#dc3545', margin: '0 0 10px 0', fontSize: '1.2rem' }}>
                         {practiceSubmitted[q.question_id] === 'correct' ? 'Exact Form Calculated! ✅' : 'Incorrect Topology ❌'}
                      </h4>
                      <p style={{ margin: '0 0 15px 0', fontSize: '1.1rem' }}>
                        <strong>Exact Mathematical Form: </strong> 
                        <span style={{ background: '#d4edda', color: '#155724', padding: '4px 10px', borderRadius: '4px', fontWeight: 'bold', marginLeft: '10px' }}>
                          {q.type === 'mcq' ? q.correct_options?.join(', ') : (q.correct_answer || q.answer)}
                        </span>
                      </p>
                      {q.explanation && (
                         <details onToggle={(e) => {
                             if (e.target.open && window.MathJax) {
                                 setTimeout(() => window.MathJax.typesetPromise().catch(err => console.error(err)), 50);
                             }
                         }}>
                            <summary style={{ cursor: 'pointer', color: '#17a2b8', fontWeight: 'bold', fontSize: '1.1rem', padding: '10px', background: '#e0f3f5', borderRadius: '6px', border: '1px solid #bee5eb' }}>
                              Expand Official Solution Architecture 👁️
                            </summary>
                            <div style={{ marginTop: '15px', padding: '20px', background: '#fff', borderRadius: '6px', border: '1px dashed #ced4da' }}>
                               <h5 style={{ margin: '0 0 10px 0', color: '#6c757d', textTransform: 'uppercase', letterSpacing: '1px' }}>Structural Explanation</h5>
                               <div dangerouslySetInnerHTML={{ __html: q.explanation }} style={{ color: '#343a40', lineHeight: '1.7', overflowX: 'auto' }} />
                            </div>
                         </details>
                      )}
                   </div>
                )}
             </div>
          ))}
        </div>
      </div>
    );
  }

  if (view === 'result') {
    return (
      <div style={{ padding: '2rem', background: '#f8f9fa', minHeight: '100vh' }}>
        <h1 style={{ color: '#28a745' }}>Test Architecture Collapsed & Scored Successfully!</h1>
        <h2 style={{ fontSize: '2rem', background: '#fff', display: 'inline-block', padding: '10px 20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>Final Grade Evaluated: <span style={{ color: '#007bff' }}>{resultData?.score} / 300</span></h2>
        <br />
        <button onClick={() => { setView('dashboard'); setAnswers({}); setAllQuestions([]); }} style={{ background: '#007bff', color: 'white', padding: '12px 24px', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '20px', fontSize: '1.1rem' }}>Return to Native Dashboard</button>
        <div style={{ marginTop: '2rem', background: '#fff', borderRadius: '8px', padding: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <ResultDashboard
            allQuestions={allQuestions}
            answers={answers}
            times={trackerRef.current.getAllTimes()}
            questionsBySubject={questionsBySubject}
            onPracticeSimilar={handlePracticeSimilar}
          />
        </div>
      </div>
    );
  }

  return null;
}
