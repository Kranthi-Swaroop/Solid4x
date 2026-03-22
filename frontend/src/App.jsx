import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Onboarding from "./components/planner/Onboarding";
import StudyPlan from "./components/planner/StudyPlan";

function PlannerPage() {
  const [profileId, setProfileId] = useState(null);
  const [profile, setProfile] = useState(null);

  if (!profileId) {
    return (
      <Onboarding
        onComplete={(id, p) => {
          setProfileId(id);
          setProfile(p);
        }}
      />
    );
  }

  return <StudyPlan profileId={profileId} profile={profile} />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/planner" element={<PlannerPage />} />
        {/* Redirect root to /planner for now */}
        <Route path="/" element={<Navigate to="/planner" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
