/**
 * @module AlphabetIndex
 * @description Renders an A-Z navigation with clickable letter buttons and a
 * filtered list of pre-cached ICD-10 diagnoses. Extracts unique starting
 * letters from the conditions array and displays matching entries as
 * pill-shaped links.
 *
 * @component
 * @param {Object} props
 * @param {Array}    props.cachedConditions       - Array of {code, title} objects from /api/cached-conditions
 * @param {string}   props.activeLetter          - Currently selected letter filter
 * @param {Function} props.setActiveLetter       - Setter to change the active letter
 * @param {Function} props.handleSelectCondition - Callback when a condition pill is clicked
 * @returns {React.JSX.Element|null} Returns null when cachedConditions is empty
 */
import React from 'react';
import { slugify } from '../../utils/helpers';

const AlphabetIndex = ({
  cachedConditions,
  activeLetter,
  setActiveLetter,
  handleSelectCondition
}) => {
  if (!cachedConditions || cachedConditions.length === 0) return null;

  // Extract unique starting letters from condition titles
  const letters = Array.from(
    new Set(cachedConditions.map((c) => c.title.charAt(0).toUpperCase()))
  ).sort();

  return (
    <div className="cached-conditions-container">
      <div className="cached-title">Krankheits-Index (A-Z)</div>

      <div className="alphabet-nav">
        {letters.map((letter) => (
          <button
            key={letter}
            className={`alphabet-btn ${activeLetter === letter ? 'active' : ''}`}
            onClick={() => setActiveLetter(letter)}
          >
            {letter}
          </button>
        ))}
      </div>

      <div className="cached-list">
        {cachedConditions
          .filter((c) => c.title.charAt(0).toUpperCase() === activeLetter)
          .map((c) => (
            <a
              key={c.code}
              href={`/${slugify(c.title)}/${c.code}`}
              className="cached-pill"
              onClick={(e) => {
                e.preventDefault();
                handleSelectCondition(c.code, c.title, 1.0);
              }}
            >
              {c.title}
            </a>
          ))}
        {cachedConditions.filter(
          (c) => c.title.charAt(0).toUpperCase() === activeLetter
        ).length === 0 && (
          <div style={{ fontSize: '13px', color: 'var(--muted)', padding: '10px 0' }}>
            Keine Einträge für diesen Buchstaben.
          </div>
        )}
      </div>
    </div>
  );
};

export default AlphabetIndex;
