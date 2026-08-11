import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Pin, Bookmark } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { MarkdownRenderer } from '../common/MarkdownRenderer';

export const PinnedDrawer: React.FC = () => {
  const {
    pinnedDrawerOpen,
    togglePinnedDrawer,
    conversations,
    activeConversationId,
  } = useChatStore();

  const activeConv = conversations.find((c) => c.id === activeConversationId);
  const pinnedMessages = activeConv?.messages.filter((m) => m.isPinned) || [];

  return (
    <AnimatePresence>
      {pinnedDrawerOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={togglePinnedDrawer}
            className="fixed inset-0 bg-black/20 backdrop-blur-xs z-40"
          />

          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed right-0 top-0 bottom-0 w-80 sm:w-96 bg-white border-l border-zinc-200 shadow-xl z-50 flex flex-col dark:bg-zinc-900 dark:border-zinc-800"
          >
            <div className="flex items-center justify-between p-4 border-b border-zinc-200 dark:border-zinc-800">
              <div className="flex items-center gap-2 font-semibold text-zinc-900 text-sm dark:text-zinc-100">
                <Pin className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />
                <span>Pinned Items ({pinnedMessages.length})</span>
              </div>
              <button
                onClick={togglePinnedDrawer}
                className="p-1 rounded-lg text-zinc-400 hover:text-zinc-900 hover:bg-zinc-100 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {pinnedMessages.length === 0 ? (
                <div className="text-center py-12 text-zinc-400 space-y-2">
                  <Bookmark className="w-8 h-8 mx-auto text-zinc-300 dark:text-zinc-600" />
                  <p className="text-xs font-medium text-zinc-600 dark:text-zinc-400">No pinned messages yet.</p>
                  <p className="text-[11px] text-zinc-400">
                    Click the pin icon on any AI response toolbar to save key insights here.
                  </p>
                </div>
              ) : (
                pinnedMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 text-xs space-y-2 shadow-2xs dark:bg-zinc-950 dark:border-zinc-800"
                  >
                    <div className="flex items-center justify-between text-[11px] text-zinc-400">
                      <span className="font-semibold text-zinc-700 dark:text-zinc-300">{msg.role === 'assistant' ? 'AI Insight' : 'Your Note'}</span>
                      <span>{msg.timestamp}</span>
                    </div>
                    <MarkdownRenderer content={msg.content.slice(0, 240) + (msg.content.length > 240 ? '...' : '')} />
                  </div>
                ))
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
