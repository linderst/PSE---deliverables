/**
 * @module SubcodesPanel
 * @description Expandable/collapsible panel listing the ICD-10 subcodes
 * (4-digit specialisations) of the current 3-digit diagnosis category.
 * Each row shows the code, title, and a relative relevance bar based on
 * synonym count. Clicking a subcode navigates to that specific diagnosis.
 *
 * @component
 * @param {Object} props
 * @param {Array}    props.subcodes              - Array of {code, title, synonym_count}
 * @param {boolean}  props.subcodesOpen          - Whether the panel is expanded
 * @param {Function} props.setSubcodesOpen       - Toggle setter for expansion state
 * @param {Function} props.handleSelectCondition - Callback when a subcode row is clicked
 * @returns {React.JSX.Element|null} Returns null when subcodes is empty
 */
import React from 'react';

const SubcodesPanel = ({ subcodes, subcodesOpen, setSubcodesOpen, handleSelectCondition }) => {
  if (!subcodes || subcodes.length === 0) return null;

  return (
    <div className="subcodes-panel">
      <div className="subcodes-toggle" onClick={() => setSubcodesOpen(!subcodesOpen)}>
        <div className="subcodes-toggle-left">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="8" y1="6" x2="21" y2="6"></line>
            <line x1="8" y1="12" x2="21" y2="12"></line>
            <line x1="8" y1="18" x2="21" y2="18"></line>
            <line x1="3" y1="6" x2="3.01" y2="6"></line>
            <line x1="3" y1="12" x2="3.01" y2="12"></line>
            <line x1="3" y1="18" x2="3.01" y2="18"></line>
          </svg>
          <span>Spezifische Diagnosen ({subcodes.length} Unterkategorien)</span>
        </div>
        <button className="toggle-btn">
          {subcodesOpen ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          )}
        </button>
      </div>

      {subcodesOpen && (
        <div className="subcodes-list">
          <div style={{ padding: '8px 20px', display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontWeight: '600', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', borderBottom: '1px solid var(--border)', background: 'var(--surface)' }}>
            <span>Unterkategorien</span>
            <span>Klinische Relevanz</span>
          </div>
          {(() => {
            const maxSynonyms = Math.max(...subcodes.map(s => s.synonym_count), 1);
            return subcodes.map((sub) => {
              const barWidth = Math.max(5, (sub.synonym_count / maxSynonyms) * 100);
              return (
                <div
                  key={sub.code}
                  className="subcode-item"
                  onClick={() => handleSelectCondition({ code: sub.code, title: sub.title, score: 0.99, version: '2024' })}
                >
                  <div className="subcode-item-left">
                    <span className="subcode-code">{sub.code}</span>
                    <span className="subcode-title">{sub.title}</span>
                  </div>
                  <div className="subcode-item-right" title={`Relevanz-Score: ${sub.synonym_count}`}>
                    <div className="subcode-bar-bg">
                      <div className="subcode-bar-fill" style={{ width: `${barWidth}%` }}></div>
                    </div>
                  </div>
                </div>
              );
            });
          })()}
        </div>
      )}
    </div>
  );
};

export default SubcodesPanel;
