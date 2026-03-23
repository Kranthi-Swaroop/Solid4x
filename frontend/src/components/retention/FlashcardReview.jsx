import { useState } from "react";
import "./retention.css";

export default function FlashcardReview({ card, onReviewed }) {
  const [revealed, setRevealed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRate = async (quality) => {
    setLoading(true);
    try {
      const res = await fetch("https://8251-2a09-bac1-36e0-1468-00-ca-6e.ngrok-free.app/api/v1/retention/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ card_id: card._id, quality })
      });
      const data = await res.json();
      if (res.ok) {
        setRevealed(false);
        onReviewed(data.updated_card);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ret-flashcard-container">
      <div className={`ret-flashcard ${revealed ? "revealed" : ""}`}>
        <div className="ret-flashcard-inner">
          <div className="ret-flashcard-front">
            <span className="ret-fc-subject">{card.subject}</span>
            <h2 className="ret-fc-topic">{card.topic}</h2>
            <p className="ret-fc-hint">How well do you recall this?</p>
            <button className="ret-btn-reveal" onClick={() => setRevealed(true)}>
              Reveal Answer &rarr;
            </button>
          </div>

          <div className="ret-flashcard-back">
            <span className="ret-fc-subject">{card.subject}</span>
            <h2 className="ret-fc-topic">{card.topic}</h2>
            <h3 className="ret-fc-rate-header">Rate your recall:</h3>

            <div className="ret-rating-row">
              <button disabled={loading} className="rate-btn" style={{ backgroundColor: "#c0392b" }} onClick={() => handleRate(0)}>
                0<br /><span>Blackout</span>
              </button>
              <button disabled={loading} className="rate-btn" style={{ backgroundColor: "#e74c3c" }} onClick={() => handleRate(1)}>
                1<br /><span>Wrong</span>
              </button>
              <button disabled={loading} className="rate-btn" style={{ backgroundColor: "#e67e22" }} onClick={() => handleRate(2)}>
                2<br /><span>Hard</span>
              </button>
              <button disabled={loading} className="rate-btn" style={{ backgroundColor: "#f1c40f" }} onClick={() => handleRate(3)}>
                3<br /><span>Ok</span>
              </button>
              <button disabled={loading} className="rate-btn" style={{ backgroundColor: "#2ecc71" }} onClick={() => handleRate(4)}>
                4<br /><span>Good</span>
              </button>
              <button disabled={loading} className="rate-btn" style={{ backgroundColor: "#27ae60" }} onClick={() => handleRate(5)}>
                5<br /><span>Perfect</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
