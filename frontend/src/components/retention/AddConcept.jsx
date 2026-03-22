import { useState } from "react";
import "./retention.css";

export default function AddConcept({ profileId, onAdded }) {
  const [topic, setTopic] = useState("");
  const [subject, setSubject] = useState("Physics");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic) return;
    setLoading(true);

    try {
      await fetch("/retention/card", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_id: profileId,
          topic,
          subject,
          source: "manual"
        })
      });
      onAdded();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="ret-add-form inline-form" onSubmit={handleSubmit}>
      <input 
        type="text" 
        placeholder="Topic name (e.g. Kinematics)" 
        value={topic} 
        onChange={e => setTopic(e.target.value)} 
        required
      />
      <select value={subject} onChange={e => setSubject(e.target.value)}>
        <option value="Physics">Physics</option>
        <option value="Chemistry">Chemistry</option>
        <option value="Mathematics">Mathematics</option>
      </select>
      <button type="submit" disabled={loading}>
        {loading ? "Adding..." : "Add to revision list"}
      </button>
    </form>
  );
}
