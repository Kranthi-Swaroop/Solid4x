import "./retention.css";

export default function ConceptCard({ card, onClick }) {
  const getSubjectColor = (subject) => {
    switch (subject) {
      case "Physics": return "#3498db";
      case "Chemistry": return "#9b59b6";
      case "Mathematics": return "#e67e22";
      default: return "#6b7280";
    }
  };

  const getMasteryColor = (score) => {
    if (score <= 40) return "#e74c3c"; // red
    if (score <= 74) return "#e67e22"; // orange
    return "#27ae60"; // green
  };

  return (
    <div className="ret-concept-card-list" onClick={onClick}>
      <div className="ret-concept-header">
        <span 
          className="ret-subject-pill" 
          style={{ backgroundColor: getSubjectColor(card.subject) }}
        >
          {card.subject}
        </span>
        <span className="ret-topic-name">{card.topic}</span>
      </div>

      <div className="ret-mastery-container">
        <div className="ret-mastery-bar">
          <div 
            className="ret-mastery-fill" 
            style={{ 
              width: `${Math.max(0, Math.min(100, card.mastery_score || 0))}%`, 
              backgroundColor: getMasteryColor(card.mastery_score) 
            }}
          />
        </div>
      </div>

      <div className="ret-concept-footer">
        <span className="ret-next-review">Next: {new Date(card.next_review_date).toLocaleDateString()}</span>
        <span className="ret-interval-badge">Review in {card.interval} days</span>
      </div>
    </div>
  );
}
