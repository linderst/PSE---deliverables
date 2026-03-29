import React from 'react';

const OtherMatches = ({ otherMatches, handleSelectCondition }) => {
  if (!otherMatches || otherMatches.length === 0) return null;

  return (
    <div className="other-matches" style={{ display: 'flex' }}>
      <span style={{ color: 'var(--muted)', fontSize: '12px' }}>Weitere Treffer:</span>
      {otherMatches.map((m, i) => (
        <div
          key={i}
          className={`other-match-chip tooltip-wrap${(m.score || 0) >= 0.95 ? ' other-match-chip--high' : ''}`}
          onClick={() => handleSelectCondition(m.code, m.title, m.score)}
        >
          {m.code}
          {(m.score || 0) >= 0.95 && <span className="chip-star">✓</span>}
          <div className="tooltip-bubble">
            <div className="tooltip-title">{m.title}</div>
            <div className="tooltip-score">Sicherheit: {Math.round(m.score * 100)}%</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default OtherMatches;
