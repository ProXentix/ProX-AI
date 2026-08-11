import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  SquarePen,
  Search,
  BookOpen,
  Folder,
  FolderPlus,
  Bot,
  PanelLeftClose,
  Compass,
} from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { ConversationItem } from './ConversationItem';
import { UserProfile } from './UserProfile';
import { groupConversationsByDate } from '../../utils/formatters';
import { Tooltip } from '../ui/Tooltip';
import { Modal } from '../ui/Modal';
import { ModelSelector } from '../ui/ModelSelector';
import { toast } from 'sonner';

export const Sidebar: React.FC = () => {
  const {
    sidebarOpen,
    toggleSidebar,
    conversations,
    createNewConversation,
    setSearchModalOpen,
    setSavedPromptsModalOpen,
    setSettingsModalOpen,
    setExploreOpen,
    setAgentsPageOpen,
    setProjectsOpen,
    folders,
    addFolder,
  } = useChatStore();
  
  const [showProjects, setShowProjects] = useState(false);
  const [createFolderModalOpen, setCreateFolderModalOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  const grouped = groupConversationsByDate(conversations);

  const handleConfirmCreateFolder = (e: React.FormEvent) => {
    e.preventDefault();
    if (newFolderName.trim()) {
      addFolder(newFolderName.trim());
      toast.success(`Project Folder "${newFolderName.trim()}" created!`);
      setNewFolderName('');
      setCreateFolderModalOpen(false);
    }
  };

  const closeMobile = () => {
    if (window.innerWidth < 768 && sidebarOpen) {
      toggleSidebar();
    }
  };

  return (
    <>
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <>
            {/* Mobile Backdrop Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={toggleSidebar}
              className="fixed inset-0 bg-black/60 z-30 md:hidden backdrop-blur-xs"
            />

            <motion.aside
              initial={{ x: -280, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -280, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 350, damping: 30 }}
              className="fixed inset-y-0 left-0 z-40 md:relative md:z-auto w-[280px] sm:w-72 md:w-64 bg-zinc-50 border-r border-zinc-200/80 flex flex-col h-screen shrink-0 select-none font-sans dark:bg-zinc-900 dark:border-zinc-800 shadow-xl md:shadow-none"
            >
            {/* Top Header Row: Logo & Action Icons */}
            <div className="flex items-center justify-between px-3.5 pt-3 pb-2">
              <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => createNewConversation()}>
                <img
                  src="/prox-ai-logo.png"
                  alt="ProX AI"
                  className="w-8 h-8 rounded-lg object-contain"
                />
                <span className="font-extrabold text-zinc-900 text-base tracking-tight dark:text-zinc-100">
                  ProX AI
                </span>
              </div>

              <div className="flex items-center gap-1">
                <Tooltip content="Search history (Ctrl+K)" position="bottom">
                  <button
                    onClick={() => setSearchModalOpen(true)}
                    className="p-1.5 rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-200/60 transition-colors dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
                  >
                    <Search className="w-4 h-4" />
                  </button>
                </Tooltip>
                <Tooltip content="Close Sidebar (Ctrl+/)" position="bottom">
                  <button
                    onClick={toggleSidebar}
                    className="p-1.5 rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-200/60 transition-colors dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
                  >
                    <PanelLeftClose className="w-4 h-4" />
                  </button>
                </Tooltip>
              </div>
            </div>

            {/* New Chat Button */}
            <div className="px-3 py-1.5">
              <button
                onClick={() => {
                  createNewConversation();
                  closeMobile();
                }}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-blue-600 text-white font-semibold text-xs hover:bg-blue-700 shadow-sm transition-all dark:bg-blue-600 dark:hover:bg-blue-500"
              >
                <div className="flex items-center gap-2">
                  <SquarePen className="w-3.5 h-3.5" />
                  <span>New Chat</span>
                </div>
                <span className="text-[10px] opacity-80 font-mono">⌘N</span>
              </button>
            </div>

            {/* Navigation Options List */}
            <div className="px-2 py-1 space-y-0.5">
              {/* Explore Button */}
              <button
                onClick={() => {
                  setExploreOpen(true);
                  closeMobile();
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-zinc-700 hover:bg-zinc-200/60 transition-colors dark:text-zinc-300 dark:hover:bg-zinc-800/70"
              >
                <Compass className="w-4 h-4 text-blue-500 dark:text-blue-400" />
                <span className="text-sm">Explore</span>
                <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400 font-medium border border-blue-200 dark:border-blue-800/50">New</span>
              </button>

              {/* Library Button */}
              <button
                onClick={() => {
                  setSavedPromptsModalOpen(true);
                  closeMobile();
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-zinc-700 hover:bg-zinc-200/60 transition-colors dark:text-zinc-300 dark:hover:bg-zinc-800/70"
              >
                <BookOpen className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                <span className="text-sm">Library</span>
              </button>

              {/* Projects Toggle & Create Folder */}
              <div className="space-y-0.5">
                <div className="flex items-center justify-between px-3 py-2 rounded-xl hover:bg-zinc-200/60 transition-colors dark:hover:bg-zinc-800/70 text-zinc-700 dark:text-zinc-300">
                  <button
                    onClick={() => {
                      setProjectsOpen(true);
                      closeMobile();
                    }}
                    className="flex items-center gap-2.5 flex-1"
                  >
                    <Folder className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                    <span className="text-sm">Projects</span>
                  </button>
                  <Tooltip content="New Project Folder">
                    <button
                      onClick={() => setCreateFolderModalOpen(true)}
                      className="p-1 rounded-lg hover:bg-zinc-300/60 dark:hover:bg-zinc-700 text-zinc-500 dark:text-zinc-400"
                    >
                      <FolderPlus className="w-3.5 h-3.5" />
                    </button>
                  </Tooltip>
                </div>

                {/* Expanded Folder List */}
                {showProjects && folders && (
                  <div className="pl-8 pr-2 space-y-1 py-1">
                    {folders.length === 0 ? (
                      <span className="text-xs text-zinc-400 italic">No folders created</span>
                    ) : (
                      folders.map((f) => {
                        const count = conversations.filter((c) => c.folderId === f.id).length;
                        return (
                          <div
                            key={f.id}
                            className="flex items-center justify-between px-2 py-1 rounded-lg hover:bg-zinc-200/50 dark:hover:bg-zinc-800 text-xs text-zinc-600 dark:text-zinc-400"
                          >
                            <span className="truncate">{f.name}</span>
                            <span className="text-[10px] text-zinc-400 font-mono">({count})</span>
                          </div>
                        );
                      })
                    )}
                  </div>
                )}
              </div>

              {/* Custom Agents Option */}
              <button
                onClick={() => {
                  setAgentsPageOpen(true);
                  closeMobile();
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-zinc-700 hover:bg-zinc-200/60 transition-colors dark:text-zinc-300 dark:hover:bg-zinc-800/70"
              >
                <Bot className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
                <span className="text-sm">Agents</span>
              </button>
            </div>

            {/* Section Header: Recents */}
            <div className="px-3.5 pt-3 pb-1">
              <span className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">
                Recents
              </span>
            </div>

            {/* Scrollable Recents List */}
            <div className="flex-1 overflow-y-auto px-2 space-y-0.5 py-1">
              {Object.entries(grouped).map(([groupName, items]) => {
                if (items.length === 0) return null;
                return items.map((c) => (
                  <ConversationItem key={c.id} conversation={c} />
                ));
              })}
            </div>

            {/* User Profile Card */}
            <UserProfile />
          </motion.aside>
        </>
      )}
    </AnimatePresence>

      {/* CREATE PROJECT FOLDER MODAL */}
      <Modal
        isOpen={createFolderModalOpen}
        onClose={() => setCreateFolderModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <FolderPlus className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Create New Project Folder</span>
          </div>
        }
        maxWidth="sm"
      >
        <form onSubmit={handleConfirmCreateFolder} className="space-y-4 text-xs">
          <p className="text-zinc-500 dark:text-zinc-400">
            Organize your conversations and prompts into a dedicated project workspace.
          </p>

          <div>
            <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
              Folder Name
            </label>
            <input
              type="text"
              placeholder="e.g. ProX AI Mobile App, Frontend Refactor, Python Server..."
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
              autoFocus
              required
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setCreateFolderModalOpen(false)}
              className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs"
            >
              <FolderPlus className="w-3.5 h-3.5" />
              <span>Create Folder</span>
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
};
