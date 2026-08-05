import React, { useEffect } from 'react';
import { Sidebar } from '../sidebar/Sidebar';
import { Header } from './Header';
import { ChatArea } from '../chat/ChatArea';
import { PinnedDrawer } from '../chat/PinnedDrawer';
import { SearchModal } from '../common/SearchModal';
import { SettingsModal } from '../common/SettingsModal';
import { SavedPromptsModal } from '../sidebar/SavedPromptsModal';
import { ExplorePage } from '../explore/ExplorePage';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { useSettingsStore } from '../../store/settingsStore';
import { useChatStore } from '../../store/chatStore';

export const MainLayout: React.FC = () => {
  useKeyboardShortcuts();
  const { theme } = useSettingsStore();
  const { exploreOpen, setExploreOpen, createNewConversation, setActiveConversation } = useChatStore();

  // Sync dark class on document root
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else if (theme === 'light') {
      root.classList.add('light');
      root.classList.remove('dark');
    } else {
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (systemDark) root.classList.add('dark');
      else root.classList.remove('dark');
    }
  }, [theme]);

  const handleExplorePrompt = (promptText: string) => {
    const id = createNewConversation();
    setActiveConversation(id);
    setExploreOpen(false);
    // Slight delay to let the chat area mount then dispatch
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('prox:send-prompt', { detail: { text: promptText } }));
    }, 100);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0d1117] text-slate-100 font-sans antialiased">
      {/* Collapsible Left Navigation Sidebar */}
      <Sidebar />

      {/* Main Content View */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {exploreOpen ? (
          <ExplorePage
            onSelectPrompt={handleExplorePrompt}
            onClose={() => setExploreOpen(false)}
          />
        ) : (
          <ChatArea />
        )}
      </div>

      {/* Slide-over Drawers & Overlay Modals */}
      <PinnedDrawer />
      <SearchModal />
      <SettingsModal />
      <SavedPromptsModal />
    </div>
  );
};


