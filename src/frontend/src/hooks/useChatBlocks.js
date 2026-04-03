/**
 * @module useChatBlocks
 * @description Custom hook for managing the three parallel AI info blocks
 *              (explain, specialist, guidance). Fetches all three in parallel
 *              whenever a new condition is provided.
 */
import { useState, useCallback } from 'react';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const INITIAL_BLOCK = { loading: false, data: null, error: null };

/**
 * @returns {{
 *   explain: object,
 *   specialist: object,
 *   guidance: object,
 *   disclaimer: string,
 *   fetchBlocks: Function,
 *   resetBlocks: Function,
 * }}
 */
export function useChatBlocks() {
  const [explain, setExplain] = useState(INITIAL_BLOCK);
  const [specialist, setSpecialist] = useState(INITIAL_BLOCK);
  const [guidance, setGuidance] = useState(INITIAL_BLOCK);
  const [disclaimer, setDisclaimer] = useState('');

  /**
   * Generic fetcher for a single AI info block.
   * @param {string} endpoint - API path suffix (e.g. '/chat/explain')
   * @param {string} question - "{code}: {title}"
   * @param {Function} setter - State setter for the block
   */
  const fetchBlock = async (endpoint, question, setter) => {
    try {
      const res = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (data.answer) {
        setter({ loading: false, data: data.answer, error: null });
        if (data.disclaimer) {
          setDisclaimer(
            'Diese Information dient nur zur Orientierung. Eine medizinische Beratung durch einen Arzt, ein ärztliches Zeugnis oder ein Rezept erhalten Sie auf <a href="https://extradoc.ch" target="_blank" rel="noopener">extradoc.ch</a>'
          );
        }
      } else {
        setter({ loading: false, data: null, error: 'Keine Antwort erhalten.' });
      }
    } catch {
      setter({ loading: false, data: null, error: 'Fehler beim Laden.' });
    }
  };

  /**
   * Fires all three AI block fetches in parallel for a given condition.
   * @param {string} code  - ICD-10 code
   * @param {string} title - Diagnosis title
   */
  const fetchBlocks = useCallback((code, title) => {
    const question = `${code}: ${title}`;
    setExplain({ loading: true, data: null, error: null });
    setSpecialist({ loading: true, data: null, error: null });
    setGuidance({ loading: true, data: null, error: null });
    setDisclaimer('');
    fetchBlock('/chat/explain', question, setExplain);
    fetchBlock('/chat/specialist', question, setSpecialist);
    fetchBlock('/chat/guidance', question, setGuidance);
  }, []);

  /** Resets all blocks to their initial (empty) state. */
  const resetBlocks = useCallback(() => {
    setExplain(INITIAL_BLOCK);
    setSpecialist(INITIAL_BLOCK);
    setGuidance(INITIAL_BLOCK);
    setDisclaimer('');
  }, []);

  return { explain, specialist, guidance, disclaimer, fetchBlocks, resetBlocks };
}
