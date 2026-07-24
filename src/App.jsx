import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import CommandCenter from './pages/CommandCenter';
import AlertCenter from './pages/AlertCenter';
import AccountIntel from './pages/AccountIntel';
import AnomalyLab from './pages/AnomalyLab';
import ExplainableAI from './pages/ExplainableAI';
import RiskEngine from './pages/RiskEngine';
import PatternDiscovery from './pages/PatternDiscovery';
import Copilot from './pages/Copilot';
import ModelIntel from './pages/ModelIntel';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<Landing />} />

        {/* Command Center Dashboard */}
        <Route path="/command-center" element={<CommandCenter />} />

        {/* Alert Queue and Review Center */}
        <Route path="/alert-center" element={<AlertCenter />} />

        {/* Detailed Account Telemetry */}
        <Route path="/account-intel" element={<AccountIntel />} />

        {/* Unsupervised Anomaly Lab */}
        <Route path="/anomaly-lab" element={<AnomalyLab />} />

        {/* Explainable AI Dashboard */}
        <Route path="/explainable-ai" element={<ExplainableAI />} />

        {/* Predictive Risk Engine forecast */}
        <Route path="/risk-engine" element={<RiskEngine />} />

        {/* Coordinated Ring Discovery */}
        <Route path="/pattern-discovery" element={<PatternDiscovery />} />

        {/* FIU Forensic Copilot chatbot */}
        <Route path="/copilot" element={<Copilot />} />

        {/* Model evaluation reports */}
        <Route path="/model-intel" element={<ModelIntel />} />
      </Routes>
    </BrowserRouter>
  );
}
