/**
 * @module App
 * @description Root component and central state container for the Medcode SPA.
 *
 * Manages all application state via React useState hooks and coordinates API
 * communication with the FastAPI backend. Implements a binary view model
 * ('hero' landing page vs 'results' detail view) with client-side routing
 * via the History API (pushState / popstate).
 *
 * Architecture decisions:
 * - Centralised state in this single root component (no Context API or
 *   external state library) — keeps the dependency graph flat and explicit.
 * - Prop drilling to child components — acceptable given the shallow
 *   component tree (max depth 2).
 * - Two-phase search strategy: fast Meilisearch/pgvector first, then
 *   optional Gemini AI refinement when confidence < 0.75.
 * - Three parallel fetchBlock() calls for the AI info blocks, so each
 *   block renders independently as soon as its response arrives.
 */
import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import { slugify } from './utils/helpers';

import HeroView from './components/hero/HeroView';
import TopBar from './components/results/TopBar';
import MatchCard from './components/results/MatchCard';
import OtherMatches from './components/results/OtherMatches';
import InfoBlocks from './components/results/InfoBlocks';
import SubcodesPanel from './components/results/SubcodesPanel';
import DialogPanel from './components/results/DialogPanel';

/** @constant {string} API - Base URL for all backend API requests (Vite env or localhost fallback). */
const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [view, setView] = useState('hero'); // 'hero' or 'results'
  const [currentCondition, setCurrentCondition] = useState(null);
  
  // Index state
  const [activeLetter, setActiveLetter] = useState('A');
  
  // Results state
  const [otherMatches, setOtherMatches] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchRefined, setSearchRefined] = useState(false); // true when Gemini improved results
  const [searchError, setSearchError] = useState(null);
  const [longLoading, setLongLoading] = useState(false); // true when waiting for Gemini > 2.5s

  // Blocks state
  const [explain, setExplain] = useState({ loading: false, data: null, error: null });
  const [specialist, setSpecialist] = useState({ loading: false, data: null, error: null });
  const [guidance, setGuidance] = useState({ loading: false, data: null, error: null });
  const [disclaimer, setDisclaimer] = useState('');

  // Dialog state
  const [dialogInput, setDialogInput] = useState('');
  const [dialogMessages, setDialogMessages] = useState([]);
  const [dialogLoading, setDialogLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Subcodes panel state
  const [subcodes, setSubcodes] = useState([]);
  const [subcodesLoading, setSubcodesLoading] = useState(false);
  const [subcodesOpen, setSubcodesOpen] = useState(false);

  // Cached Conditions state
  const [cachedConditions, setCachedConditions] = useState([]);
  const handleSearchRef = useRef(null);

  // Dynamic SEO meta tags
  useEffect(() => {
    if (currentCondition) {
      document.title = `${currentCondition.title} (${currentCondition.code}) — medcode.ch`;
      const metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc) metaDesc.setAttribute('content', `Verständliche medizinische Erklärung, Behandlung und Informationen zur Diagnose ${currentCondition.title} (ICD-10 Code ${currentCondition.code}).`);
    } else {
      document.title = 'medcode.ch — Diagnosensuche';
      const metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc) metaDesc.setAttribute('content', 'ICD-10 Diagnosensuche. Verstehen Sie Ihre Diagnose verständlich erklärt.');
    }
  }, [currentCondition]);

  /**
   * Pushes an SEO-friendly URL to the browser history.
   * @param {string} code  - ICD-10 code (e.g. "J18")
   * @param {string} title - Diagnosis title in German
   * @param {boolean} skipHistory - If true, skip the pushState (used during popstate handling)
   */
  const updateHistory = (code, title, skipHistory) => {
    if (!skipHistory) {
      window.history.pushState({}, '', `/${slugify(title)}/${code}`);
    }
  };

  useEffect(() => {
    // Fetch cached conditions
    fetch(`${API}/cached-conditions`)
      .then(r => r.json())
      .then(data => {
        if (data.conditions) setCachedConditions(data.conditions);
      })
      .catch(e => console.error("Error fetching cached conditions:", e));

    // Handle initial routing based on URL
    const path = window.location.pathname;
    if (path !== '/') {
      const match = path.match(/^\/[^/]+\/([A-Z0-9.-]+)$/i);
      if (match && match[1]) {
        // use setTimeout to ensure handleSearchRef has been assigned
        setTimeout(() => {
          if (handleSearchRef.current) handleSearchRef.current(match[1].toUpperCase(), true);
        }, 50);
      }
    }

    const handlePopState = () => {
      const currentPath = window.location.pathname;
      if (currentPath === '/') {
        setView('hero');
        setSearchTerm('');
        setCurrentCondition(null);
      } else {
        const m = currentPath.match(/^\/[^/]+\/([A-Z0-9.-]+)$/i);
        if (m && m[1]) {
          if (handleSearchRef.current) handleSearchRef.current(m[1].toUpperCase(), true);
        }
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  useEffect(() => {
    let timer;
    if (searchLoading) {
      timer = setTimeout(() => setLongLoading(true), 2500);
    } else {
      setLongLoading(false);
    }
    return () => clearTimeout(timer);
  }, [searchLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [dialogMessages, dialogLoading]);

  // Fetch subcodes whenever the current 3-digit condition changes
  useEffect(() => {
    if (!currentCondition) return;
    const code3 = currentCondition.code.slice(0, 3);
    setSubcodes([]);
    setSubcodesLoading(true);
    setSubcodesOpen(false);
    fetch(`${API}/subcodes?code=${encodeURIComponent(code3)}`)
      .then(r => r.json())
      .then(data => {
        setSubcodes(data.subcodes || []);
        setSubcodesLoading(false);
      })
      .catch(() => setSubcodesLoading(false));
  }, [currentCondition?.code]);

  /**
   * Executes a diagnosis search against the backend API.
   *
   * Implements a two-phase search strategy:
   * 1. Fast search via /api/search (Meilisearch + pgvector).
   * 2. If the top result's confidence score < REFINE_THRESHOLD (0.75),
   *    triggers /api/search/refined which uses Gemini to extract medical
   *    terms and re-runs the search with boosted keywords.
   *
   * After a result is selected, three parallel fetchBlock() calls are fired
   * for the explain/specialist/guidance AI info blocks.
   *
   * @async
   * @param {string} term - Search query (ICD-10 code or free-text symptoms)
   * @param {boolean} [skipHistory=false] - If true, does not push to browser history
   */
  const handleSearch = async (term, skipHistory = false) => {
    const q = (term || '').trim();
    if (!q) return;

    setView('results');
    setSearchTerm(q);
    setSearchLoading(true);
    setSearchError(null);
    setCurrentCondition(null);
    setOtherMatches([]);
    setDisclaimer('');
    setSearchRefined(false);
    
    // Reset blocks
    setExplain({ loading: true, data: null, error: null });
    setSpecialist({ loading: true, data: null, error: null });
    setGuidance({ loading: true, data: null, error: null });
    
    // Reset dialog
    setDialogMessages([]);
    setDialogInput('');
    setIsChatOpen(false);

    try {
      // Fire fast search immediately
      const res = await fetch(`${API}/search?q=${encodeURIComponent(q)}&limit=5`);
      const data = await res.json();
      const results = data.results || [];

      if (!results.length) {
        setSearchError('Keine passenden ICD-10-Codes gefunden.');
        setExplain({ loading: false, data: null, error: 'Keine Ergebnisse.' });
        setSpecialist({ loading: false, data: null, error: 'Keine Ergebnisse.' });
        setGuidance({ loading: false, data: null, error: 'Keine Ergebnisse.' });
        setSearchLoading(false);
        return;
      }

      const top = results[0];
      const REFINE_THRESHOLD = 0.75;

      // If confidence is high, show immediately and trigger blocks
      if ((top.score || 0) >= REFINE_THRESHOLD) {
        setCurrentCondition({ code: top.code, title: top.title, version: top.version, score: top.score });
        if (results.length > 1) setOtherMatches(results.slice(1));
        setSearchLoading(false);
        updateHistory(top.code, top.title, skipHistory);

        const question = `${top.code}: ${top.title}`;
        fetchBlock('/chat/explain', question, setExplain);
        fetchBlock('/chat/specialist', question, setSpecialist);
        fetchBlock('/chat/guidance', question, setGuidance);
      } else {
        // Low confidence: wait for AI Gemini refinement to avoid showing garbage with low %
        try {
          const refinedRes = await fetch(`${API}/search/refined?q=${encodeURIComponent(q)}&limit=5`);
          const refinedData = await refinedRes.json();
          const refined = refinedData.results || [];
          
          if (refined.length > 0) {
            const refinedTop = refined[0];
            setCurrentCondition({ code: refinedTop.code, title: refinedTop.title, version: refinedTop.version, score: refinedTop.score });
            if (refined.length > 1) setOtherMatches(refined.slice(1));
            setSearchRefined(true);
            setSearchLoading(false);
            updateHistory(refinedTop.code, refinedTop.title, skipHistory);

            const refinedQuestion = `${refinedTop.code}: ${refinedTop.title}`;
            fetchBlock('/chat/explain', refinedQuestion, setExplain);
            fetchBlock('/chat/specialist', refinedQuestion, setSpecialist);
            fetchBlock('/chat/guidance', refinedQuestion, setGuidance);
            return;
          }
        } catch (e) {
          // If Gemini fails, silently fall through to the original result
        }

        // Absolute Fallback: if Gemini failed or found nothing, show the initial weak result
        setCurrentCondition({ code: top.code, title: top.title, version: top.version, score: top.score });
        if (results.length > 1) setOtherMatches(results.slice(1));
        setSearchLoading(false);
        updateHistory(top.code, top.title, skipHistory);

        const question = `${top.code}: ${top.title}`;
        fetchBlock('/chat/explain', question, setExplain);
        fetchBlock('/chat/specialist', question, setSpecialist);
        fetchBlock('/chat/guidance', question, setGuidance);
      }

    } catch (e) {
      setSearchError('Fehler bei der Suche. Bitte erneut versuchen.');
      setSearchLoading(false);
    }
  };

  /**
   * Generic fetcher for a single AI info block (explain, specialist, or guidance).
   * Acts as a Facade: the caller only supplies the endpoint suffix and a state setter.
   *
   * @async
   * @param {string} endpoint - API path suffix (e.g. '/chat/explain')
   * @param {string} question - The formatted question "{code}: {title}"
   * @param {Function} setter  - React state setter for the block's {loading, data, error} object
   */
  const fetchBlock = async (endpoint, question, setter) => {
    try {
      const res = await fetch(`${API}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await res.json();
      if (data.answer) {
        setter({ loading: false, data: data.answer, error: null });
        if (data.disclaimer) {
          setDisclaimer('Diese Information dient nur zur Orientierung. Eine medizinische Beratung durch einen Arzt, ein ärztliches Zeugnis oder ein Rezept erhalten Sie auf <a href="https://extradoc.ch" target="_blank" rel="noopener">extradoc.ch</a>');
        }
      } else {
        setter({ loading: false, data: null, error: 'Keine Antwort erhalten.' });
      }
    } catch (e) {
      setter({ loading: false, data: null, error: 'Fehler beim Laden.' });
    }
  };

  /**
   * Handles selection of a diagnosis from OtherMatches chips or AlphabetIndex.
   * Swaps the current main result into the chips list and promotes the
   * clicked item to the primary MatchCard. Resets and reloads all AI blocks.
   *
   * @param {string} code  - ICD-10 code of the selected diagnosis
   * @param {string} title - Title of the selected diagnosis
   * @param {number} score - Confidence score (0.0-1.0)
   * @param {boolean} [skipHistory=false] - If true, skip browser history push
   */
  const handleSelectCondition = (code, title, score, skipHistory = false) => {
    // Switch to results view if we are on hero
    if (view === 'hero') setView('results');

    // Swap: put the current main result back into the chips list
    setOtherMatches(prev => {
      const prevMain = currentCondition;
      // Remove the clicked item from chips, add the old main result
      const withoutClicked = prev.filter(m => m.code !== code);
      if (prevMain && prevMain.code !== code) {
        return [{ code: prevMain.code, title: prevMain.title, score: prevMain.score }, ...withoutClicked];
      }
      return withoutClicked;
    });

    setCurrentCondition({ code, title, version: '2024', score });
    updateHistory(code, title, skipHistory);
    
    // Reset contents
    setExplain({ loading: true, data: null, error: null });
    setSpecialist({ loading: true, data: null, error: null });
    setGuidance({ loading: true, data: null, error: null });
    setDialogMessages([]);
    setDialogInput('');
    setIsChatOpen(false);

    const question = `${code}: ${title}`;
    fetchBlock('/chat/explain', question, setExplain);
    fetchBlock('/chat/specialist', question, setSpecialist);
    fetchBlock('/chat/guidance', question, setGuidance);
  };

  /**
   * Sends a follow-up question to the contextual chat endpoint.
   * Appends the user message immediately and the AI response upon arrival.
   * The chat keeps the current ICD-10 diagnosis as context so the LLM
   * answers within the scope of the active condition.
   *
   * @async
   */
  const handleSendDialog = async () => {
    const q = dialogInput.trim();
    if (!q || !currentCondition) return;

    setDialogInput('');
    const newMessages = [...dialogMessages, { role: 'user', text: q }];
    setDialogMessages(newMessages);
    setDialogLoading(true);
    setIsChatOpen(true); // auto-expand when user sends first message

    try {
      const res = await fetch(`${API}/chat/contextual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          condition_code: currentCondition.code,
          condition_title: currentCondition.title
        })
      });
      const data = await res.json();
      setDialogMessages([...newMessages, { role: 'assistant', text: data.answer || 'Keine Antwort erhalten.' }]);
    } catch (e) {
      setDialogMessages([...newMessages, { role: 'assistant', text: 'Fehler bei der Anfrage.', isError: true }]);
    } finally {
      setDialogLoading(false);
    }
  };

  /**
   * Resets all application state and navigates back to the hero (landing) view.
   * Used when the user clicks the medcode.ch logo or navigates to '/'.
   *
   * @param {Event|boolean} e_or_skipHistory - Either a click event or boolean
   *   indicating whether to skip the history push (true when triggered by popstate)
   */
  const handleReset = (e_or_skipHistory) => {
    const skipHistory = e_or_skipHistory === true;
    setView('hero');
    setSearchTerm('');
    setCurrentCondition(null);
    setSearchError(null);
    setOtherMatches([]);
    setSearchRefined(false);
    setExplain({ loading: false, data: null, error: null });
    setSpecialist({ loading: false, data: null, error: null });
    setGuidance({ loading: false, data: null, error: null });
    setDialogMessages([]);
    setDialogInput('');
    setIsChatOpen(false);
    setSubcodes([]);
    setSubcodesOpen(false);
    if (!skipHistory) {
      window.history.pushState({}, '', '/');
    }
  };

  handleSearchRef.current = handleSearch;

  return (
    <div className="layout">
      <main className="main">
        {view === 'hero' ? (
          <HeroView
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            handleSearch={handleSearch}
            cachedConditions={cachedConditions}
            activeLetter={activeLetter}
            setActiveLetter={setActiveLetter}
            handleSelectCondition={handleSelectCondition}
          />
        ) : (
          <div className="results-view visible">
            <div className="results-content">
              <TopBar
                handleReset={handleReset}
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                handleSearch={handleSearch}
              />

              <MatchCard
                searchLoading={searchLoading}
                currentCondition={currentCondition}
                searchError={searchError}
                longLoading={longLoading}
                searchRefined={searchRefined}
              />

              <OtherMatches
                otherMatches={otherMatches}
                handleSelectCondition={handleSelectCondition}
              />

              <InfoBlocks
                explain={explain}
                specialist={specialist}
                guidance={guidance}
              />

              {disclaimer && (
                <div className="disclaimer" dangerouslySetInnerHTML={{ __html: disclaimer }} />
              )}
            </div>

            <SubcodesPanel
              subcodes={subcodes}
              subcodesOpen={subcodesOpen}
              setSubcodesOpen={setSubcodesOpen}
              handleSelectCondition={handleSelectCondition}
            />

            <DialogPanel
              dialogMessages={dialogMessages}
              isChatOpen={isChatOpen}
              setIsChatOpen={setIsChatOpen}
              dialogLoading={dialogLoading}
              messagesEndRef={messagesEndRef}
              dialogInput={dialogInput}
              setDialogInput={setDialogInput}
              handleSendDialog={handleSendDialog}
              currentCondition={currentCondition}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
