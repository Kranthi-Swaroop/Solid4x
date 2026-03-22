import { useState, useEffect } from "react";
import FlashcardReview from "./FlashcardReview";
import ConceptCard from "./ConceptCard";
import TopicPicker from "./TopicPicker";
import "./retention.css";

export default function RetentionDashboard({ profileId }) {
  const [dueCards, setDueCards] = useState([]);
  const [graph, setGraph] = useState({});
  const [activeReviewIndex, setActiveReviewIndex] = useState(-1);
  const [activeReviewCard, setActiveReviewCard] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const [dueRes, graphRes] = await Promise.all([
        fetch(`/retention/due/${profileId}`),
        fetch(`/retention/graph/${profileId}`)
      ]);
      if (dueRes.ok) {
        const d = await dueRes.json();
        setDueCards(Array.isArray(d) ? d : (d.due_concepts || []));
      }
      if (graphRes.ok) {
        setGraph(await graphRes.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (profileId) fetchDashboardData();
  }, [profileId]);

  const handleReviewed = (updatedCard) => {
    if (activeReviewCard) {
      setActiveReviewCard(null);
      fetchDashboardData();
    } else if (activeReviewIndex < dueCards.length - 1) {
      setActiveReviewIndex(prev => prev + 1);
    } else {
      setActiveReviewIndex(-1);
      fetchDashboardData();
    }
  };

  const startReview = () => {
    if (dueCards.length > 0) setActiveReviewIndex(0);
  };

  const reviewCardToPass = activeReviewCard || (activeReviewIndex >= 0 ? dueCards[activeReviewIndex] : null);

  if (reviewCardToPass) {
    return (
      <div className="retention-module">
        <FlashcardReview 
          card={reviewCardToPass} 
          onReviewed={handleReviewed} 
        />
        {!activeReviewCard && (
          <div className="ret-review-count">
            Card {activeReviewIndex + 1} of {dueCards.length}
          </div>
        )}
      </div>
    );
  }

  // Render Columns
  const renderColumn = (subjectName) => {
    const data = graph[subjectName] || { total: 0, mastered: 0, due: 0, topics: [] };
    const sortedTopics = [...data.topics].sort((a, b) => a.mastery_score - b.mastery_score);
    
    return (
      <div className="ret-subject-col" key={subjectName}>
        <div className="ret-col-header">
          <h3>{subjectName}</h3>
          <span className="ret-col-stats">{data.mastered} / {data.total} Mastered</span>
        </div>
        
        <div className="ret-mastery-bar">
          <div className="ret-mastery-fill" 
               style={{ 
                 width: `${data.total ? (data.mastered / data.total) * 100 : 0}%`,
                 backgroundColor: '#3498db'
               }} 
          />
        </div>

        <div className="ret-col-cards">
          {sortedTopics.map((topicNode, idx) => (
            <ConceptCard 
              key={idx} 
              card={{ ...topicNode, subject: subjectName }} 
              onClick={() => setActiveReviewCard({ ...topicNode, subject: subjectName })} 
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="retention-module">
      {dueCards.length > 0 && (
        <div className="ret-due-banner">
          <div className="ret-due-info">
            <strong>{dueCards.length} concepts due for review today</strong>
            <p>Keep your SM-2 streaks alive to master these topics!</p>
          </div>
          <button className="ret-btn-start" onClick={startReview}>
            Start Review Session &rarr;
          </button>
        </div>
      )}

      <div className="ret-graph-section">
        <div className="ret-graph-header">
          <h2>Knowledge Graph</h2>
          <button className="ret-btn-add" onClick={() => setShowAddForm(!showAddForm)}>
            {showAddForm ? "Cancel" : "+ Add Topics"}
          </button>
        </div>

        {showAddForm && (
          <TopicPicker 
            profileId={profileId} 
            onAdded={() => {
              setShowAddForm(false);
              fetchDashboardData();
            }} 
          />
        )}

        <div className="ret-graph-grid">
          {renderColumn("Physics")}
          {renderColumn("Chemistry")}
          {renderColumn("Mathematics")}
        </div>
      </div>
    </div>
  );
}
