import React, { useState } from 'react';
import { ChevronDown, BrainCircuit, Clock } from 'lucide-react';
import { ReasoningStep } from '../../types/chat';

interface ReasoningBlockProps {
  reasoning: {
    thinkingTimeSeconds?: number;
    steps: ReasoningStep[];
  };
}

export const ReasoningBlock: React.FC<ReasoningBlockProps> = ({ reasoning }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="my-2 border border-zinc-200 rounded-xl bg-white overflow-hidden text-xs dark:border-zinc-800 dark:bg-zinc-950">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3 py-2 bg-zinc-100/60 hover:bg-zinc-100 text-zinc-700 transition-colors dark:bg-zinc-800/40 dark:hover:bg-zinc-800 dark:text-zinc-300"
      >
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-zinc-900 animate-pulse dark:text-zinc-100" />
          <span className="font-semibold text-zinc-900 dark:text-zinc-100">Thinking Process</span>
          {reasoning.thinkingTimeSeconds && (
            <span className="flex items-center gap-1 text-[11px] text-zinc-500 bg-white px-2 py-0.5 rounded-full border border-zinc-200 dark:bg-zinc-900 dark:border-zinc-700 font-mono">
              <Clock className="w-3 h-3 text-zinc-400" />
              {reasoning.thinkingTimeSeconds}s
            </span>
          )}
        </div>

        <ChevronDown className={`w-4 h-4 text-zinc-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="p-3 space-y-2 border-t border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950">
          {reasoning.steps.map((step, idx) => (
            <div key={step.id || idx} className="space-y-1">
              <div className="flex items-center gap-2 font-semibold text-zinc-900 dark:text-zinc-100">
                <span className="w-4 h-4 rounded-full bg-zinc-900 text-white flex items-center justify-center text-[10px] font-bold dark:bg-white dark:text-zinc-950">
                  {idx + 1}
                </span>
                <span>{step.title}</span>
              </div>
              <p className="pl-6 text-zinc-600 text-[11px] leading-relaxed dark:text-zinc-400">
                {step.content}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
