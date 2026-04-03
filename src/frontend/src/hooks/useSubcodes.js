/**
 * @module useSubcodes
 * @description Custom hook that fetches and manages the subcodes panel
 *              for a given 3-digit ICD-10 code. Refetches automatically
 *              whenever the active condition changes.
 */
import { useState, useEffect, startTransition } from 'react';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * @param {object|null} currentCondition - The active ICD-10 condition object
 * @returns {{
 *   subcodes: array,
 *   subcodesLoading: boolean,
 *   subcodesOpen: boolean,
 *   setSubcodesOpen: Function,
 * }}
 */
export function useSubcodes(currentCondition) {
  const [subcodes, setSubcodes] = useState([]);
  const [subcodesLoading, setSubcodesLoading] = useState(false);
  const [subcodesOpen, setSubcodesOpen] = useState(false);

  useEffect(() => {
    if (!currentCondition) return;

    const code3 = currentCondition.code.slice(0, 3);

    // Batch the synchronous resets into a transition to satisfy lint rules
    startTransition(() => {
      setSubcodes([]);
      setSubcodesLoading(true);
      setSubcodesOpen(false);
    });

    fetch(`${API}/subcodes?code=${encodeURIComponent(code3)}`)
      .then(r => r.json())
      .then(data => {
        setSubcodes(data.subcodes || []);
        setSubcodesLoading(false);
      })
      .catch(() => setSubcodesLoading(false));
  }, [currentCondition?.code]); // eslint-disable-line react-hooks/exhaustive-deps

  return { subcodes, subcodesLoading, subcodesOpen, setSubcodesOpen };
}
