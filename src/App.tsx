import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import TextInput from './components/TextInput';
import Dashboard from './components/Dashboard';
import Reports from './components/Reports';

export interface AnalysisResult {
  originalText: string;
  cleanedText: string;
  sentiment: {
    score: number;
    label: string;
    positive: number;
    negative: number;
    neutral: number;
  };
  topics: Array<{ word: string; weight: number }>;
  summary: string;
  wordCount: number;
  sentenceCount: number;
  keywords: Array<{ text: string; value: number }>;
}

function App() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>NarrativeNexus</h1>
          <p>Dynamic Text Analysis Platform</p>
        </header>
        
        <nav className="app-nav">
          <Link to="/">Text Analysis</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/reports">Reports</Link>
        </nav>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<TextInput onAnalysisComplete={setAnalysisResult} />} />
            <Route path="/dashboard" element={<Dashboard analysisResult={analysisResult} />} />
            <Route path="/reports" element={<Reports analysisResult={analysisResult} />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>© 2025 NarrativeNexus | Advanced Text Analysis Technology</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
