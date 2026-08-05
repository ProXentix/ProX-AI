import React from 'react';
import { Code2, FileText, Globe, Wrench, Sparkles, RefreshCw } from 'lucide-react';

export interface SlashCommand {
  command: string;
  description: string;
  template: string;
  icon: React.ReactNode;
}

export const SLASH_COMMANDS: SlashCommand[] = [
  {
    command: '/code',
    description: 'Write production-ready TypeScript code snippet',
    template: 'Write a clean TypeScript implementation for: ',
    icon: <Code2 className="w-4 h-4 text-emerald-400" />,
  },
  {
    command: '/summarize',
    description: 'Create concise executive summary with bullets',
    template: 'Provide a concise executive summary of the following text:\n\n',
    icon: <FileText className="w-4 h-4 text-blue-400" />,
  },
  {
    command: '/web',
    description: 'Deep web search and citation analysis',
    template: 'Search the web for latest 2026 insights on: ',
    icon: <Globe className="w-4 h-4 text-amber-400" />,
  },
  {
    command: '/refactor',
    description: 'Optimize code for performance and readability',
    template: 'Refactor and optimize the following code:\n\n```ts\n\n```',
    icon: <RefreshCw className="w-4 h-4 text-purple-400" />,
  },
  {
    command: '/explain',
    description: 'Explain complex technical concept simply',
    template: 'Explain how the following concept works step-by-step: ',
    icon: <Sparkles className="w-4 h-4 text-teal-400" />,
  },
  {
    command: '/fix',
    description: 'Debug and fix errors in code snippet',
    template: 'Find and fix the bugs in this code:\n\n',
    icon: <Wrench className="w-4 h-4 text-rose-400" />,
  },
];

interface SlashCommandsProps {
  onSelect: (cmd: SlashCommand) => void;
  filter: string;
}

export const SlashCommands: React.FC<SlashCommandsProps> = ({ onSelect, filter }) => {
  const filtered = SLASH_COMMANDS.filter((c) =>
    c.command.toLowerCase().includes(filter.toLowerCase())
  );

  if (filtered.length === 0) return null;

  return (
    <div className="absolute bottom-full mb-2 left-0 right-0 max-w-lg mx-auto bg-slate-900/95 border border-slate-700/80 rounded-2xl shadow-2xl p-2 z-50 backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150">
      <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800 mb-1">
        Slash Commands
      </div>

      <div className="space-y-1 max-h-48 overflow-y-auto">
        {filtered.map((cmd) => (
          <button
            key={cmd.command}
            onClick={() => onSelect(cmd)}
            className="w-full flex items-center gap-3 p-2 rounded-xl text-left hover:bg-slate-800/80 text-slate-200 transition-colors group"
          >
            <span className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 group-hover:border-emerald-500/40">
              {cmd.icon}
            </span>
            <div className="flex-1 min-w-0">
              <span className="text-xs font-mono font-bold text-emerald-400">{cmd.command}</span>
              <span className="text-xs text-slate-400 ml-2">{cmd.description}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
