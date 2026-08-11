import React from 'react';
import { ExternalLink, Globe } from 'lucide-react';
import { Citation } from '../../types/chat';

interface CitationsBlockProps {
  citations: Citation[];
}

export const CitationsBlock: React.FC<CitationsBlockProps> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="my-3 space-y-2">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
        <Globe className="w-3.5 h-3.5 text-zinc-700 dark:text-zinc-300" />
        <span>Sources ({citations.length})</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {citations.map((c) => (
          <a
            key={c.id}
            href={c.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-start gap-2.5 p-2.5 rounded-xl bg-white hover:bg-zinc-100 border border-zinc-200 text-xs transition-all group shadow-2xs hover:border-zinc-900 dark:bg-zinc-900 dark:border-zinc-800 dark:hover:border-zinc-700"
          >
            <div className="p-1.5 rounded-lg bg-zinc-100 border border-zinc-200 shrink-0 text-zinc-900 mt-0.5 dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100">
              <Globe className="w-3.5 h-3.5" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between font-semibold text-zinc-900 group-hover:text-black transition-colors dark:text-zinc-100">
                <span className="truncate">{c.title}</span>
                <ExternalLink className="w-3 h-3 text-zinc-400 group-hover:text-zinc-900 shrink-0 ml-1 dark:group-hover:text-zinc-100" />
              </div>
              <p className="text-[11px] text-zinc-500 line-clamp-1 mt-0.5 dark:text-zinc-400">{c.snippet}</p>
              <span className="text-[10px] text-zinc-400 font-mono mt-1 block">{c.domain}</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};
