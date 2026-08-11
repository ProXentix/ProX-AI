import React, { useState, useRef, useEffect } from 'react';
import { Plus, Paperclip, BookOpen, Image as ImageIcon, Telescope } from 'lucide-react';
import { Attachment } from '../../types/chat';
import { useChatStore } from '../../store/chatStore';
import { Tooltip } from '../ui/Tooltip';

interface FileUploaderProps {
  attachments: Attachment[];
  onAddAttachment: (att: Attachment) => void;
  onRemoveAttachment: (id: string) => void;
  onInsertPromptPrefix?: (prefix: string) => void;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  attachments,
  onAddAttachment,
  onInsertPromptPrefix,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const { webSearchEnabled, toggleWebSearch, setSavedPromptsModalOpen } = useChatStore();

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach((file) => {
      let type: Attachment['type'] = 'text';
      if (file.type.startsWith('image/')) type = 'image';
      else if (file.name.endsWith('.ts') || file.name.endsWith('.tsx') || file.name.endsWith('.py') || file.name.endsWith('.rs')) type = 'code';
      else if (file.name.endsWith('.pdf')) type = 'pdf';

      const newAtt: Attachment = {
        id: 'att-' + Date.now() + '-' + Math.random().toString(36).substring(2, 6),
        name: file.name,
        size: file.size,
        type,
      };

      onAddAttachment(newAtt);
    });

    if (fileInputRef.current) fileInputRef.current.value = '';
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={menuRef}>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        className="hidden"
      />

      <Tooltip content="Add attachment or action">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-xl text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 transition-all dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800"
        >
          <Plus className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-45 text-zinc-900 dark:text-zinc-100' : ''}`} />
        </button>
      </Tooltip>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-3 w-80 p-1.5 bg-white border border-zinc-200/90 rounded-2xl shadow-2xl z-50 font-sans animate-in fade-in zoom-in-95 duration-150 dark:bg-zinc-900 dark:border-zinc-800">
          <div className="space-y-0.5">
            {/* 1. Add photos & files */}
            <button
              type="button"
              onClick={() => {
                fileInputRef.current?.click();
              }}
              className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-zinc-100/80 text-left transition-colors dark:hover:bg-zinc-800/80"
            >
              <div className="flex items-center gap-3">
                <Paperclip className="w-4 h-4 text-zinc-700 dark:text-zinc-300 shrink-0" />
                <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">
                  Add photos & files
                </span>
              </div>
              <span className="text-[11px] text-zinc-400 dark:text-zinc-500 font-normal">
                Upload from computer
              </span>
            </button>

            {/* 2. Add from library */}
            <button
              type="button"
              onClick={() => {
                setSavedPromptsModalOpen(true);
                setIsOpen(false);
              }}
              className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-zinc-100/80 text-left transition-colors dark:hover:bg-zinc-800/80"
            >
              <div className="flex items-center gap-3">
                <BookOpen className="w-4 h-4 text-zinc-700 dark:text-zinc-300 shrink-0" />
                <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">
                  Add from library
                </span>
              </div>
              <span className="text-[11px] text-zinc-400 dark:text-zinc-500 font-normal">
                Browse and search your files
              </span>
            </button>

            {/* 3. Create image */}
            <button
              type="button"
              onClick={() => {
                if (onInsertPromptPrefix) onInsertPromptPrefix('Create a high quality image of ');
                setIsOpen(false);
              }}
              className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-zinc-100/80 text-left transition-colors dark:hover:bg-zinc-800/80"
            >
              <div className="flex items-center gap-3">
                <span className="p-1 rounded-lg bg-amber-100 border border-amber-200 text-amber-600 dark:bg-amber-950/60 dark:border-amber-900 dark:text-amber-400 shrink-0">
                  <ImageIcon className="w-3.5 h-3.5" />
                </span>
                <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">
                  Create image
                </span>
              </div>
              <span className="text-[11px] text-zinc-400 dark:text-zinc-500 font-normal">
                Visualize anything
              </span>
            </button>



            {/* 5. Deep research */}
            <button
              type="button"
              onClick={() => {
                if (!webSearchEnabled) toggleWebSearch();
                if (onInsertPromptPrefix) onInsertPromptPrefix('Perform deep research on ');
                setIsOpen(false);
              }}
              className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-zinc-100/80 text-left transition-colors dark:hover:bg-zinc-800/80"
            >
              <div className="flex items-center gap-3">
                <span className="p-1 rounded-lg bg-blue-100 border border-blue-200 text-blue-600 dark:bg-blue-950/60 dark:border-blue-900 dark:text-blue-400 shrink-0">
                  <Telescope className="w-3.5 h-3.5" />
                </span>
                <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100">
                  Deep research
                </span>
              </div>
              <span className="text-[11px] text-zinc-400 dark:text-zinc-500 font-normal">
                Get a detailed report
              </span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

