import React, { useState } from 'react';
import {
  PanelLeft,
  Share2,
  Download,
  Pin,
  Check,
} from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { ModelSelector } from '../ui/ModelSelector';
import { ThemeToggle } from '../ui/ThemeToggle';

export const Header: React.FC = () => {
  const {
    sidebarOpen,
    toggleSidebar,
    conversations,
    activeConversationId,
    renameConversation,
    togglePinnedDrawer,
  } = useChatStore();

  const activeConv = conversations.find((c) => c.id === activeConversationId);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [title, setTitle] = useState(activeConv?.title || '');
  const [copiedShareLink, setCopiedShareLink] = useState(false);

  const handleTitleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeConv && title.trim()) {
      renameConversation(activeConv.id, title.trim());
      setIsEditingTitle(false);
    }
  };

  const handleShare = () => {
    setCopiedShareLink(true);
    setTimeout(() => setCopiedShareLink(false), 2500);
  };

  const handleExportJson = () => {
    if (!activeConv) return;
    const blob = new Blob([JSON.stringify(activeConv, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${activeConv.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <header className="h-14 bg-white/90 border-b border-zinc-200 px-4 flex items-center justify-between sticky top-0 z-20 backdrop-blur-md dark:bg-zinc-900/90 dark:border-zinc-800">
      <div className="flex items-center gap-3 min-w-0">
        {/* Toggle Sidebar Button */}
        {!sidebarOpen && (
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-xl text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 transition-colors dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
            title="Expand Sidebar (Ctrl+/)"
          >
            <PanelLeft className="w-4 h-4" />
          </button>
        )}

        {/* Model Selector Pill */}
        <ModelSelector />

        {/* Active Conversation Title */}
        {activeConv && (
          <div className="hidden md:flex items-center gap-2 min-w-0">
            <span className="text-zinc-300 dark:text-zinc-700">•</span>
            {isEditingTitle ? (
              <form onSubmit={handleTitleSubmit} className="flex items-center gap-1">
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  onBlur={handleTitleSubmit}
                  className="bg-white text-zinc-900 text-xs px-2 py-1 rounded border border-zinc-900 font-semibold focus:outline-none dark:bg-zinc-950 dark:text-zinc-100 dark:border-zinc-100"
                  autoFocus
                />
              </form>
            ) : (
              <span
                onClick={() => {
                  setTitle(activeConv.title);
                  setIsEditingTitle(true);
                }}
                className="text-xs font-semibold text-zinc-800 hover:text-zinc-950 cursor-pointer truncate max-w-xs transition-colors dark:text-zinc-200 dark:hover:text-white"
                title="Click to rename"
              >
                {activeConv.title}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Right Header Actions */}
      <div className="flex items-center gap-2">
        {/* Pinned Drawer Button */}
        <button
          onClick={togglePinnedDrawer}
          className="p-2 rounded-xl text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 transition-colors dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
          title="View Pinned Notes"
        >
          <Pin className="w-4 h-4" />
        </button>

        {/* Share Button */}
        <button
          onClick={handleShare}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-black text-white text-xs font-medium transition-all shadow-xs dark:bg-zinc-100 dark:hover:bg-white dark:text-zinc-950"
          title="Share Conversation"
        >
          {copiedShareLink ? (
            <>
              <Check className="w-3.5 h-3.5 text-white dark:text-zinc-950" />
              <span className="font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <Share2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Share</span>
            </>
          )}
        </button>

        {/* Export JSON Button */}
        <button
          onClick={handleExportJson}
          className="p-2 rounded-xl text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 transition-colors hidden sm:flex dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
          title="Export Conversation JSON"
        >
          <Download className="w-4 h-4" />
        </button>

        {/* Theme Toggle */}
        <ThemeToggle />
      </div>
    </header>
  );
};
