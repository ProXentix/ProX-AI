import React, { useEffect } from 'react';
import { Sidebar } from '../sidebar/Sidebar';
import { ChatArea } from '../chat/ChatArea';
import { PinnedDrawer } from '../chat/PinnedDrawer';
import { SearchModal } from '../common/SearchModal';
import { SettingsModal } from '../common/SettingsModal';
import { SavedPromptsModal } from '../sidebar/SavedPromptsModal';
import { ExplorePage } from '../explore/ExplorePage';
import { AgentsPage } from '../agents/AgentsPage';
import { ProjectsPage } from '../projects/ProjectsPage';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { useSettingsStore } from '../../store/settingsStore';
import { useChatStore } from '../../store/chatStore';
import { AIAgent } from '../../types/chat';

export const MainLayout: React.FC = () => {
  useKeyboardShortcuts();
  const { theme } = useSettingsStore();
  const {
    exploreOpen,
    setExploreOpen,
    agentsPageOpen,
    setAgentsPageOpen,
    projectsOpen,
    setProjectsOpen,
    createNewConversation,
    setActiveConversation,
    setActiveModel,
  } = useChatStore();

  // Sync dark class on document root
  useEffect(() => {
    const root = document.documentElement;

    const applyTheme = () => {
      if (theme === 'dark') {
        root.classList.add('dark');
        root.classList.remove('light');
      } else if (theme === 'light') {
        root.classList.add('light');
        root.classList.remove('dark');
      } else {
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (systemDark) {
          root.classList.add('dark');
          root.classList.remove('light');
        } else {
          root.classList.add('light');
          root.classList.remove('dark');
        }
      }
    };

    applyTheme();

    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => applyTheme();
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
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

  const handleLaunchAgent = (agent: AIAgent, promptText?: string) => {
    const id = createNewConversation();
    setActiveConversation(id);
    setActiveModel(agent.modelId);
    setAgentsPageOpen(false);
    if (promptText) {
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('prox:send-prompt', { detail: { text: promptText } }));
      }, 100);
    }
  };

  const handleStartChatInProject = (projectId: string, initialPrompt?: string) => {
    const id = createNewConversation(projectId);
    setActiveConversation(id);
    setProjectsOpen(false);
    if (initialPrompt) {
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('prox:send-prompt', { detail: { text: initialPrompt } }));
      }, 100);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-white text-zinc-900 dark:bg-[#0d1117] dark:text-slate-100 font-sans antialiased transition-colors duration-200">
      {/* Collapsible Left Navigation Sidebar */}
      <Sidebar />

      {/* Main Content View */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {exploreOpen ? (
          <ExplorePage
            onSelectPrompt={handleExplorePrompt}
            onClose={() => setExploreOpen(false)}
          />
        ) : agentsPageOpen ? (
          <AgentsPage
            onLaunchAgent={handleLaunchAgent}
            onClose={() => setAgentsPageOpen(false)}
          />
        ) : projectsOpen ? (
          <ProjectsPage
            onStartChatInProject={handleStartChatInProject}
            onClose={() => setProjectsOpen(false)}
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


