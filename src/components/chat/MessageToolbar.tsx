import React, { useState } from 'react';
import {
  Copy,
  Check,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  Volume2,
  VolumeX,
  Pin,
  Download,
  GitBranch,
} from 'lucide-react';
import { copyToClipboard } from '../../utils/formatters';
import { useSpeech } from '../../hooks/useSpeech';
import { useChatStore } from '../../store/chatStore';
import { Tooltip } from '../ui/Tooltip';

interface MessageToolbarProps {
  messageId: string;
  conversationId: string;
  content: string;
  rating?: 'like' | 'dislike' | null;
  isPinned?: boolean;
  onRetry?: () => void;
}

export const MessageToolbar: React.FC<MessageToolbarProps> = ({
  messageId,
  conversationId,
  content,
  rating,
  isPinned,
  onRetry,
}) => {
  const [copied, setCopied] = useState(false);
  const { speakingMessageId, speakText, stopSpeech } = useSpeech();
  const { updateMessage, createNewConversation } = useChatStore();

  const isSpeaking = speakingMessageId === messageId;

  const handleCopy = async () => {
    const success = await copyToClipboard(content);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRating = (nextRating: 'like' | 'dislike') => {
    const updated = rating === nextRating ? null : nextRating;
    updateMessage(conversationId, messageId, { rating: updated });
  };

  const handleTogglePin = () => {
    updateMessage(conversationId, messageId, { isPinned: !isPinned });
  };

  const handleAudioSpeech = () => {
    if (isSpeaking) {
      stopSpeech();
    } else {
      speakText(messageId, content);
    }
  };

  const handleBranchChat = () => {
    const newConvId = createNewConversation();
    alert(`Branched new thread from message. Conversation ID: ${newConvId}`);
  };

  const handleDownloadMd = () => {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `response-${messageId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center gap-1 mt-3 pt-2 border-t border-zinc-200 text-zinc-500 text-xs dark:border-zinc-800 dark:text-zinc-400">
      <Tooltip content="Copy response">
        <button
          onClick={handleCopy}
          className="p-1.5 rounded-lg hover:text-zinc-900 hover:bg-zinc-200/60 transition-colors dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-zinc-950 font-bold dark:text-zinc-100" /> : <Copy className="w-3.5 h-3.5" />}
        </button>
      </Tooltip>

      <Tooltip content={isSpeaking ? 'Stop reading' : 'Read aloud (TTS)'}>
        <button
          onClick={handleAudioSpeech}
          className={`p-1.5 rounded-lg transition-colors ${
            isSpeaking ? 'text-zinc-950 bg-zinc-200 font-bold dark:text-zinc-100 dark:bg-zinc-800' : 'hover:text-zinc-900 hover:bg-zinc-200/60 dark:hover:text-zinc-100 dark:hover:bg-zinc-800'
          }`}
        >
          {isSpeaking ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
        </button>
      </Tooltip>

      {onRetry && (
        <Tooltip content="Regenerate response">
          <button
            onClick={onRetry}
            className="p-1.5 rounded-lg hover:text-zinc-900 hover:bg-zinc-200/60 transition-colors dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </Tooltip>
      )}

      <Tooltip content="Good response">
        <button
          onClick={() => handleRating('like')}
          className={`p-1.5 rounded-lg transition-colors ${
            rating === 'like' ? 'text-zinc-950 bg-zinc-200 font-bold dark:text-zinc-100 dark:bg-zinc-800' : 'hover:text-zinc-900 hover:bg-zinc-200/60 dark:hover:text-zinc-100 dark:hover:bg-zinc-800'
          }`}
        >
          <ThumbsUp className="w-3.5 h-3.5" />
        </button>
      </Tooltip>

      <Tooltip content="Bad response">
        <button
          onClick={() => handleRating('dislike')}
          className={`p-1.5 rounded-lg transition-colors ${
            rating === 'dislike' ? 'text-rose-600 bg-rose-50 font-bold dark:text-rose-400 dark:bg-rose-950/40' : 'hover:text-zinc-900 hover:bg-zinc-200/60 dark:hover:text-zinc-100 dark:hover:bg-zinc-800'
          }`}
        >
          <ThumbsDown className="w-3.5 h-3.5" />
        </button>
      </Tooltip>

      <Tooltip content={isPinned ? 'Unpin message' : 'Pin message'}>
        <button
          onClick={handleTogglePin}
          className={`p-1.5 rounded-lg transition-colors ${
            isPinned ? 'text-zinc-950 bg-zinc-200 font-bold dark:text-zinc-100 dark:bg-zinc-800' : 'hover:text-zinc-900 hover:bg-zinc-200/60 dark:hover:text-zinc-100 dark:hover:bg-zinc-800'
          }`}
        >
          <Pin className="w-3.5 h-3.5" />
        </button>
      </Tooltip>

      <Tooltip content="Branch new thread">
        <button
          onClick={handleBranchChat}
          className="p-1.5 rounded-lg hover:text-zinc-900 hover:bg-zinc-200/60 transition-colors dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
        >
          <GitBranch className="w-3.5 h-3.5" />
        </button>
      </Tooltip>

      <Tooltip content="Download Markdown">
        <button
          onClick={handleDownloadMd}
          className="p-1.5 rounded-lg hover:text-zinc-900 hover:bg-zinc-200/60 transition-colors ml-auto dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
        >
          <Download className="w-3.5 h-3.5" />
        </button>
      </Tooltip>
    </div>
  );
};
