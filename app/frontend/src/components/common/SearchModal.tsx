import React, { useState, useEffect, useRef } from 'react';
import { Search, MessageSquare, BookOpen, ArrowRight } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { useChatStore } from '../../store/chatStore';

export const SearchModal: React.FC = () => {
  const { searchModalOpen, setSearchModalOpen, conversations, savedPrompts, setActiveConversation } = useChatStore();
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (searchModalOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [searchModalOpen]);

  const filteredConversations = query.trim()
    ? conversations.filter(
        (c) =>
          c.title.toLowerCase().includes(query.toLowerCase()) ||
          c.messages.some((m) => m.content.toLowerCase().includes(query.toLowerCase()))
      )
    : conversations.slice(0, 5);

  const filteredPrompts = query.trim()
    ? savedPrompts.filter(
        (p) =>
          p.title.toLowerCase().includes(query.toLowerCase()) ||
          p.content.toLowerCase().includes(query.toLowerCase())
      )
    : savedPrompts.slice(0, 3);

  return (
    <Modal
      isOpen={searchModalOpen}
      onClose={() => setSearchModalOpen(false)}
      maxWidth="lg"
    >
      <div className="space-y-4">
        {/* Search Input Bar */}
        <div className="relative flex items-center">
          <Search className="w-4 h-4 absolute left-3.5 text-zinc-400" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search conversations, prompts, or messages... (Esc to close)"
            className="w-full bg-zinc-50 text-zinc-900 text-sm pl-10 pr-4 py-3 rounded-xl border border-zinc-200 focus:outline-none focus:border-zinc-950 font-sans dark:bg-zinc-950 dark:text-zinc-100 dark:border-zinc-800"
          />
        </div>

        {/* Results Sections */}
        <div className="space-y-4 max-h-96 overflow-y-auto pr-1">
          {/* Conversations Section */}
          <div>
            <div className="flex items-center gap-1.5 px-2 py-1 text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              <MessageSquare className="w-3.5 h-3.5 text-zinc-700 dark:text-zinc-300" />
              <span>Conversations ({filteredConversations.length})</span>
            </div>

            {filteredConversations.length === 0 ? (
              <p className="px-3 py-2 text-xs text-zinc-400 italic">No matching conversations found.</p>
            ) : (
              <div className="space-y-1 mt-1">
                {filteredConversations.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => {
                      setActiveConversation(c.id);
                      setSearchModalOpen(false);
                    }}
                    className="w-full flex items-center justify-between p-2.5 rounded-xl text-left bg-white hover:bg-zinc-100 border border-zinc-200 text-xs transition-colors group dark:bg-zinc-900 dark:border-zinc-800 dark:hover:bg-zinc-800"
                  >
                    <div className="min-w-0 flex-1">
                      <span className="font-semibold text-zinc-900 group-hover:text-black transition-colors block truncate dark:text-zinc-100">
                        {c.title}
                      </span>
                      <span className="text-[11px] text-zinc-400 font-mono">
                        {c.modelId} • {c.messages.length} messages
                      </span>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-950 group-hover:translate-x-0.5 transition-all ml-2 shrink-0 dark:group-hover:text-zinc-100" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Saved Prompts Section */}
          <div>
            <div className="flex items-center gap-1.5 px-2 py-1 text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              <BookOpen className="w-3.5 h-3.5 text-zinc-700 dark:text-zinc-300" />
              <span>Saved Prompts ({filteredPrompts.length})</span>
            </div>

            {filteredPrompts.length === 0 ? (
              <p className="px-3 py-2 text-xs text-zinc-400 italic">No matching prompts found.</p>
            ) : (
              <div className="space-y-1 mt-1">
                {filteredPrompts.map((p) => (
                  <div
                    key={p.id}
                    className="p-2.5 rounded-xl bg-white border border-zinc-200 text-xs space-y-1 dark:bg-zinc-900 dark:border-zinc-800"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-zinc-900 dark:text-zinc-100">{p.title}</span>
                      <span className="text-[10px] font-mono text-zinc-900 bg-zinc-100 px-2 py-0.5 rounded border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700">
                        {p.shortcut || p.category}
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-500 line-clamp-1 dark:text-zinc-400">{p.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};
