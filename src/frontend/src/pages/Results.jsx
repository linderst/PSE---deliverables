/**
 * @module Results
 * @description Results page route container. Reads the ICD-10 code from the
 *              URL (via useParams) or the search query (via useSearchParams)
 *              to drive the two-phase search and render all result components.
 *
 * Coordinates the four custom hooks:
 *   - useSearch         → search state & logic
 *   - useChatBlocks     → AI info blocks (explain/specialist/guidance)
 *   - useContextualChat → Q&A dialog
 *   - useSubcodes       → subcodes panel
 */
import React, { useState, useEffect, startTransition } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { slugify } from '../utils/helpers';

import { useSearch } from '../hooks/useSearch';
import { useChatBlocks } from '../hooks/useChatBlocks';
import { useContextualChat } from '../hooks/useContextualChat';
import { useSubcodes } from '../hooks/useSubcodes';

import TopBar from '../components/results/TopBar';
import MatchCard from '../components/results/MatchCard';
import OtherMatches from '../components/results/OtherMatches';
import InfoBlocks from '../components/results/InfoBlocks';
import SubcodesPanel from '../components/results/SubcodesPanel';
import DialogPanel from '../components/results/DialogPanel';

const Results = () => {
  const { code } = useParams();          // set when navigating to /:slug/:code
  const [searchParams] = useSearchParams(); // set when navigating to /search?q=...
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState('');

  // Custom hooks
  const { currentCondition, otherMatches, searchLoading, searchRefined, searchRefining, searchError, longLoading, runSearch, selectCondition } = useSearch();
  const { explain, specialist, guidance, disclaimer, fetchBlocks, resetBlocks } = useChatBlocks();
  const { dialogMessages, dialogInput, setDialogInput, dialogLoading, isChatOpen, setIsChatOpen, messagesEndRef, handleSendDialog, resetDialog } = useContextualChat(currentCondition);
  const { subcodes, subcodesOpen, setSubcodesOpen } = useSubcodes(currentCondition);

  // Dynamic SEO meta tags
  useEffect(() => {
    if (currentCondition) {
      document.title = `${currentCondition.title} (${currentCondition.code}) — medcode.ch`;
      const metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc) metaDesc.setAttribute('content', `Verständliche medizinische Erklärung, Behandlung und Informationen zur Diagnose ${currentCondition.title} (ICD-10 Code ${currentCondition.code}).`);
    }
  }, [currentCondition]);

  // Trigger search when the URL changes (from ?q= query or /:code param)
  useEffect(() => {
    const q = searchParams.get('q');
    const term = code || q;
    if (!term) return;

    // After searching for e.g. "diabetes", we navigate to /:slug/:code (replace: true).
    // This causes the effect to fire again with code='E11'. Skip re-searching if the
    // condition is already loaded for that code — it was just set by the prior search.
    if (code && !q && currentCondition && currentCondition.code === code) return;

    startTransition(() => setSearchTerm(term));

    (async () => {
      const result = await runSearch(term);
      if (result) {
        fetchBlocks(result.code, result.title);
        // If we came in via /search?q= redirect to canonical URL
        if (q && !code) {
          // Keep the original search term visible in the top bar
          startTransition(() => setSearchTerm(term));
          navigate(`/${slugify(result.title)}/${result.code}`, { replace: true });
        }
      }
    })();
  }, [code, searchParams.get('q')]); // eslint-disable-line react-hooks/exhaustive-deps

  /** Run a new search from the TopBar input. */
  const handleSearch = async (term) => {
    const q = (term || '').trim();
    if (!q) return;
    setSearchTerm(q);
    resetDialog();
    resetBlocks();
    const result = await runSearch(q);
    if (result) {
      fetchBlocks(result.code, result.title);
      navigate(`/${slugify(result.title)}/${result.code}`, { replace: true });
    }
  };

  /** Select an alternative match from the chips list. */
  const handleSelectCondition = (condition) => {
    const { code, title } = condition;
    selectCondition(condition);
    resetDialog();
    fetchBlocks(code, title);
    navigate(`/${slugify(title)}/${code}`, { replace: false });
  };

  /** Go back to home. */
  const handleReset = () => {
    document.title = 'medcode.ch — Diagnosensuche';
    navigate('/');
  };

  return (
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
          searchRefining={searchRefining}
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
  );
};

export default Results;
