/**
 * @module useSearch
 * @description Custom hook encapsulating the two-phase hybrid search logic.
 *
 * Phase 1: Fast Meilisearch/pgvector search via /api/search.
 * Phase 2: If top result confidence < REFINE_THRESHOLD, triggers
 *          /api/search/refined (Gemini-enhanced) for better accuracy.
 */
import { useState, useEffect } from 'react';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const REFINE_THRESHOLD = 0.75;

/**
 * @returns {{
 *   currentCondition: object|null,
 *   otherMatches: array,
 *   searchLoading: boolean,
 *   searchRefined: boolean,
 *   searchError: string|null,
 *   longLoading: boolean,
 *   runSearch: Function,
 *   selectCondition: Function,
 * }}
 */
export function useSearch() {
  const [currentCondition, setCurrentCondition] = useState(null);
  const [otherMatches, setOtherMatches] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchRefined, setSearchRefined] = useState(false);
  const [searchRefining, setSearchRefining] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [longLoading, setLongLoading] = useState(false);

  // Show "long loading" hint after 2.5 seconds
  useEffect(() => {
    let timer;
    if (searchLoading) {
      timer = setTimeout(() => setLongLoading(true), 2500);
    }
    return () => {
      clearTimeout(timer);
      if (!searchLoading) setLongLoading(false);
    };
  }, [searchLoading]);

  /**
   * Executes a diagnosis search against the backend API.
   * @param {string} term - Search query (ICD-10 code or free-text symptoms)
   * @returns {object|null} The top result condition, or null on failure.
   */
  const runSearch = async (term) => {
    const q = (term || '').trim();
    if (!q) return null;

    setSearchLoading(true);
    setSearchError(null);
    setCurrentCondition(null);
    setOtherMatches([]);
    setSearchRefined(false);
    setSearchRefining(false);

    try {
      const res = await fetch(`${API}/search?q=${encodeURIComponent(q)}&limit=5`);
      const data = await res.json();
      const results = data.results || [];

      if (!results.length) {
        setSearchError('Keine passenden ICD-10-Codes gefunden.');
        setSearchLoading(false);
        return null;
      }

      const top = results[0];

      if ((top.score || 0) >= REFINE_THRESHOLD) {
        setCurrentCondition(top);
        if (results.length > 1) setOtherMatches(results.slice(1));
        setSearchLoading(false);
        return top;
      }

      // Low confidence — try Gemini-enhanced refined search
      setSearchRefining(true);
      try {
        const refinedRes = await fetch(`${API}/search/refined?q=${encodeURIComponent(q)}&limit=5`);
        const refinedData = await refinedRes.json();
        const refined = refinedData.results || [];

        if (refined.length > 0) {
          const refinedTop = refined[0];
          setCurrentCondition(refinedTop);
          if (refined.length > 1) setOtherMatches(refined.slice(1));
          setSearchRefined(true);
          setSearchRefining(false);
          setSearchLoading(false);
          return refinedTop;
        }
      } catch {
        // Gemini failed — silently fall through to original weak result
      } finally {
        setSearchRefining(false);
      }

      // Absolute fallback: use the original weak result
      setCurrentCondition(top);
      if (results.length > 1) setOtherMatches(results.slice(1));
      setSearchLoading(false);
      return top;

    } catch {
      setSearchError('Fehler bei der Suche. Bitte erneut versuchen.');
      setSearchLoading(false);
      return null;
    }
  };

  /**
   * Promotes an alternative match to the primary result.
   * @param {object} condition - Full ICD-10 condition object
   */
  const selectCondition = (condition) => {
    const { code, title, score, version } = condition;
    setOtherMatches(prev => {
      const prevMain = currentCondition;
      const withoutClicked = prev.filter(m => m.code !== code);
      if (prevMain && prevMain.code !== code) {
        return [prevMain, ...withoutClicked];
      }
      return withoutClicked;
    });
    setCurrentCondition(condition);
  };

  return {
    currentCondition,
    otherMatches,
    searchLoading,
    searchRefined,
    searchRefining,
    searchError,
    longLoading,
    runSearch,
    selectCondition,
  };
}
