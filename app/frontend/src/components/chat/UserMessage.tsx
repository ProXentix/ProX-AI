import React, { useState } from 'react';
import { Pencil, Check, User, Paperclip, Copy, Share2 } from 'lucide-react';
import { Message } from '../../types/chat';
import { useChatStore } from '../../store/chatStore';
import { Tooltip } from '../ui/Tooltip';
import { copyToClipboard } from '../../utils/formatters';
import { toast } from 'sonner';

interface UserMessageProps {
  message: Message;
}

export const UserMessage: React.FC<UserMessageProps> = ({ message }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(message.content);
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);

  const { updateMessageContent } = useChatStore();

  const handleSaveEdit = () => {
    if (editedText.trim()) {
      updateMessageContent(message.conversationId, message.id, editedText);
      setIsEditing(false);
    }
  };

  const handleCopy = async () => {
    const success = await copyToClipboard(message.content);
    if (success) {
      setCopied(true);
      toast.success('Prompt copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleShare = async () => {
    const success = await copyToClipboard(message.content);
    if (success) {
      setShared(true);
      toast.success('Prompt link copied!');
      setTimeout(() => setShared(false), 2000);
    }
  };

  return (
    <div className="flex justify-end my-4 group w-full">
      <div className={`space-y-1 transition-all ${isEditing ? 'w-full pl-11' : 'max-w-[85%] sm:max-w-[75%]'}`}>
        <div className="flex items-center justify-end gap-2 text-xs text-zinc-400 mb-1">
          <span className="text-[11px]">{message.timestamp}</span>
          <span className="font-semibold text-zinc-700 dark:text-zinc-300">You</span>
          <span className="p-1 rounded-full bg-zinc-200 text-zinc-900 border border-zinc-300 dark:bg-zinc-800 dark:text-zinc-100 dark:border-zinc-700">
            <User className="w-3 h-3" />
          </span>
        </div>

        {isEditing ? (
          <div className="p-4 bg-[#F4F4F6] border border-zinc-200/80 rounded-3xl space-y-3 shadow-xs dark:bg-zinc-900 dark:border-zinc-800">
            <textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              className="w-full bg-transparent text-zinc-900 text-sm focus:outline-none resize-none min-h-[60px] leading-relaxed font-sans dark:text-zinc-100"
              autoFocus
            />
            <div className="flex justify-end items-center gap-2 text-xs pt-1">
              <button
                type="button"
                onClick={() => {
                  setEditedText(message.content);
                  setIsEditing(false);
                }}
                className="px-4 py-1.5 rounded-full bg-white hover:bg-zinc-100 text-zinc-900 font-medium border border-zinc-200/80 shadow-2xs transition-all dark:bg-zinc-800 dark:text-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-700"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveEdit}
                className="px-4 py-1.5 rounded-full bg-zinc-950 hover:bg-black text-white font-medium shadow-2xs transition-all dark:bg-white dark:text-zinc-950 dark:hover:bg-zinc-100"
              >
                Send
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div className="relative p-4 rounded-2xl bg-[#F4F4F6] text-zinc-900 font-medium border border-zinc-200/80 shadow-2xs dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-800">
              {message.attachments && message.attachments.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {message.attachments.map((att) => (
                    <div
                      key={att.id}
                      className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-zinc-200 text-xs font-medium text-zinc-800 dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-200"
                    >
                      <Paperclip className="w-3 h-3" />
                      <span>{att.name}</span>
                    </div>
                  ))}
                </div>
              )}

              <p className="text-sm leading-relaxed whitespace-pre-wrap font-sans">{message.content}</p>
            </div>

            {/* Options Bar: Copy, Share, Edit */}
            <div className="flex items-center justify-end gap-1 pt-1 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity select-none">
              {/* Copy */}
              <Tooltip content="Copy prompt text" position="bottom">
                <button
                  onClick={handleCopy}
                  className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-800 hover:bg-zinc-100 transition-colors dark:text-zinc-500 dark:hover:text-zinc-200 dark:hover:bg-zinc-800"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </Tooltip>

              {/* Share */}
              <Tooltip content="Share prompt" position="bottom">
                <button
                  onClick={handleShare}
                  className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-800 hover:bg-zinc-100 transition-colors dark:text-zinc-500 dark:hover:text-zinc-200 dark:hover:bg-zinc-800"
                >
                  {shared ? <Check className="w-3.5 h-3.5 text-blue-500" /> : <Share2 className="w-3.5 h-3.5" />}
                </button>
              </Tooltip>

              {/* Edit */}
              <Tooltip content="Edit prompt" position="bottom">
                <button
                  onClick={() => setIsEditing(true)}
                  className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-800 hover:bg-zinc-100 transition-colors dark:text-zinc-500 dark:hover:text-zinc-200 dark:hover:bg-zinc-800"
                >
                  <Pencil className="w-3.5 h-3.5" />
                </button>
              </Tooltip>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

