import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Eye, Code } from 'lucide-react';

interface MermaidViewerProps {
  chart: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'neutral',
  securityLevel: 'loose',
  fontFamily: 'Inter, system-ui, sans-serif',
});

export const MermaidViewer: React.FC<MermaidViewerProps> = ({ chart }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  useEffect(() => {
    let isMounted = true;
    const renderChart = async () => {
      try {
        const id = 'mermaid-' + Math.random().toString(36).substring(2, 9);
        const { svg } = await mermaid.render(id, chart.trim());
        if (isMounted) {
          setSvgContent(svg);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to render Mermaid chart');
        }
      }
    };

    renderChart();
    return () => {
      isMounted = false;
    };
  }, [chart]);

  return (
    <div className="my-4 border border-zinc-200 rounded-xl bg-white overflow-hidden shadow-2xs dark:bg-zinc-900 dark:border-zinc-800">
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-100 border-b border-zinc-200 text-xs dark:bg-zinc-800/80 dark:border-zinc-700">
        <span className="font-semibold text-zinc-900 flex items-center gap-1.5 dark:text-zinc-100">
          <span>📊 Mermaid Diagram</span>
        </span>

        <div className="flex gap-1 p-0.5 bg-white rounded-lg border border-zinc-200 dark:bg-zinc-900 dark:border-zinc-700">
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'preview'
                ? 'bg-zinc-950 text-white shadow-2xs dark:bg-white dark:text-zinc-950 font-semibold'
                : 'text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Diagram</span>
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'code'
                ? 'bg-zinc-950 text-white shadow-2xs dark:bg-white dark:text-zinc-950 font-semibold'
                : 'text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200'
            }`}
          >
            <Code className="w-3.5 h-3.5" />
            <span>Source</span>
          </button>
        </div>
      </div>

      <div className="p-4 overflow-x-auto min-h-32 flex items-center justify-center">
        {activeTab === 'preview' ? (
          error ? (
            <div className="text-xs text-rose-600 bg-rose-50 p-3 rounded-lg border border-rose-200 w-full">
              <strong>Diagram Render Error:</strong> {error}
            </div>
          ) : (
            <div
              ref={containerRef}
              className="w-full flex justify-center text-zinc-900 dark:text-zinc-100"
              dangerouslySetInnerHTML={{ __html: svgContent }}
            />
          )
        ) : (
          <pre className="w-full text-xs font-mono text-zinc-900 bg-zinc-50 p-3 rounded-lg overflow-x-auto border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100">
            {chart}
          </pre>
        )}
      </div>
    </div>
  );
};
