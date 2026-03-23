import { useState } from "react";
import "./planner.css";

const WEAK_TOPICS = {
  Physics: [
    "Mechanics",
    "Thermodynamics",
    "Electrostatics",
    "Optics",
    "Modern Physics",
    "Waves",
    "Magnetism",
  ],
  Chemistry: [
    "Mole Concept",
    "Electrochemistry",
    "Organic Reactions",
    "Equilibrium",
    "Coordination Chemistry",
    "Thermochemistry",
    "Chemical Bonding",
  ],
  Mathematics: [
    "Calculus",
    "Algebra",
    "Coordinate Geometry",
    "Trigonometry",
    "Vectors",
    "Probability",
    "Matrices",
  ],
};

export default function Onboarding({ onComplete }) {
  const storedName = localStorage.getItem('studentName') || '';
  const userId = localStorage.getItem('profileId') || '';

  const [name, setName] = useState(storedName);
  const [examDate, setExamDate] = useState("");
  const [dailyHours, setDailyHours] = useState(6);
  const [weakAreas, setWeakAreas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggleWeak = (topic) => {
    setWeakAreas((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) return setError("Please enter your full name.");
    if (!examDate) return setError("Please select your exam date.");

    setLoading(true);
    try {
      const res = await fetch("https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/planner/onboard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          name: name.trim(),
          exam_date: examDate,
          daily_hours: dailyHours,
          weak_areas: weakAreas,
          target_exam: localStorage.getItem('targetExam') || 'JEE Advanced',
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Server error. Please try again.");
      }

      const data = await res.json();
      onComplete(data.profile_id || userId, {
        name: name.trim(),
        exam_date: examDate,
        daily_hours: dailyHours,
        weak_areas: weakAreas,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="planner-module">
      <div className="onb-card">
        <h1 className="onb-heading">Set up your JEE Study Plan</h1>

        <form onSubmit={handleSubmit} noValidate>
          {/* Name */}
          <div className="onb-field">
            <label className="onb-label" htmlFor="onb-name">
              Full name
            </label>
            <input
              id="onb-name"
              className="onb-input"
              type="text"
              placeholder="e.g. Arjun Sharma"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {/* Exam date */}
          <div className="onb-field">
            <label className="onb-label" htmlFor="onb-date">
              JEE exam date
            </label>
            <input
              id="onb-date"
              className="onb-input"
              type="date"
              value={examDate}
              onChange={(e) => setExamDate(e.target.value)}
            />
          </div>

          {/* Daily hours slider */}
          <div className="onb-field">
            <label className="onb-label" htmlFor="onb-hours">
              Daily study hours —{" "}
              <span className="onb-hours-val">{dailyHours} hrs/day</span>
            </label>
            <input
              id="onb-hours"
              className="onb-slider"
              type="range"
              min={1}
              max={12}
              step={1}
              value={dailyHours}
              onChange={(e) => setDailyHours(Number(e.target.value))}
            />
          </div>

          {/* Weak topics */}
          <div className="onb-field">
            <p className="onb-label">Weak topics (select all that apply)</p>
            <div className="onb-subjects">
              {Object.entries(WEAK_TOPICS).map(([subject, topics]) => (
                <div key={subject} className="onb-subject-col">
                  <p className="onb-subject-heading">{subject}</p>
                  <div className="onb-checkbox-grid">
                    {topics.map((topic) => (
                      <label key={topic} className="onb-checkbox-label">
                        <input
                          type="checkbox"
                          checked={weakAreas.includes(topic)}
                          onChange={() => toggleWeak(topic)}
                        />
                        <span>{topic}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {error && <p className="onb-error">{error}</p>}

          <button
            id="onb-submit-btn"
            className="onb-submit-btn"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="btn-spinner" />
                Generating…
              </>
            ) : (
              "Generate My Plan →"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
