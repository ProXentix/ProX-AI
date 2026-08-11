import React, { useState, useEffect } from 'react';
import Prism from 'prismjs';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-markdown';
import 'prismjs/components/prism-sql';
import { Copy, Check, Download, Maximize2, Minimize2, WrapText } from 'lucide-react';
import { copyToClipboard } from '../../utils/formatters';
import { useSettingsStore } from '../../store/settingsStore';
import { Tooltip } from '../ui/Tooltip';

interface CodeBlockProps {
  language: string;
  code: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { showLineNumbers, enableWordWrap, setEnableWordWrap } = useSettingsStore();

  const cleanLang = (language || 'text').replace(/language-/, '').toLowerCase();

  useEffect(() => {
    Prism.highlightAll();
  }, [code, cleanLang]);

  const handleCopy = async () => {
    const success = await copyToClipboard(code);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    const extMap: Record<string, string> = {
      typescript: 'ts',
      javascript: 'js',
      tsx: 'tsx',
      jsx: 'jsx',
      python: 'py',
      rust: 'rs',
      css: 'css',
      json: 'json',
      sql: 'sql',
      bash: 'sh',
      html: 'html',
    };
    const extension = extMap[cleanLang] || 'txt';
    const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `snippet.${extension}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const lines = code.trim().split('\n');

  return (
    <div
      className={`relative my-4 rounded-xl border border-slate-700/80 bg-[#0d1117] overflow-hidden shadow-xl transition-all ${
        isFullscreen ? 'fixed inset-4 z-50 my-0 max-w-none flex flex-col' : ''
      }`}
    >
      {/* Header toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800/80 border-b border-slate-700/60 text-xs text-slate-300 select-none">
        <div className="flex items-center gap-2">
          <span className="flex gap-1.5 mr-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
          </span>
          <span className="font-mono text-emerald-400 font-semibold uppercase tracking-wider text-[11px]">
            {cleanLang}
          </span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400 text-[11px]">{lines.length} lines</span>
        </div>

        <div className="flex items-center gap-1">
          <Tooltip content="Toggle Word Wrap">
            <button
              onClick={() => setEnableWordWrap(!enableWordWrap)}
              className={`p-1.5 rounded-md hover:bg-slate-700/60 transition-colors ${
                enableWordWrap ? 'text-emerald-400 bg-emerald-500/10' : 'text-slate-400'
              }`}
            >
              <WrapText className="w-3.5 h-3.5" />
            </button>
          </Tooltip>

          <Tooltip content="Download Snippet">
            <button
              onClick={handleDownload}
              className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-700/60 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
          </Tooltip>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 rounded-md text-xs bg-slate-700/50 hover:bg-slate-700 text-slate-200 transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400 text-[11px]">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span className="text-[11px]">Copy</span>
              </>
            )}
          </button>

          <Tooltip content={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-700/60 transition-colors"
            >
              {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
            </button>
          </Tooltip>
        </div>
      </div>

      {/* Code body */}
      <div className={`p-4 overflow-x-auto font-mono text-xs leading-relaxed text-slate-200 ${isFullscreen ? 'flex-1 overflow-y-auto' : 'max-h-96 overflow-y-auto'}`}>
        <div className="flex">
          {showLineNumbers && (
            <div className="select-none pr-4 text-right text-slate-600 border-r border-slate-800 shrink-0 font-mono text-[11px]">
              {lines.map((_, i) => (
                <div key={i}>{i + 1}</div>
              ))}
            </div>
          )}

          <pre className={`pl-4 flex-1 ${enableWordWrap ? 'whitespace-pre-wrap break-words' : 'whitespace-pre'}`}>
            <code className={`language-${cleanLang}`}>{code.trim()}</code>
          </pre>
        </div>
      </div>
    </div>
  );
};
