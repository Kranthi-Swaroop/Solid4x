export { calcSubjectScore, scoreQuestion } from './scoring'

export function analyzeConceptStrength(questions, answers, times) {
  const conceptMap = {}
  
  questions.forEach(q => {
    const key = q.topic
    if (!conceptMap[key]) {
      conceptMap[key] = {
        topic: q.topic, chapter: q.chapter, subject: q.subject,
        total: 0, correct: 0, totalTime: 0, questions: []
      }
    }
    const { verdict } = scoreQuestion_inline(q, answers[q.question_id])
    conceptMap[key].total++
    if (verdict === 'correct') conceptMap[key].correct++
    conceptMap[key].totalTime += times[q.question_id] || 0
    conceptMap[key].questions.push({
      id: q.question_id, verdict,
      time: times[q.question_id] || 0
    })
  })
  
  return Object.values(conceptMap).map(c => {
    const accuracy = c.total ? c.correct / c.total : 0
    const avgTime = c.total ? c.totalTime / c.total : 0
    
    // Quality of Time: high accuracy + reasonable time = strong
    let strength
    if (accuracy >= 0.7 && avgTime <= 180)      strength = 'strong'
    else if (accuracy >= 0.4 || avgTime <= 120)  strength = 'weak'
    else                                          strength = 'poor'
    
    return { ...c, accuracy: Math.round(accuracy*100), avgTime, strength }
  }).sort((a,b) => a.accuracy - b.accuracy)
}

function scoreQuestion_inline(q, ans) {
  if (!ans && ans !== 0) return { verdict: 'unattempted' }
  if (q.type === 'mcq')
    return { verdict: ans === q.correct_options[0] ? 'correct' : 'incorrect' }
  if (q.type === 'integer')
    return { verdict: parseInt(ans) === parseInt(q.correct_answer) 
             ? 'correct' : 'incorrect' }
  return { verdict: 'unattempted' }
}

export function qualityOfTimeSpent(questions, answers, times) {
  // Penalize: too long on wrong answers, too short on correct ones
  let score = 0
  let total = 0
  questions.forEach(q => {
    const t = times[q.question_id] || 0
    const { verdict } = scoreQuestion_inline(q, answers[q.question_id])
    if (verdict === 'unattempted') return
    total++
    if (verdict === 'correct' && t >= 30)  score++        // spent time, got right
    if (verdict === 'correct' && t < 30)   score += 0.5   // too fast but correct
    if (verdict === 'incorrect' && t > 120) score -= 0.5  // wasted time
    if (verdict === 'incorrect' && t <= 60) score += 0.3  // moved on quickly
  })
  if (!total) return 0
  return Math.min(100, Math.max(0, Math.round((score / total) * 100)))
}
