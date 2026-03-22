export class TimeTracker {
  constructor() {
    this.times = {}          // { question_id: totalSeconds }
    this.current = null      // { id, startedAt }
  }
  
  startQuestion(id) {
    this.stopCurrent()
    this.current = { id, startedAt: Date.now() }
    if (!this.times[id]) this.times[id] = 0
  }
  
  stopCurrent() {
    if (!this.current) return
    const elapsed = Math.floor((Date.now() - this.current.startedAt) / 1000)
    this.times[this.current.id] = (this.times[this.current.id] || 0) + elapsed
    this.current = null
  }
  
  getTime(id) { return this.times[id] || 0 }
  
  getAllTimes() {
    this.stopCurrent()
    return { ...this.times }
  }
  
  formatTime(seconds) {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}m ${s.toString().padStart(2,'0')}s`
  }
}
