import React, { useState } from 'react';
import { Plus, Trash2, BookOpen } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { useChatStore } from '../../store/chatStore';
import { Tooltip } from '../ui/Tooltip';

export const SavedPromptsModal: React.FC = () => {
  const { savedPromptsModalOpen, setSavedPromptsModalOpen, savedPrompts, addSavedPrompt, deleteSavedPrompt } = useChatStore();
  const [isAdding, setIsAdding] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState<'Coding' | 'Writing' | 'Analysis' | 'Productivity' | 'Custom'>('Custom');
  const [shortcut, setShortcut] = useState('');

  const handleCreatePrompt = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && content.trim()) {
      addSavedPrompt({
        title: title.trim(),
        content: content.trim(),
        category,
        shortcut: shortcut.trim() ? (shortcut.startsWith('/') ? shortcut : '/' + shortcut) : undefined,
        tags: [category.toLowerCase()],
      });
      setTitle('');
      setContent('');
      setShortcut('');
      setIsAdding(false);
    }
  };

  return (
    <Modal
      isOpen={savedPromptsModalOpen}
      onClose={() => setSavedPromptsModalOpen(false)}
      title={
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />
          <span>Saved Prompts Library</span>
        </div>
      }
      maxWidth="lg"
    >
      <div className="space-y-4">
        {isAdding ? (
          <form onSubmit={handleCreatePrompt} className="space-y-3 bg-zinc-50 p-4 rounded-xl border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800">
            <h4 className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">Create New Prompt Template</h4>
            <input
              type="text"
              placeholder="Prompt Title (e.g. Clean Code Refactor)"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-white text-zinc-900 text-xs p-2.5 rounded-lg border border-zinc-200 focus:outline-none focus:border-zinc-950 dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700"
              required
            />
            <textarea
              placeholder="Prompt Content Template..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={4}
              className="w-full bg-white text-zinc-900 text-xs p-2.5 rounded-lg border border-zinc-200 focus:outline-none focus:border-zinc-950 resize-y dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700"
              required
            />
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Shortcut e.g. /refactor"
                value={shortcut}
                onChange={(e) => setShortcut(e.target.value)}
                className="flex-1 bg-white text-zinc-900 text-xs p-2.5 rounded-lg border border-zinc-200 focus:outline-none focus:border-zinc-950 dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700"
              />
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as any)}
                className="bg-white text-zinc-900 text-xs p-2.5 rounded-lg border border-zinc-200 focus:outline-none dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-700"
              >
                <option value="Coding">Coding</option>
                <option value="Writing">Writing</option>
                <option value="Analysis">Analysis</option>
                <option value="Productivity">Productivity</option>
                <option value="Custom">Custom</option>
              </select>
            </div>
            <div className="flex justify-end gap-2 text-xs pt-2">
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="px-3 py-1.5 rounded-lg border border-zinc-200 hover:bg-zinc-100 text-zinc-700 dark:border-zinc-700 dark:text-zinc-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3 py-1.5 rounded-lg bg-zinc-950 hover:bg-black text-white font-medium dark:bg-white dark:text-zinc-950"
              >
                Save Prompt
              </button>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setIsAdding(true)}
            className="w-full flex items-center justify-center gap-2 p-2.5 rounded-xl border border-dashed border-zinc-300 hover:border-zinc-950 hover:bg-zinc-50 text-zinc-900 text-xs font-semibold transition-colors dark:border-zinc-700 dark:text-zinc-100"
          >
            <Plus className="w-4 h-4" />
            <span>Create Saved Prompt Template</span>
          </button>
        )}

        <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
          {savedPrompts.map((prompt) => (
            <div
              key={prompt.id}
              className="p-3 rounded-xl bg-white border border-zinc-200 text-xs space-y-1 group dark:bg-zinc-950 dark:border-zinc-800"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-zinc-900 dark:text-zinc-100">{prompt.title}</span>
                <div className="flex items-center gap-2">
                  {prompt.shortcut && (
                    <span className="text-[10px] font-mono text-zinc-900 bg-zinc-100 px-2 py-0.5 rounded border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700">
                      {prompt.shortcut}
                    </span>
                  )}
                  <Tooltip content="Delete Prompt" position="left">
                    <button
                      onClick={() => deleteSavedPrompt(prompt.id)}
                      className="p-1 text-zinc-400 hover:text-rose-600 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </Tooltip>
                </div>
              </div>
              <p className="text-[11px] text-zinc-600 leading-relaxed font-mono whitespace-pre-wrap dark:text-zinc-400">
                {prompt.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </Modal>
  );
};
