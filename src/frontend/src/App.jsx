import React, { useState, useRef, useEffect } from 'react';
import './App.css';

// Using Vite's environment variables or defaulting to localhost:8000
const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [view, setView] = useState('hero'); // 'hero' or 'results'
  const [currentCondition, setCurrentCondition] = useState(null);
  
  // Results state
  const [otherMatches, setOtherMatches] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchRefined, setSearchRefined] = useState(false); // true when Gemini improved results
  const [searchError, setSearchError] = useState(null);

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

  const formatText = (text) => {
    if (!text) return { __html: '' };
    // Very basic formatting: newlines to <br>, **text** to <strong>text</strong>
    const formatted = text
      .split(/\n\n+/)
      .map(p => `<p>${p.replace(/\n/g,'<br>').replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')}</p>`)
      .join('');
    return { __html: formatted };
  };

  const handleSearch = async (term) => {
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
      setCurrentCondition({ code: top.code, title: top.title, version: top.version, score: top.score });
      if (results.length > 1) setOtherMatches(results.slice(1));
      setSearchLoading(false);

      // Fire 3 content blocks
      const question = `${top.code}: ${top.title}`;
      fetchBlock('/chat/explain', question, setExplain);
      fetchBlock('/chat/specialist', question, setSpecialist);
      fetchBlock('/chat/guidance', question, setGuidance);

      // In parallel: fire Gemini-refined search — but ONLY when the initial
      // confidence is low (< 0.75). If Meilisearch is already confident, skip.
      const REFINE_THRESHOLD = 0.75;
      if ((top.score || 0) < REFINE_THRESHOLD) {
        fetch(`${API}/search/refined?q=${encodeURIComponent(q)}&limit=5`)
          .then(r => r.json())
          .then(refinedData => {
            const refined = refinedData.results || [];
            if (!refined.length) return;
            const refinedTop = refined[0];
            // Only swap if Gemini found a meaningfully different top result
            if (refinedTop.code !== top.code) {
              setCurrentCondition({ code: refinedTop.code, title: refinedTop.title, version: refinedTop.version, score: refinedTop.score });
              setOtherMatches(refined.slice(1));
              setSearchRefined(true);
              const refinedQuestion = `${refinedTop.code}: ${refinedTop.title}`;
              setExplain({ loading: true, data: null, error: null });
              setSpecialist({ loading: true, data: null, error: null });
              setGuidance({ loading: true, data: null, error: null });
              fetchBlock('/chat/explain', refinedQuestion, setExplain);
              fetchBlock('/chat/specialist', refinedQuestion, setSpecialist);
              fetchBlock('/chat/guidance', refinedQuestion, setGuidance);
            }
          })
          .catch(() => {}); // Silently ignore refinement errors
      }


    } catch (e) {
      setSearchError('Fehler bei der Suche. Bitte erneut versuchen.');
      setSearchLoading(false);
    }
  };

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

  const handleSelectCondition = (code, title, score) => {
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

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>medcode.ch</h1>
          <p>Diagnosensuche</p>
        </div>
        <div className="sidebar-section">Letzte Suchen</div>
        <div className="history-list">
          <div className="history-empty">Verlauf wird für diese Sitzung nicht gespeichert.</div>
        </div>
        <a 
          href="https://extradoc.ch" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="sidebar-extradoc-link"
        >
          Arztzeugnis online: extradoc.ch
        </a>
      </aside>

      {/* Main */}
      <main className="main">
        {view === 'hero' ? (
          <div className="hero">
            <div className="hero-badge">ICD-10 Diagnosensuche</div>
            <div>
              <div className="hero-title">Was steht in Ihrem Arztbrief?</div>
              <div className="hero-sub" style={{ marginTop: '12px' }}>
                Geben Sie einen medizinischen Begriff, eine Diagnose oder einen ICD-10-Code ein — wir erklären ihn verständlich.
              </div>
            </div>
            <div className="search-wrap">
              <input 
                type="text" 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Medizinischen Begriff oder Code eingeben..." 
                onKeyDown={(e) => e.key === 'Enter' && handleSearch(searchTerm)}
                autoFocus
              />
              <button className="search-btn" onClick={() => handleSearch(searchTerm)}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                </svg>
              </button>
            </div>
          </div>
        ) : (
          <div className="results-view visible">
            <div className="results-content">
              {/* Top bar with inline search */}
              <div className="results-topbar">
                <div className="search-wrap no-animate">
                  <input 
                    type="text" 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Neue Suche..." 
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch(searchTerm)}
                  />
                  <button className="search-btn" onClick={() => handleSearch(searchTerm)}>
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                    </svg>
                  </button>
                </div>
              </div>

              {/* Primary match */}
              <div className="match-card">
                <div className="match-content">
                  <div className="match-code">{searchLoading ? '…' : (currentCondition ? currentCondition.code : '?')}</div>
                  <div className="match-info">
                    <div className="match-title">
                      {searchLoading ? 'Suche läuft…' : (currentCondition ? currentCondition.title : searchError)}
                    </div>
                    <div className="match-meta">
                      {currentCondition && `ICD-10-GM ${currentCondition.version}`}
                    </div>
                    {searchRefined && (
                      <div className="refined-badge">✦ KI-verfeinert</div>
                    )}
                  </div>
                </div>
                {/* Tachometer */}
                {currentCondition && !searchLoading && currentCondition.score != null && (
                  <div className="tachometer">
                    <svg viewBox="0 0 36 36" className="circular-chart">
                      <path className="circle-bg"
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path className="circle"
                        strokeDasharray={`${Math.round(currentCondition.score * 100)}, 100`}
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <text x="18" y="20.35" className="percentage">{Math.round(currentCondition.score * 100)}%</text>
                    </svg>
                    <div className="tacho-label">Treffer</div>
                  </div>
                )}
              </div>

              {/* Other matches */}
              {otherMatches.length > 0 && (
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
              )}

              {/* Three content blocks */}
              <div className="blocks-grid">
                {/* Explain */}
                <div className="block">
                  <div className="block-header">
                    <div className="block-icon blue">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
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

                {/* Specialist */}
                <div className="block">
                  <div className="block-header">
                    <div className="block-icon green">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                      </svg>
                    </div>
                    <span className="block-label">Wer behandelt das?</span>
                  </div>
                  <div>
                    {specialist.loading && <div className="block-loading"><div className="spinner"></div>Wird geladen…</div>}
                    {specialist.error && <div className="block-body"><p style={{ color: 'var(--muted)' }}>{specialist.error}</p></div>}
                    {specialist.data && <div className="block-body" dangerouslySetInnerHTML={formatText(specialist.data)} />}
                  </div>
                </div>

                {/* Guidance */}
                <div className="block">
                  <div className="block-header">
                    <div className="block-icon amber">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
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

              {disclaimer && (
                <div className="disclaimer" dangerouslySetInnerHTML={{ __html: disclaimer }} />
              )}
            </div>

            {/* Subcodes Panel */}
            {subcodes.length > 0 && (
              <div className="subcodes-panel">
                <div 
                  className="subcodes-toggle" 
                  onClick={() => setSubcodesOpen(!subcodesOpen)}
                >
                  <div className="subcodes-toggle-left">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line>
                    </svg>
                    <span>Spezifische Diagnosen ({subcodes.length} Unterkategorien)</span>
                  </div>
                  <button className="toggle-btn">
                    {subcodesOpen ? (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
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
                            onClick={() => handleSelectCondition(sub.code, sub.title, 0.99)}
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
            )}

            {/* Dialog Panel */}
            <div className="dialog-panel">
              {dialogMessages.length > 0 ? (
                /* Once conversation started: show toggle header; input + history are toggled together */
                <>
                  <div 
                    className="dialog-toggle" 
                    onClick={() => setIsChatOpen(!isChatOpen)}
                  >
                    <span>Gesprächsverlauf ({dialogMessages.length} Nachrichten)</span>
                    <button className="toggle-btn">
                      {isChatOpen ? (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>
                      ) : (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                      )}
                    </button>
                  </div>

                  {isChatOpen && (
                    <div className="dialog-section">
                      <div className="dialog-messages">
                        {dialogMessages.map((msg, idx) => (
                          <div key={idx} className={`msg ${msg.role === 'user' ? 'user' : 'assistant'}`}>
                            <div className="msg-bubble" dangerouslySetInnerHTML={formatText(msg.text)} 
                                 style={msg.isError ? { color: 'var(--muted)' } : {}}/>
                          </div>
                        ))}
                        {dialogLoading && (
                          <div className="msg assistant">
                            <div className="msg-spinner"><div className="spinner"></div>Antwort wird generiert…</div>
                          </div>
                        )}
                        <div ref={messagesEndRef} />
                      </div>
                      <div className="dialog-input-row">
                        <input 
                          type="text" 
                          value={dialogInput}
                          onChange={(e) => setDialogInput(e.target.value)}
                          placeholder="Stellen Sie eine Folgefrage zu dieser Diagnose..." 
                          onKeyDown={(e) => e.key === 'Enter' && handleSendDialog()}
                          disabled={!currentCondition || dialogLoading}
                        />
                        <button 
                          className="dialog-send" 
                          onClick={handleSendDialog}
                          disabled={!currentCondition || dialogLoading || !dialogInput.trim()}
                        >
                          Senden
                        </button>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                /* No messages yet: only show the input bar */
                <div className="dialog-input-row">
                  <input 
                    type="text" 
                    value={dialogInput}
                    onChange={(e) => setDialogInput(e.target.value)}
                    placeholder="Stellen Sie eine Folgefrage zu dieser Diagnose..." 
                    onKeyDown={(e) => e.key === 'Enter' && handleSendDialog()}
                    disabled={!currentCondition || dialogLoading}
                  />
                  <button 
                    className="dialog-send" 
                    onClick={handleSendDialog}
                    disabled={!currentCondition || dialogLoading || !dialogInput.trim()}
                  >
                    Senden
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
