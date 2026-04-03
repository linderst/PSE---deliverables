/**
 * @module Home
 * @description Landing page route container. Manages the hero search state
 *              and navigates to the Results page on search submission.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { slugify } from '../utils/helpers';
import HeroView from '../components/hero/HeroView';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const Home = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [activeLetter, setActiveLetter] = useState('A');
  const [cachedConditions, setCachedConditions] = useState([]);

  // Fetch cached conditions for the A-Z index on mount
  useEffect(() => {
    fetch(`${API}/cached-conditions`)
      .then(r => r.json())
      .then(data => {
        if (data.conditions) setCachedConditions(data.conditions);
      })
      .catch(e => console.error('Error fetching cached conditions:', e));
  }, []);

  /**
   * Navigates to the Results page with the search term as the query param.
   * @param {string} term - Free text or ICD-10 code
   */
  const handleSearch = (term) => {
    const q = (term || '').trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  /**
   * Navigates directly to the results page for a known condition (from A-Z index).
   * @param {string} code  - ICD-10 code
   * @param {string} title - Diagnosis title
   */
  const handleSelectCondition = (code, title) => {
    navigate(`/${slugify(title)}/${code}`);
  };

  return (
    <HeroView
      searchTerm={searchTerm}
      setSearchTerm={setSearchTerm}
      handleSearch={handleSearch}
      cachedConditions={cachedConditions}
      activeLetter={activeLetter}
      setActiveLetter={setActiveLetter}
      handleSelectCondition={handleSelectCondition}
    />
  );
};

export default Home;
