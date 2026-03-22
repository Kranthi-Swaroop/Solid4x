import React, { useState, useEffect, useRef, useCallback } from 'react'
import rawData from '../../data/mocktest_questions.json'
import TestInterface from './TestInterface'
import ResultDashboard from './ResultDashboard'
import { TimeTracker } from './utils/timeTracker'
import './mocktest.css'

const SUBJECTS = ['Physics', 'Chemistry', 'Mathematics']
const TOTAL_TIME = 3 * 60 * 60   // 3 hours in seconds

export default function MockTestApp() {
  const [allQuestions, setAllQuestions] = useState([])
  const [questionsBySubject, setQuestionsBySubject] = useState({})
  const [answers, setAnswers] = useState({})
  const [markedForReview, setMarkedForReview] = useState({})
  const [visited, setVisited] = useState({})
  const [timeLeft, setTimeLeft] = useState(TOTAL_TIME)
  const [submitted, setSubmitted] = useState(false)
  const trackerRef = useRef(new TimeTracker())

  useEffect(() => {
    let globalIndex = 0
    const flatArr = []
    const grouped = {}
    
    if (rawData.questions_by_subject) {
      SUBJECTS.forEach(sub => {
        const qList = rawData.questions_by_subject[sub] || []
        const mcqs = qList.filter(q => q.type === 'mcq').slice(0, 20)
        const ints = qList.filter(q => q.type === 'integer').slice(0, 5)
        const combined = [...mcqs, ...ints].map(q => {
          globalIndex++
          return { ...q, subject: sub, global_index: globalIndex }
        })
        grouped[sub] = combined
        flatArr.push(...combined)
      })
    }
    setAllQuestions(flatArr)
    setQuestionsBySubject(grouped)
  }, [])

  useEffect(() => {
    if (submitted) return
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer)
          handleSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, [submitted])

  const handleAnswer = useCallback((question_id, value) => {
    setAnswers(prev => ({ ...prev, [question_id]: value }))
    setVisited(prev => ({ ...prev, [question_id]: true }))
  }, [])

  const handleMarkForReview = useCallback((question_id) => {
    setMarkedForReview(prev => ({ ...prev, [question_id]: !prev[question_id] }))
  }, [])

  const handleNavigate = useCallback((question_id) => {
    trackerRef.current.startQuestion(question_id)
    setVisited(prev => ({ ...prev, [question_id]: true }))
  }, [])

  const handleSubmit = useCallback(() => {
    trackerRef.current.stopCurrent()
    setSubmitted(true)
  }, [])

  if (allQuestions.length === 0) return <div>Loading questions...</div>

  if (!submitted) {
    return (
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
      />
    )
  }

  return (
    <ResultDashboard
      allQuestions={allQuestions}
      answers={answers}
      times={trackerRef.current.getAllTimes()}
      questionsBySubject={questionsBySubject}
    />
  )
}
