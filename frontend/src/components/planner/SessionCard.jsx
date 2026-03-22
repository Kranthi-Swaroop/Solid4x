import "./planner.css";

const PRIORITY_COLORS = {
  high: "#e74c3c",
  medium: "#f39c12",
  low: "#27ae60",
};

const SUBJECT_CLASSES = {
  Physics: "pill-physics",
  Chemistry: "pill-chemistry",
  Mathematics: "pill-maths",
};

const STATUS_BORDER = {
  done: "#27ae60",
  missed: "#e74c3c",
};

export default function SessionCard({ session, onMark }) {
  const {
    _id,
    topic = "",
    subject = "",
    duration_mins = 0,
    priority = "medium",
    reason = "",
    status = "pending",
  } = session;

  const isDone = status === "done";
  const isMissed = status === "missed";
  const isSettled = isDone || isMissed;

  const borderColor = STATUS_BORDER[status] ?? PRIORITY_COLORS[priority] ?? "#ccc";
  const priorityColor = PRIORITY_COLORS[priority] ?? "#999";

  return (
    <div
      className="sc-card"
      style={{ borderLeftColor: borderColor }}
      aria-label={`${subject}: ${topic}`}
    >
      {/* Priority badge */}
      <span
        className="sc-priority-badge"
        style={{ background: priorityColor }}
      >
        {priority}
      </span>

      {/* Topic */}
      <p className="sc-topic">{topic}</p>

      {/* Subject pill */}
      <span className={`sc-pill ${SUBJECT_CLASSES[subject] ?? ""}`}>
        {subject}
      </span>

      {/* Duration */}
      <p className="sc-duration">
        <svg
          className="sc-clock-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        {duration_mins} min
      </p>

      {/* Reason */}
      <p className="sc-reason">{reason}</p>

      {/* Action buttons — hidden when settled */}
      {!isSettled && (
        <div className="sc-actions">
          <button
            id={`sc-done-${_id}`}
            className="sc-btn sc-btn-done"
            onClick={() => onMark(_id, "done")}
          >
            ✓ Done
          </button>
          <button
            id={`sc-missed-${_id}`}
            className="sc-btn sc-btn-missed"
            onClick={() => onMark(_id, "missed")}
          >
            ✗ Missed
          </button>
        </div>
      )}
    </div>
  );
}
