import React from 'react';
import LoadingDots from '../ui/LoadingDots';

const MatchCard = ({
  searchLoading,
  currentCondition,
  searchError,
  longLoading,
  searchRefined
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
                <span>KI-Diagnose läuft<LoadingDots /></span>
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
            {currentCondition && `ICD-10-GM ${currentCondition.version}`}
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
