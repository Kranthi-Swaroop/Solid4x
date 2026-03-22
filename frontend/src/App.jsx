import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import Onboarding from "./components/planner/Onboarding";
import StudyPlan from "./components/planner/StudyPlan";

import RetentionDashboard from "./components/retention/RetentionDashboard";

function PlannerPage({ profileId, setProfileId, profile, setProfile }) {
  if (!profileId) {
    return (
      <Onboarding
        onComplete={(id, p) => {
          setProfileId(id);
          setProfile(p);
          localStorage.setItem('profileId', id);
          localStorage.setItem('profile', JSON.stringify(p));
        }}
      />
    );
  }

  return <StudyPlan profileId={profileId} profile={profile} />;
}

export default function App() {
  const [profileId, setProfileId] = useState(() => localStorage.getItem('profileId') || null);
  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem('profile');
    try { return saved ? JSON.parse(saved) : null; } catch { return null; }
  });

  return (
    <BrowserRouter>
      <div style={{ padding: '10px', background: '#f3f4f6', display: 'flex', gap: '15px' }}>
        <Link to="/planner" id="nav-planner" style={{fontWeight: 'bold'}}>Study Planner</Link>
        <Link to="/retention" id="nav-retention" style={{fontWeight: 'bold'}}>Spaced Repetition</Link>
      </div>
      <Routes>
        <Route 
          path="/planner" 
          element={<PlannerPage profileId={profileId} setProfileId={setProfileId} profile={profile} setProfile={setProfile} />} 
        />
        <Route 
          path="/retention" 
          element={
            profileId ? <RetentionDashboard profileId={profileId} /> : <Navigate to="/planner" replace />
          } 
        />
        {/* Redirect root to /planner for now */}
        <Route path="/" element={<Navigate to="/planner" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
