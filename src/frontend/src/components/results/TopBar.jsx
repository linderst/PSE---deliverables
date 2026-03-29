import React from 'react';

const TopBar = ({ handleReset, searchTerm, setSearchTerm, handleSearch }) => {
  return (
    <div className="results-topbar">
      <div
        className="brand-logo"
        onClick={handleReset}
        style={{ cursor: 'pointer', marginRight: '20px', display: 'flex', flexDirection: 'column' }}
        title="Zurück zum Start"
      >
        <h1 style={{ fontSize: '22px', margin: 0, fontWeight: 800, letterSpacing: '-0.5px', color: 'var(--accent)', lineHeight: 1 }}>
          medcode.ch
        </h1>
        <span style={{ fontSize: '11px', color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.3px', marginTop: '2px' }}>
          DIAGNOSEN
        </span>
      </div>
      <div className="search-wrap no-animate">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Neue Suche..."
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(searchTerm)}
        />
        <button className="search-btn" onClick={() => handleSearch(searchTerm)}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default TopBar;
