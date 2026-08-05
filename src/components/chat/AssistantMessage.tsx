import React from 'react';
import { Bot, AlertCircle } from 'lucide-react';
import { Message } from '../../types/chat';
import { ReasoningBlock } from './ReasoningBlock';
import { CitationsBlock } from './CitationsBlock';
import { MarkdownRenderer } from '../common/MarkdownRenderer';
import { MessageToolbar } from './MessageToolbar';

interface AssistantMessageProps {
  message: Message;
  onRetry?: () => void;
}

export const AssistantMessage: React.FC<AssistantMessageProps> = ({ message, onRetry }) => {
  return (
    <div className="flex gap-3 my-5 group">
      {/* Assistant Avatar */}
      <div className="shrink-0">
        <div className="w-8 h-8 rounded-xl bg-zinc-950 text-white flex items-center justify-center shadow-xs border border-zinc-800 mt-0.5 dark:bg-white dark:text-zinc-950 dark:border-zinc-200">
          <Bot className="w-4.5 h-4.5" />
        </div>
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        {/* Header line */}
        <div className="flex items-center gap-2 text-xs">
          <span className="font-bold text-zinc-900 dark:text-zinc-100">ProX AI</span>
          {message.modelId && (
            <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-zinc-100 text-zinc-800 border border-zinc-200 uppercase tracking-wider dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700">
              {message.modelId}
            </span>
          )}
          <span className="text-[11px] text-zinc-400 ml-auto">{message.timestamp}</span>
        </div>

        {/* Card Frame */}
        <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 shadow-2xs relative overflow-hidden dark:bg-zinc-900/80 dark:border-zinc-800">
          {message.isError && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 text-xs mb-3">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>Failed to generate response. Please try again.</span>
            </div>
          )}

          {/* Reasoning Steps Accordion */}
          {message.reasoning && message.reasoning.steps.length > 0 && (
            <ReasoningBlock reasoning={message.reasoning} />
          )}

          {/* Citations List */}
          {message.citations && message.citations.length > 0 && (
            <CitationsBlock citations={message.citations} />
          )}

          {/* Markdown Content */}
          <MarkdownRenderer content={message.content} />

          {/* Streaming Cursor pulse */}
          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-zinc-900 animate-pulse rounded-xs align-middle dark:bg-zinc-100" />
          )}

          {/* Toolbar Actions */}
          {!message.isStreaming && (
            <MessageToolbar
              messageId={message.id}
              conversationId={message.conversationId}
              content={message.content}
              rating={message.rating}
              isPinned={message.isPinned}
              onRetry={onRetry}
            />
          )}
        </div>
      </div>
    </div>
  );
};
