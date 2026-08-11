import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Sparkles, Cpu, BrainCircuit, Check } from 'lucide-react';
import { AI_MODELS } from '../../constants/models';
import { useChatStore } from '../../store/chatStore';
import { ModelInfo } from '../../types/chat';
import { Tooltip } from './Tooltip';

const ICON_MAP: Record<string, React.ReactNode> = {
  Sparkles: <Sparkles className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-100" />,
  Cpu: <Cpu className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-100" />,
  BrainCircuit: <BrainCircuit className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-100" />,
};

export const ModelSelector: React.FC = () => {
  const { activeModelId, setActiveModel } = useChatStore();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const activeModel = AI_MODELS.find((m) => m.id === activeModelId) || AI_MODELS[0];

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <Tooltip content="Switch AI Model" position="bottom">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-100 hover:bg-zinc-200/70 border border-zinc-200 text-zinc-900 text-xs font-medium transition-all shadow-xs dark:bg-zinc-800 dark:hover:bg-zinc-700 dark:border-zinc-700 dark:text-zinc-100"
        >
          <span className="p-1 rounded-md bg-white border border-zinc-200 dark:bg-zinc-900 dark:border-zinc-700">
            {ICON_MAP[activeModel.icon] || <Sparkles className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-100" />}
          </span>
          <span className="tracking-tight font-semibold">{activeModel.name}</span>
          <span className="text-[10px] text-zinc-500 font-mono px-1.5 py-0.5 rounded bg-white border border-zinc-200 dark:bg-zinc-900 dark:border-zinc-700">
            {activeModel.capabilities.contextWindow}
          </span>
          <ChevronDown className={`w-3.5 h-3.5 text-zinc-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
        </button>
      </Tooltip>

      {isOpen && (
        <div className="absolute left-0 mt-2 w-72 p-1.5 bg-white border border-zinc-200 rounded-2xl shadow-xl z-50 animate-in fade-in zoom-in-95 duration-150 dark:bg-zinc-900 dark:border-zinc-800">
          <div className="px-3 py-2 text-[11px] font-semibold text-zinc-400 uppercase tracking-wider border-b border-zinc-100 dark:border-zinc-800 mb-1">
            Select Intelligence Model
          </div>

          <div className="space-y-1 max-h-80 overflow-y-auto">
            {AI_MODELS.map((model: ModelInfo) => {
              const isSelected = model.id === activeModelId;
              return (
                <button
                  key={model.id}
                  onClick={() => {
                    setActiveModel(model.id);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-start gap-3 p-2.5 rounded-xl text-left transition-all ${
                    isSelected
                      ? 'bg-zinc-100 border border-zinc-300 text-zinc-950 font-medium dark:bg-zinc-800 dark:border-zinc-700 dark:text-white'
                      : 'hover:bg-zinc-50 text-zinc-700 hover:text-zinc-950 dark:hover:bg-zinc-800/50 dark:text-zinc-300 dark:hover:text-white'
                  }`}
                >
                  <span className="p-2 rounded-lg bg-zinc-100 border border-zinc-200 shrink-0 mt-0.5 dark:bg-zinc-800 dark:border-zinc-700">
                    {ICON_MAP[model.icon] || <Sparkles className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />}
                  </span>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold tracking-tight text-zinc-900 dark:text-zinc-100 flex items-center gap-1.5">
                        {model.name}
                        {model.badge && (
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-200 text-zinc-800 border border-zinc-300 dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700">
                            {model.badge}
                          </span>
                        )}
                      </span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-100" />}
                    </div>

                    <p className="text-[11px] text-zinc-500 line-clamp-1 mt-0.5 dark:text-zinc-400">
                      {model.description}
                    </p>

                    <div className="flex items-center gap-2 mt-1 text-[10px] text-zinc-400">
                      <span>{model.provider}</span>
                      <span>•</span>
                      <span>Ctx: {model.capabilities.contextWindow}</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
