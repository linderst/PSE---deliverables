/**
 * @module useContextualChat
 * @description Custom hook that manages the contextual Q&A dialog.
 *              Keeps a message history for the current condition and
 *              POSTs follow-up questions to /api/chat/contextual.
 */
import { useState, useRef, useEffect, useCallback } from 'react';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * @param {object|null} currentCondition - The active ICD-10 condition object
 * @returns {{
 *   dialogMessages: array,
 *   dialogInput: string,
 *   setDialogInput: Function,
 *   dialogLoading: boolean,
 *   isChatOpen: boolean,
 *   setIsChatOpen: Function,
 *   messagesEndRef: React.RefObject,
 *   handleSendDialog: Function,
 *   resetDialog: Function,
 * }}
 */
export function useContextualChat(currentCondition) {
  const [dialogMessages, setDialogMessages] = useState([]);
  const [dialogInput, setDialogInput] = useState('');
  const [dialogLoading, setDialogLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [dialogMessages, dialogLoading]);

  /**
   * Sends the current dialogInput as a contextual question to the backend.
   * Appends user message immediately, then appends AI response on arrival.
   */
  const handleSendDialog = useCallback(async () => {
    const q = dialogInput.trim();
    if (!q || !currentCondition) return;

    setDialogInput('');
    const newMessages = [...dialogMessages, { role: 'user', text: q }];
    setDialogMessages(newMessages);
    setDialogLoading(true);
    setIsChatOpen(true);

    try {
      const res = await fetch(`${API}/chat/contextual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          condition_code: currentCondition.code,
          condition_title: currentCondition.title,
        }),
      });
      const data = await res.json();
      setDialogMessages([
        ...newMessages,
        { role: 'assistant', text: data.answer || 'Keine Antwort erhalten.' },
      ]);
    } catch {
      setDialogMessages([
        ...newMessages,
        { role: 'assistant', text: 'Fehler bei der Anfrage.', isError: true },
      ]);
    } finally {
      setDialogLoading(false);
    }
  }, [dialogInput, dialogMessages, currentCondition]);

  /** Resets all dialog state (call when switching conditions or views). */
  const resetDialog = useCallback(() => {
    setDialogMessages([]);
    setDialogInput('');
    setIsChatOpen(false);
  }, []);

  return {
    dialogMessages,
    dialogInput,
    setDialogInput,
    dialogLoading,
    isChatOpen,
    setIsChatOpen,
    messagesEndRef,
    handleSendDialog,
    resetDialog,
  };
}
