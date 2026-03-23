import React, { useState, useEffect } from 'react';

export default function SpacedRepetitionPractice({ topic, onClose }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/practice/generate?topic=${encodeURIComponent(topic)}&limit=5`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setQuestions(data);
        }
      } catch (err) {
        console.error("Failed to load topic practice", err);
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, [topic]);

  useEffect(() => {
    if (window.MathJax && !loading) {
      setTimeout(() => {
        window.MathJax.typesetPromise().catch(err => console.error(err));
      }, 100);
    }
  }, [questions, loading]);

  const submitQuestion = async (q) => {
    const userAns = answers[q.question_id];
    if (!userAns && userAns !== 0) return;

    let isCorrect = false;
    if (q.type === 'mcq') {
      isCorrect = q.correct_options?.includes(userAns);
    } else {
      const correctVal = String(q.correct_answer || q.answer).trim().toLowerCase();
      isCorrect = correctVal === String(userAns).trim().toLowerCase();
    }

    setSubmitted(prev => ({ ...prev, [q.question_id]: isCorrect ? 'correct' : 'incorrect' }));

    // Update Knowledge Graph through the exact backend proxy
    try {
      const token = localStorage.getItem('token');
      await fetch('https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/practice/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: "temp", // Fast API will extract actual from JWT
          question_id: q.question_id,
          is_correct: isCorrect,
          time_spent: 30
        })
      });
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}><h2>Generating Problem Set for {topic}...</h2></div>;
  }

  if (questions.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', background: '#fff', borderRadius: '8px', border: '1px solid #dee2e6' }}>
        <h3>You have perfectly exhausted the Question Bank for this Topic!</h3>
        <p>Congratulations. Return to Dashboard to pick a new topic.</p>
        <button onClick={onClose} style={{ marginTop: '20px', padding: '10px 20px', background: '#343a40', color: 'white', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>Back to Dashboard</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', background: '#f8f9fa', minHeight: '100vh' }}>
      <style dangerouslySetInnerHTML={{
        __html: `
        .jee-mcq-inline-math mjx-container[display="true"] {
          display: inline-block !important;
          margin: 0 !important;
        }
      `}} />
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '2rem', color: '#343a40', margin: 0 }}>Spaced Repetition: {topic}</h2>
            <p style={{ color: '#6c757d', margin: '5px 0 0 0' }}>Mastery Target: 5 Questions</p>
          </div>
          <button
            onClick={onClose}
            style={{ padding: '10px 20px', backgroundColor: '#6c757d', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
            &larr; Return to Active Retention Graph
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          {questions.map((q, index) => {
            const userAns = answers[q.question_id];
            const isSubmitted = submitted[q.question_id];

            return (
              <div key={q.question_id} style={{ background: '#fff', padding: '25px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', borderLeft: '5px solid #007bff' }}>
                <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
                  <div style={{ background: '#e9ecef', color: '#495057', width: '35px', height: '35px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', fontWeight: 'bold', fontSize: '1.2rem', flexShrink: 0 }}>
                    {index + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div dangerouslySetInnerHTML={{ __html: q.question_text }} style={{ fontSize: '1.15rem', color: '#212529', lineHeight: '1.6', overflowX: 'auto' }} />
                  </div>
                </div>

                {/* Options or Integer Input */}
                <div style={{ marginLeft: '50px', display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '25px' }}>
                  {q.type === 'mcq' ? (
                    q.options?.map(opt => {
                      const isSelected = userAns === opt.identifier;
                      let border = '1px solid #ced4da';
                      let bg = '#fff';

                      if (isSelected) { border = '2px solid #007bff'; bg = '#f1f8ff'; }
                      if (isSubmitted) {
                        if (q.correct_options?.includes(opt.identifier)) { border = '2px solid #28a745'; bg = '#d4edda'; }
                        else if (isSelected && !q.correct_options?.includes(opt.identifier)) { border = '2px solid #dc3545'; bg = '#f8d7da'; }
                      }

                      return (
                        <div
                          key={opt.identifier}
                          onClick={() => {
                            if (!isSubmitted) setAnswers(prev => ({ ...prev, [q.question_id]: opt.identifier }));
                          }}
                          style={{ display: 'flex', gap: '15px', alignItems: 'center', padding: '12px 15px', border, borderRadius: '8px', background: bg, cursor: isSubmitted ? 'default' : 'pointer', transition: 'all 0.2s' }}>
                          <strong style={{ color: '#495057', fontSize: '1.2rem', minWidth: '30px' }}>{opt.identifier})</strong>
                          <div className="jee-mcq-inline-math" dangerouslySetInnerHTML={{ __html: opt.content || '' }} style={{ flex: 1, color: '#343a40', overflowWrap: 'break-word' }} />
                        </div>
                      );
                    })
                  ) : (
                    <div>
                      <input
                        type="text"
                        disabled={isSubmitted}
                        placeholder="Enter your exact numerical answer"
                        value={userAns || ''}
                        onChange={(e) => setAnswers(prev => ({ ...prev, [q.question_id]: e.target.value }))}
                        style={{ width: '100%', maxWidth: '300px', padding: '12px', fontSize: '1.1rem', border: '1px solid #ced4da', borderRadius: '6px' }}
                      />
                    </div>
                  )}
                </div>

                {/* Actions and Feedback */}
                <div style={{ marginLeft: '50px' }}>
                  {!isSubmitted ? (
                    <button
                      onClick={() => submitQuestion(q)}
                      disabled={!userAns && userAns !== 0}
                      style={{ padding: '10px 25px', background: (!userAns && userAns !== 0) ? '#6c757d' : '#28a745', color: '#fff', border: 'none', borderRadius: '6px', fontSize: '1.1rem', fontWeight: 'bold', cursor: (!userAns && userAns !== 0) ? 'not-allowed' : 'pointer' }}>
                      Submit Topology Evaluation
                    </button>
                  ) : (
                    <div style={{ border: `2px solid ${isSubmitted === 'correct' ? '#28a745' : '#dc3545'}`, borderRadius: '8px', padding: '20px', background: '#fff' }}>
                      <h4 style={{ margin: '0 0 10px 0', color: isSubmitted === 'correct' ? '#28a745' : '#dc3545', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {isSubmitted === 'correct' ? 'Exact Form Calculated! ✅' : 'Incorrect Topology ❌'}
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

              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
