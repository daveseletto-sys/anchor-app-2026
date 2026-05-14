import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./lib/auth";
import { Toaster } from "./components/ui/sonner";

import Landing from "./pages/Landing";
import AppShell from "./components/AppShell";
import Dashboard from "./pages/Dashboard";
import Diary from "./pages/Diary";
import DietTracker from "./pages/DietTracker";
import FoodLabelReader from "./pages/FoodLabelReader";
import BloodTests from "./pages/BloodTests";
import Goals from "./pages/Goals";
import Glossary from "./pages/Glossary";
import Profile from "./pages/Profile";
import Medications from "./pages/Medications";
import Crisis from "./pages/Crisis";
import Reports from "./pages/Reports";
import ShareLinks from "./pages/ShareLinks";
import SharedView from "./pages/SharedView";
import Milestones from "./pages/Milestones";
import Privacy from "./pages/Privacy";
import Support from "./pages/Support";

const Private = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="p-10 text-muted-foreground">Loading…</div>;
    if (!user) return <Navigate to="/" replace />;
    return children;
};

const Public = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="p-10 text-muted-foreground">Loading…</div>;
    if (user) return <Navigate to="/app" replace />;
    return children;
};

function App() {
    return (
        <div className="App">
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<Public><Landing /></Public>} />
                        <Route path="/share/:token" element={<SharedView />} />
                        <Route path="/privacy" element={<Privacy />} />
                        <Route path="/support" element={<Support />} />
                        <Route path="/app" element={<Private><AppShell /></Private>}>
                            <Route index element={<Dashboard />} />
                            <Route path="diary" element={<Diary />} />
                            <Route path="diet" element={<DietTracker />} />
                            <Route path="food-label" element={<FoodLabelReader />} />
                            <Route path="blood" element={<BloodTests />} />
                            <Route path="goals" element={<Goals />} />
                            <Route path="meds" element={<Medications />} />
                            <Route path="reports" element={<Reports />} />
                            <Route path="share" element={<ShareLinks />} />
                            <Route path="milestones" element={<Milestones />} />
                            <Route path="glossary" element={<Glossary />} />
                            <Route path="crisis" element={<Crisis />} />
                            <Route path="profile" element={<Profile />} />
                        </Route>
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </BrowserRouter>
                <Toaster position="top-center" richColors />
            </AuthProvider>
        </div>
    );
}

export default App;
