import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Onboarding from "./components/planner/Onboarding";
import StudyPlan from "./components/planner/StudyPlan";

import RetentionDashboard from "./components/retention/RetentionDashboard";
import MockTestApp from "./components/mocktest/MockTestApp";
import Dashboard from "./components/dashboard/Dashboard";
import AuthPage from "./components/auth/AuthPage";
import Syllabus from "./components/syllabus/Syllabus";

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => localStorage.getItem('isLoggedIn') === 'true');
  const [needsOnboarding, setNeedsOnboarding] = useState(() => localStorage.getItem('onboarding_completed') !== 'true');
  const [profileId, setProfileId] = useState(() => localStorage.getItem('profileId') || null);
  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem('profile');
    try { return saved ? JSON.parse(saved) : null; } catch { return null; }
  });

  const handleLogin = (name) => {
    setIsLoggedIn(true);
    // Check if onboarding was completed
    checkOnboarding();
  };

  const checkOnboarding = async () => {
    const userId = localStorage.getItem('profileId');
    if (!userId) { setNeedsOnboarding(true); return; }
    try {
      const res = await fetch(`/planner/onboarding-status/${userId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.onboarding_completed) {
          setNeedsOnboarding(false);
          localStorage.setItem('onboarding_completed', 'true');
        } else {
          setNeedsOnboarding(true);
        }
      }
    } catch {
      // If backend is down, skip onboarding check
      setNeedsOnboarding(false);
    }
  };

  const handleOnboardingComplete = (id, p) => {
    setProfileId(id || localStorage.getItem('profileId'));
    setProfile(p);
    localStorage.setItem('profileId', id || localStorage.getItem('profileId'));
    localStorage.setItem('profile', JSON.stringify(p));
    localStorage.setItem('onboarding_completed', 'true');
    setNeedsOnboarding(false);
  };

  // Not logged in → auth page
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
          path="/onboarding"
          element={
            <Onboarding
              onComplete={handleOnboardingComplete}
            />
          }
        />
        <Route
          path="/planner"
          element={
            profileId
              ? <StudyPlan profileId={profileId} profile={profile} />
              : <Navigate to="/onboarding" replace />
          }
        />
        <Route
          path="/retention"
          element={<RetentionDashboard profileId={profileId || localStorage.getItem('profileId')} />}
        />
        <Route path="/mocktest" element={<MockTestApp />} />
        <Route path="/syllabus" element={<Syllabus />} />
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
