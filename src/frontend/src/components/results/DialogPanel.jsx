import React from 'react';
import { formatText } from '../../utils/helpers';

const DialogPanel = ({
  dialogMessages,
  isChatOpen,
  setIsChatOpen,
  dialogLoading,
  messagesEndRef,
  dialogInput,
  setDialogInput,
  handleSendDialog,
  currentCondition
}) => {
  return (
    <div className="dialog-panel">
      {dialogMessages.length > 0 ? (
        /* Once conversation started: show toggle header; input + history are toggled together */
        <>
          <div className="dialog-toggle" onClick={() => setIsChatOpen(!isChatOpen)}>
            <span>Gesprächsverlauf ({dialogMessages.length} Nachrichten)</span>
            <button className="toggle-btn">
              {isChatOpen ? (
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

          {isChatOpen && (
            <div className="dialog-section">
              <div className="dialog-messages">
                {dialogMessages.map((msg, idx) => (
                  <div key={idx} className={`msg ${msg.role === 'user' ? 'user' : 'assistant'}`}>
                    <div
                      className="msg-bubble"
                      dangerouslySetInnerHTML={formatText(msg.text)}
                      style={msg.isError ? { color: 'var(--muted)' } : {}}
                    />
                  </div>
                ))}
                {dialogLoading && (
                  <div className="msg assistant">
                    <div className="msg-spinner">
                      <div className="spinner"></div>Antwort wird generiert…
                    </div>
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
  );
};

export default DialogPanel;
