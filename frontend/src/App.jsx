import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Onboarding from "./components/planner/Onboarding";
import StudyPlan from "./components/planner/StudyPlan";

import RetentionDashboard from "./components/retention/RetentionDashboard";
import MockTestApp from "./components/mocktest/MockTestApp";
import Dashboard from "./components/dashboard/Dashboard";
import AuthPage from "./components/auth/AuthPage";

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
  const [isLoggedIn, setIsLoggedIn] = useState(() => localStorage.getItem('isLoggedIn') === 'true');
  const [profileId, setProfileId] = useState(() => localStorage.getItem('profileId') || null);
  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem('profile');
    try { return saved ? JSON.parse(saved) : null; } catch { return null; }
  });

  const handleLogin = (name) => {
    setIsLoggedIn(true);
  };

  if (!isLoggedIn) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AuthPage onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
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
        <Route path="/mocktest" element={<MockTestApp />} />
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
