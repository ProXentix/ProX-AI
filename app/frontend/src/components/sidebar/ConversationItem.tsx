import React, { useState } from 'react';
import { Edit3, Trash2, Check, X, AlertTriangle } from 'lucide-react';
import { Conversation } from '../../types/chat';
import { useChatStore } from '../../store/chatStore';
import { Tooltip } from '../ui/Tooltip';
import { Modal } from '../ui/Modal';
import { toast } from 'sonner';

interface ConversationItemProps {
  conversation: Conversation;
}

export const ConversationItem: React.FC<ConversationItemProps> = ({ conversation }) => {
  const {
    activeConversationId,
    setActiveConversation,
    deleteConversation,
    renameConversation,
  } = useChatStore();

  const [isEditing, setIsEditing] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [title, setTitle] = useState(conversation.title);

  const isActive = conversation.id === activeConversationId;

  const handleSaveRename = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      renameConversation(conversation.id, title.trim());
      setIsEditing(false);
      toast.success('Chat title updated!');
    }
  };

  const handleConfirmDelete = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    deleteConversation(conversation.id);
    setDeleteModalOpen(false);
    toast.success('Chat deleted');
  };

  return (
    <>
      <div
        className={`group relative flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm transition-all duration-150 cursor-pointer ${
          isActive
            ? 'bg-zinc-200/80 text-zinc-950 font-semibold shadow-2xs dark:bg-zinc-800 dark:text-zinc-100'
            : 'text-zinc-800 hover:bg-zinc-200/50 dark:text-zinc-200 dark:hover:bg-zinc-800/60'
        }`}
        onClick={() => {
          if (!isEditing) setActiveConversation(conversation.id);
        }}
      >
        {isEditing ? (
          <form onSubmit={handleSaveRename} className="flex items-center gap-1 flex-1 min-w-0">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-white text-zinc-950 text-xs px-2 py-1 rounded border border-zinc-900 focus:outline-none dark:bg-zinc-950 dark:text-zinc-100 dark:border-zinc-100"
              autoFocus
            />
            <button type="submit" className="text-zinc-900 p-0.5 hover:text-black dark:text-zinc-100">
              <Check className="w-3.5 h-3.5" />
            </button>
            <button type="button" onClick={() => setIsEditing(false)} className="text-zinc-400 p-0.5 hover:text-zinc-700">
              <X className="w-3.5 h-3.5" />
            </button>
          </form>
        ) : (
          <span className="truncate flex-1">{conversation.title}</span>
        )}

        {!isEditing && (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Tooltip content="Rename" position="top">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                }}
                className="p-1 rounded text-zinc-400 hover:text-zinc-900 hover:bg-zinc-300/60 dark:hover:text-white dark:hover:bg-zinc-700"
              >
                <Edit3 className="w-3 h-3" />
              </button>
            </Tooltip>

            <Tooltip content="Delete" position="top">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setDeleteModalOpen(true);
                }}
                className="p-1 rounded text-zinc-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:text-rose-400 dark:hover:bg-rose-950/40"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </Tooltip>
          </div>
        )}
      </div>

      {/* DELETE CHAT CONFIRMATION MODAL (WITH ENTER KEY FORM SUBMISSION & AUTOFOCUS) */}
      {deleteModalOpen && (
        <Modal
          isOpen={deleteModalOpen}
          onClose={() => setDeleteModalOpen(false)}
          title={
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span>Delete Chat</span>
            </div>
          }
          maxWidth="sm"
        >
          <form onSubmit={handleConfirmDelete} className="space-y-4 text-xs">
            <p className="text-zinc-700 dark:text-zinc-300">
              Are you sure you want to delete <strong className="text-zinc-900 dark:text-zinc-100 font-semibold">"{conversation.title}"</strong>?
            </p>
            <p className="text-zinc-500 dark:text-zinc-400 text-[11px]">
              This will permanently delete this conversation and all associated messages. Press <kbd className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 font-mono font-bold">Enter ↵</kbd> to confirm.
            </p>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setDeleteModalOpen(false)}
                className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                autoFocus
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold shadow-xs focus:ring-2 focus:ring-red-500 focus:outline-none"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Delete Chat</span>
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
};
