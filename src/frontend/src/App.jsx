/**
 * @module App
 * @description Root route configuration for the Medcode SPA.
 *              Delegates all rendering and logic to page-level components.
 */
import React from 'react';
import { Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import Results from './pages/Results';

function App() {
  return (
    <div className="layout">
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Results />} />
          <Route path="/:slug/:code" element={<Results />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
