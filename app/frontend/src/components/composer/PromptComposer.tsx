import React, { useState, useRef, useEffect } from 'react';
import { Send, Square, Globe, X } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { FileUploader } from './FileUploader';
import { VoiceInput } from './VoiceInput';
import { SlashCommands, SlashCommand } from './SlashCommands';
import { Tooltip } from '../ui/Tooltip';
import { Attachment } from '../../types/chat';

interface PromptComposerProps {
  onSendMessage: (text: string, attachments: Attachment[]) => void;
  onStopGeneration?: () => void;
  isStreaming?: boolean;
}

export const PromptComposer: React.FC<PromptComposerProps> = ({
  onSendMessage,
  onStopGeneration,
  isStreaming,
}) => {
  const [text, setText] = useState('');
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashFilter, setSlashFilter] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { webSearchEnabled, toggleWebSearch } = useChatStore();

  // Auto-resize textarea height dynamically
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setText(val);

    if (val.startsWith('/')) {
      setShowSlashMenu(true);
      setSlashFilter(val);
    } else {
      setShowSlashMenu(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if ((text.trim() || attachments.length > 0) && !isStreaming) {
      onSendMessage(text.trim(), attachments);
      setText('');
      setAttachments([]);
      setShowSlashMenu(false);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleSelectSlashCommand = (cmd: SlashCommand) => {
    setText(cmd.template);
    setShowSlashMenu(false);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto px-4 pb-4">
      {/* Slash Commands Popup */}
      {showSlashMenu && (
        <SlashCommands onSelect={handleSelectSlashCommand} filter={slashFilter} />
      )}

      {/* Main Glassmorphic Composer Frame */}
      <div className="relative bg-white border border-zinc-300 rounded-2xl shadow-xl backdrop-blur-md focus-within:border-[#4285f4] focus-within:ring-1 focus-within:ring-[#4285f4] transition-all dark:bg-zinc-900 dark:border-zinc-700 dark:focus-within:border-[#4285f4]">
        {/* Attachment Chips Bar */}
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 p-3 border-b border-zinc-200 dark:border-zinc-800">
            {attachments.map((att) => (
              <div
                key={att.id}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-zinc-100 border border-zinc-200 text-xs text-zinc-800 font-medium dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-200"
              >
                <span>{att.name}</span>
                <button
                  type="button"
                  onClick={() => setAttachments(attachments.filter((a) => a.id !== att.id))}
                  className="text-zinc-400 hover:text-zinc-900 ml-1 dark:hover:text-white"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Text Input Area */}
        <div className="p-3">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask ProX AI anything... (or type '/' for commands)"
            className="w-full bg-transparent text-zinc-900 placeholder-zinc-400 text-sm focus:outline-none resize-none max-h-48 leading-relaxed font-sans dark:text-zinc-100 dark:placeholder-zinc-500"
          />
        </div>

        {/* Bottom Toolbar & Action Bar */}
        <div className="flex items-center justify-between px-3 py-2 border-t border-zinc-100 text-xs text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
          <div className="flex items-center gap-1">
            {/* File Upload & Attachment Popover Menu */}
            <FileUploader
              attachments={attachments}
              onAddAttachment={(att) => setAttachments((prev) => [...prev, att])}
              onRemoveAttachment={(id) => setAttachments((prev) => prev.filter((a) => a.id !== id))}
              onInsertPromptPrefix={(prefix) => {
                setText((prev) => prefix + prev);
                if (textareaRef.current) textareaRef.current.focus();
              }}
            />

            {/* Voice Input Button */}
            <VoiceInput onTranscript={(t) => setText((prev) => prev + (prev ? ' ' : '') + t)} />

            {/* Web Search Toggle Pill */}
            <Tooltip content={webSearchEnabled ? 'Turn off Web Search' : 'Turn on Web Search'}>
              <button
                type="button"
                onClick={toggleWebSearch}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium transition-all ${
                  webSearchEnabled
                    ? 'bg-[#4285f4] text-white border-[#4285f4] font-semibold shadow-xs'
                    : 'bg-zinc-100 text-zinc-600 border-zinc-200 hover:text-zinc-900 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700'
                }`}
              >
                <Globe className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Web Search</span>
                {webSearchEnabled && <X className="w-3 h-3 ml-0.5 opacity-90 hover:opacity-100" />}
              </button>
            </Tooltip>
          </div>

          <div className="flex items-center gap-3">
            {/* Character / Token Counter */}
            <span className="text-[11px] font-mono text-zinc-400 hidden sm:inline">
              {text.length} chars
            </span>

            {/* Send / Stop Generation Button */}
            {isStreaming ? (
              <Tooltip content="Stop Generating">
                <button
                  type="button"
                  onClick={onStopGeneration}
                  className="p-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white shadow-xs transition-all flex items-center gap-1 text-xs font-semibold"
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                  <span className="hidden sm:inline">Stop</span>
                </button>
              </Tooltip>
            ) : (
              <Tooltip content="Send Message (Enter)">
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={!text.trim() && attachments.length === 0}
                  className="p-2.5 rounded-full bg-[#4285f4] hover:bg-[#3367d6] text-white disabled:opacity-30 disabled:cursor-not-allowed shadow-xs transition-all flex items-center justify-center active:scale-95"
                >
                  <Send className="w-4 h-4" />
                </button>
              </Tooltip>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
