import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Layout Components
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';

// Page Components
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import ROI from './pages/ROI';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow bg-gray-50">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/roi" element={<ROI />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
