/**
 * @module InfoBlocks
 * @description Three-column grid of AI-generated information cards:
 * - "Was ist das?" (explain) — layman-friendly diagnosis explanation
 * - "Wer behandelt das?" (specialist) — recommended doctor / specialist + extradoc.ch link
 * - "Wie wird behandelt?" (guidance) — initial treatment steps
 *
 * Each block independently shows a loading spinner, error state, or the
 * formatted AI response via dangerouslySetInnerHTML (content comes from
 * the trusted backend / Gemini API).
 *
 * @component
 * @param {Object} props
 * @param {{ loading: boolean, data: string|null, error: string|null }} props.explain    - Explain block state
 * @param {{ loading: boolean, data: string|null, error: string|null }} props.specialist - Specialist block state
 * @param {{ loading: boolean, data: string|null, error: string|null }} props.guidance   - Guidance block state
 */
import React from 'react';
import { formatText } from '../../utils/helpers';

const InfoBlocks = ({ explain, specialist, guidance }) => {
  return (
    <div className="blocks-grid">
      {/* Explain Block */}
      <div className="block">
        <div className="block-header">
          <div className="block-icon blue">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4M12 8h.01" />
            </svg>
          </div>
          <span className="block-label">Was ist das?</span>
        </div>
        <div>
          {explain.loading && <div className="block-loading"><div className="spinner"></div>Wird geladen…</div>}
          {explain.error && <div className="block-body"><p style={{ color: 'var(--muted)' }}>{explain.error}</p></div>}
          {explain.data && <div className="block-body" dangerouslySetInnerHTML={formatText(explain.data)} />}
        </div>
      </div>

      {/* Specialist Block */}
      <div className="block">
        <div className="block-header">
          <div className="block-icon green">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <span className="block-label">Wer behandelt das?</span>
        </div>
        <div>
          {specialist.loading && <div className="block-loading"><div className="spinner"></div>Wird geladen…</div>}
          {specialist.error && <div className="block-body"><p style={{ color: 'var(--muted)' }}>{specialist.error}</p></div>}
          {specialist.data && (
            <div className="block-body">
              <div dangerouslySetInnerHTML={formatText(specialist.data)} />
              <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
                <a
                  href="https://extradoc.ch"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    background: 'var(--accent-light)',
                    color: 'var(--accent)',
                    padding: '8px 14px',
                    borderRadius: '8px',
                    fontSize: '13px',
                    fontWeight: '600',
                    textDecoration: 'none',
                    border: '1px solid rgba(37,99,235,0.1)',
                    transition: 'transform 0.2s'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
                  onMouseOut={(e) => e.currentTarget.style.transform = 'none'}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                  Passenden Arzt finden auf extradoc.ch
                </a>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Guidance Block */}
      <div className="block">
        <div className="block-header">
          <div className="block-icon amber">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <span className="block-label">Wie wird behandelt?</span>
        </div>
        <div>
          {guidance.loading && <div className="block-loading"><div className="spinner"></div>Wird geladen…</div>}
          {guidance.error && <div className="block-body"><p style={{ color: 'var(--muted)' }}>{guidance.error}</p></div>}
          {guidance.data && <div className="block-body" dangerouslySetInnerHTML={formatText(guidance.data)} />}
        </div>
      </div>
    </div>
  );
};

export default InfoBlocks;
