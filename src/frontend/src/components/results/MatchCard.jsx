/**
 * @module MatchCard
 * @description Displays the primary diagnosis result as a prominent card.
 * Shows the ICD-10 code badge, diagnosis title, catalog version, and a
 * circular SVG confidence tachometer (0-100%). During loading, renders an
 * animated spinner with contextual messages. Displays a "KI-verfeinert"
 * badge when results were improved by Gemini AI refinement.
 *
 * @component
 * @param {Object} props
 * @param {boolean}     props.searchLoading    - Whether a search is currently in progress
 * @param {Object|null} props.currentCondition - The primary result {code, title, version, score}
 * @param {string|null} props.searchError      - Error message if search failed
 * @param {boolean}     props.longLoading      - True when search exceeds 2.5s (Gemini fallback active)
 * @param {boolean}     props.searchRefined    - True when results were improved by AI refinement
 */
import React from 'react';
import LoadingDots from '../ui/LoadingDots';

const MatchCard = ({
  searchLoading,
  currentCondition,
  searchError,
  longLoading,
  searchRefined,
  searchRefining
}) => {
  return (
    <div className="match-card">
      <div className="match-content">
        <div className="match-code">
          {searchLoading ? <LoadingDots /> : currentCondition ? currentCondition.code : '?'}
        </div>
        <div className="match-info">
          <div className="match-title" style={{ display: 'flex', alignItems: 'center' }}>
            {searchLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '3px' }}></div>
                <span>
                  {searchRefining ? 'KI-Diagnose läuft' : 'Suche läuft'}
                  <LoadingDots />
                </span>
              </div>
            ) : (
              currentCondition ? currentCondition.title : searchError
            )}
          </div>
          {searchLoading && longLoading && (
            <div style={{ fontSize: '13px', color: 'var(--muted)', marginTop: '8px', animation: 'slide-up-fade 0.5s ease-out forwards', pointerEvents: 'none' }}>
              Detaillierte Analyse deines komplexeren Symptoms...
            </div>
          )}
          <div className="match-meta">
            {currentCondition && `ICD-10`}
          </div>
          {searchRefined && (
            <div className="refined-badge">✦ KI-verfeinert</div>
          )}
        </div>
      </div>
      
      {/* Tachometer */}
      {currentCondition && !searchLoading && currentCondition.score != null && (
        <div className="tachometer">
          <svg viewBox="0 0 36 36" className="circular-chart">
            <path
              className="circle-bg"
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className="circle"
              strokeDasharray={`${Math.round(currentCondition.score * 100)}, 100`}
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <text x="18" y="20.35" className="percentage">
              {Math.round(currentCondition.score * 100)}%
            </text>
          </svg>
          <div className="tacho-label">Treffer</div>
        </div>
      )}
    </div>
  );
};

export default MatchCard;
