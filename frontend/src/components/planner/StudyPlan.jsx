import { useState, useEffect, useCallback } from "react";
import SessionCard from "./SessionCard";
import "./planner.css";

/** Format "2026-03-24" → "Monday, Mar 24" */
function formatDate(isoDate) {
  const d = new Date(isoDate + "T00:00:00");
  return d.toLocaleDateString("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}

/** Group flat sessions array into { date: [session, ...] } map */
function groupByDate(sessions) {
  return sessions.reduce((acc, s) => {
    const key = s.date;
    if (!acc[key]) acc[key] = [];
    acc[key].push(s);
    return acc;
  }, {});
}

export default function StudyPlan({ profileId, profile }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/planner/plan/${profileId}`);
      if (!res.ok) throw new Error("Failed to load sessions.");
      const data = await res.json();
      setSessions(data.sessions ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [profileId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleMark = async (sessionId, status) => {
    try {
      await fetch(`/planner/session/${sessionId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });

      if (status === "missed") {
        await fetch(`/planner/rebalance/${profileId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(profile),
        });
      }
    } catch {
      // silently fail — reload will show truth
    } finally {
      fetchSessions();
    }
  };

  const handleRebalance = async () => {
    setLoading(true);
    try {
      await fetch(`/planner/rebalance/${profileId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
    } catch {
      /* noop */
    } finally {
      fetchSessions();
    }
  };

  // Progress calculation
  const total = sessions.length;
  const done = sessions.filter((s) => s.status === "done").length;
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;

  const grouped = groupByDate(sessions);
  const sortedDates = Object.keys(grouped).sort();

  return (
    <div className="planner-module">
      {/* Top bar */}
      <div className="sp-topbar">
        <h2 className="sp-heading">Your 7-Day JEE Plan</h2>
        <div className="sp-progress-wrap">
          <p className="sp-progress-label">
            {done} of {total} sessions complete
          </p>
          <div className="sp-progress-track" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
            <div className="sp-progress-fill" style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>

      {/* Error */}
      {error && <p className="sp-error">{error}</p>}

      {/* Loading */}
      {loading && (
        <div className="sp-loading">
          <span className="btn-spinner btn-spinner--dark" />
          Loading your plan…
        </div>
      )}

      {/* Grouped session days */}
      {!loading && !error && (
        <div className="sp-days">
          {sortedDates.length === 0 && (
            <p className="sp-empty">No sessions found. Try rebalancing.</p>
          )}

          {sortedDates.map((date) => (
            <div key={date} className="sp-day-section">
              <h3 className="sp-date-heading">{formatDate(date)}</h3>
              <div className="sp-cards-row">
                {grouped[date].map((session) => (
                  <SessionCard
                    key={session._id}
                    session={session}
                    onMark={handleMark}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Floating rebalance button */}
      <button
        id="sp-rebalance-btn"
        className="sp-fab"
        onClick={handleRebalance}
        disabled={loading}
        title="Rebalance Plan"
      >
        ↻ Rebalance Plan
      </button>
    </div>
  );
}
