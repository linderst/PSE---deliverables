/**
 * @module OtherMatches
 * @description Renders alternative diagnosis results as a horizontal row of
 * clickable chips. Each chip shows the ICD-10 code; a tooltip on hover
 * reveals the full title and confidence percentage. High-confidence matches
 * (score >= 0.95) receive a green highlight and a checkmark badge.
 *
 * @component
 * @param {Object} props
 * @param {Array}    props.otherMatches          - Array of {code, title, score} objects
 * @param {Function} props.handleSelectCondition - Callback when a chip is clicked
 * @returns {React.JSX.Element|null} Returns null when otherMatches is empty
 */
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
