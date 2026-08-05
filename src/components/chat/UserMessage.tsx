import React, { useState } from 'react';
import { Edit2, Check, X, User, Paperclip } from 'lucide-react';
import { Message } from '../../types/chat';
import { useChatStore } from '../../store/chatStore';
import { Tooltip } from '../ui/Tooltip';

interface UserMessageProps {
  message: Message;
}

export const UserMessage: React.FC<UserMessageProps> = ({ message }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(message.content);
  const { updateMessageContent } = useChatStore();

  const handleSaveEdit = () => {
    if (editedText.trim()) {
      updateMessageContent(message.conversationId, message.id, editedText);
      setIsEditing(false);
    }
  };

  return (
    <div className="flex justify-end my-4 group">
      <div className="max-w-[85%] sm:max-w-[75%] space-y-1">
        <div className="flex items-center justify-end gap-2 text-xs text-zinc-400 mb-1">
          <span className="text-[11px]">{message.timestamp}</span>
          <span className="font-semibold text-zinc-700 dark:text-zinc-300">You</span>
          <span className="p-1 rounded-full bg-zinc-200 text-zinc-900 border border-zinc-300 dark:bg-zinc-800 dark:text-zinc-100 dark:border-zinc-700">
            <User className="w-3 h-3" />
          </span>
        </div>

        {isEditing ? (
          <div className="p-3 bg-white border border-zinc-300 rounded-2xl space-y-2 shadow-lg dark:bg-zinc-900 dark:border-zinc-700">
            <textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              className="w-full bg-zinc-50 text-zinc-900 text-sm p-2.5 rounded-xl border border-zinc-200 focus:outline-none focus:border-zinc-900 min-h-24 resize-y dark:bg-zinc-950 dark:text-zinc-100 dark:border-zinc-800"
            />
            <div className="flex justify-end gap-2 text-xs">
              <button
                onClick={() => setIsEditing(false)}
                className="px-3 py-1.5 rounded-lg border border-zinc-200 hover:bg-zinc-100 text-zinc-700"
              >
                <X className="w-3.5 h-3.5" /> Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-3 py-1.5 rounded-lg bg-zinc-950 hover:bg-black text-white font-medium flex items-center gap-1 dark:bg-white dark:text-zinc-950"
              >
                <Check className="w-3.5 h-3.5" /> Save & Submit
              </button>
            </div>
          </div>
        ) : (
          <div className="relative p-4 rounded-2xl bg-zinc-950 text-white shadow-xs border border-zinc-800 dark:bg-white dark:text-zinc-950 dark:border-zinc-200">
            {message.attachments && message.attachments.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {message.attachments.map((att) => (
                  <div
                    key={att.id}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-800 border border-zinc-700 text-xs font-medium dark:bg-zinc-200 dark:border-zinc-300"
                  >
                    <Paperclip className="w-3 h-3" />
                    <span>{att.name}</span>
                  </div>
                ))}
              </div>
            )}

            <p className="text-sm leading-relaxed whitespace-pre-wrap font-sans">{message.content}</p>

            <Tooltip content="Edit Prompt" position="left">
              <button
                onClick={() => setIsEditing(true)}
                className="absolute top-2 right-2 p-1.5 rounded-lg text-white/60 hover:text-white transition-colors opacity-0 group-hover:opacity-100 dark:text-zinc-500 dark:hover:text-zinc-900"
              >
                <Edit2 className="w-3.5 h-3.5" />
              </button>
            </Tooltip>
          </div>
        )}
      </div>
    </div>
  );
};
