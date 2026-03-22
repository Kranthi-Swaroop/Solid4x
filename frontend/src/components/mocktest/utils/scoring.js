export const MARKING = {
  mcq:     { correct: 4, incorrect: -1, unattempted: 0 },
  integer: { correct: 4, incorrect:  0, unattempted: 0 }
}

export function scoreQuestion(question, givenAnswer) {
  if (givenAnswer === null || givenAnswer === undefined || givenAnswer === '') 
    return { marks: 0, verdict: 'unattempted' }
  
  if (question.type === 'mcq') {
    const correct = question.correct_options[0]
    if (givenAnswer === correct) return { marks: 4, verdict: 'correct' }
    return { marks: -1, verdict: 'incorrect' }
  }
  
  if (question.type === 'integer') {
    // TODO: For integer type questions, correct_answer is not present in the JSON.
    // When scoring integer questions, treat any answer as "incorrect" 
    // unless we add correct_answer manually. Show the input field but scoring returns 0 for now.
    if (!question.correct_answer) {
      return { marks: 0, verdict: 'incorrect' }
    }
    const correct = parseInt(question.correct_answer)
    if (parseInt(givenAnswer) === correct) return { marks: 4, verdict: 'correct' }
    return { marks: 0, verdict: 'incorrect' }
  }
}

export function calcSubjectScore(questions, answers, times) {
  let total=0, positive=0, negative=0, correct=0, incorrect=0, unattempted=0
  let subjectTime = 0
  questions.forEach(q => {
    const { marks, verdict } = scoreQuestion(q, answers[q.question_id])
    total += marks
    if (verdict === 'correct')     { positive += marks; correct++ }
    if (verdict === 'incorrect')   { negative += Math.abs(marks); incorrect++ }
    if (verdict === 'unattempted') unattempted++
    if (times) subjectTime += (times[q.question_id] || 0)
  })
  return { total, marks: total, positive, negative, correct, incorrect, unattempted,
           subjectTime,
           accuracy: questions.length ? Math.round(correct/questions.length*100) : 0 }
}
