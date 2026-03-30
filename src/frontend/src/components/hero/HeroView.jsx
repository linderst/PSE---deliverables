/**
 * @module HeroView
 * @description Landing page ("hero") of the Medcode application.
 * Displays the main search input and an alphabetical index of cached
 * diagnoses. Acts as the entry point before any search is performed.
 *
 * @component
 * @param {Object} props
 * @param {string}   props.searchTerm            - Current value of the search input
 * @param {Function} props.setSearchTerm         - Setter for the search input value
 * @param {Function} props.handleSearch          - Triggers a diagnosis search
 * @param {Array}    props.cachedConditions       - Pre-loaded diagnoses for the A-Z index
 * @param {string}   props.activeLetter          - Currently selected letter in the alphabet nav
 * @param {Function} props.setActiveLetter       - Setter for the active letter filter
 * @param {Function} props.handleSelectCondition - Callback when a cached condition is clicked
 */
import React from 'react';
import AlphabetIndex from './AlphabetIndex';

const HeroView = ({
  searchTerm,
  setSearchTerm,
  handleSearch,
  cachedConditions,
  activeLetter,
  setActiveLetter,
  handleSelectCondition
}) => {
  return (
    <div className="hero">
      <div className="hero-badge">ICD-10 Diagnosensuche</div>
      <div>
        <div className="hero-title">Was steht in Ihrem Arztbrief?</div>
        <div className="hero-sub" style={{ marginTop: '12px' }}>
          Geben Sie einen medizinischen Begriff, eine Diagnose oder einen ICD-10-Code ein — wir erklären ihn verständlich.
        </div>
      </div>
      <div className="search-wrap">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Medizinischen Begriff oder Code eingeben..."
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(searchTerm)}
          autoFocus
        />
        <button className="search-btn" onClick={() => handleSearch(searchTerm)}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </button>
      </div>

      <AlphabetIndex
        cachedConditions={cachedConditions}
        activeLetter={activeLetter}
        setActiveLetter={setActiveLetter}
        handleSelectCondition={handleSelectCondition}
      />
    </div>
  );
};

export default HeroView;
