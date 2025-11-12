 import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navigation from './components/Navigation/Navigation';
import Home from './pages/Home/Home';
import Analysis from './pages/Analysis/Analysis';
import History from './pages/History/History';
import './App.css';

function App() {
  return (
    <Box className="App">
      <Navigation />
      <Box component="main" className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;