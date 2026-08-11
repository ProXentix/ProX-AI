import { useEffect } from 'react';
import { useChatStore } from '../store/chatStore';

export function useKeyboardShortcuts() {
  const {
    setSearchModalOpen,
    createNewConversation,
    toggleSidebar,
    searchModalOpen,
    settingsModalOpen,
    savedPromptsModalOpen,
    setSettingsModalOpen,
    setSavedPromptsModalOpen,
  } = useChatStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCmdOrCtrl = e.metaKey || e.ctrlKey;

      // Cmd/Ctrl + K -> Search
      if (isCmdOrCtrl && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSearchModalOpen(!searchModalOpen);
        return;
      }

      // Cmd/Ctrl + Shift + O -> New Chat
      if (isCmdOrCtrl && e.shiftKey && e.key.toLowerCase() === 'o') {
        e.preventDefault();
        createNewConversation();
        return;
      }

      // Cmd/Ctrl + / -> Toggle Sidebar
      if (isCmdOrCtrl && e.key === '/') {
        e.preventDefault();
        toggleSidebar();
        return;
      }

      // Escape -> Close active modals
      if (e.key === 'Escape') {
        if (searchModalOpen) setSearchModalOpen(false);
        if (settingsModalOpen) setSettingsModalOpen(false);
        if (savedPromptsModalOpen) setSavedPromptsModalOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    searchModalOpen,
    settingsModalOpen,
    savedPromptsModalOpen,
    setSearchModalOpen,
    setSettingsModalOpen,
    setSavedPromptsModalOpen,
    createNewConversation,
    toggleSidebar,
  ]);
}
