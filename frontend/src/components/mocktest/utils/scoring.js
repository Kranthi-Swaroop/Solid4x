export const MARKING = {
  mcq:     { correct: 4, incorrect: -1, unattempted: 0 },
  integer: { correct: 4, incorrect:  0, unattempted: 0 }
}

export function extractIntegerAnswer(q) {
  if (q.correct_answer !== undefined && q.correct_answer !== null) return String(q.correct_answer);
  if (q.answer !== undefined && q.answer !== null) return String(q.answer);
  if (!q.explanation) return null;
  
  const textSplit = q.explanation.split(/<br>|=|\n|(&nbsp;)| /);
  for (let i = textSplit.length - 1; i >= 0; i--) {
     const part = textSplit[i];
     if (!part) continue;
     const clean = part.replace(/<\/?[^>]+(>|$)/g, "").replace(/\$/g, "").trim();
     if (/^-?\d+(\.\d+)?$/.test(clean)) {
       return clean;
     }
  }
  return null;
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
    const extAns = extractIntegerAnswer(question);
    if (!extAns) {
      return { marks: 0, verdict: 'incorrect' }
    }
    const correct = parseInt(extAns)
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
