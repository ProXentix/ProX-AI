import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { CodeBlock } from '../chat/CodeBlock';
import { MermaidViewer } from './MermaidViewer';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="prose prose-zinc max-w-none text-zinc-900 text-sm leading-relaxed space-y-3 dark:prose-invert dark:text-zinc-100 font-sans">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code({ inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const codeString = String(children).replace(/\n$/, '');

            if (!inline && match && match[1] === 'mermaid') {
              return <MermaidViewer chart={codeString} />;
            }

            if (!inline && match) {
              return <CodeBlock language={match[1]} code={codeString} />;
            }

            if (!inline) {
              return <CodeBlock language="text" code={codeString} />;
            }

            return (
              <code
                className="px-1.5 py-0.5 text-xs font-mono rounded bg-zinc-100 text-zinc-900 border border-zinc-200 font-semibold dark:bg-zinc-800 dark:text-zinc-100 dark:border-zinc-700"
                {...props}
              >
                {children}
              </code>
            );
          },
          table({ children }) {
            return (
              <div className="my-4 overflow-x-auto rounded-xl border border-zinc-200 bg-white shadow-2xs dark:bg-zinc-900 dark:border-zinc-800">
                <table className="w-full text-left border-collapse text-xs">
                  {children}
                </table>
              </div>
            );
          },
          thead({ children }) {
            return <thead className="bg-zinc-100 border-b border-zinc-200 text-zinc-900 font-semibold dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100">{children}</thead>;
          },
          th({ children }) {
            return <th className="px-4 py-2.5">{children}</th>;
          },
          td({ children }) {
            return <td className="px-4 py-2 border-t border-zinc-200 text-zinc-800 dark:border-zinc-800 dark:text-zinc-200">{children}</td>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="my-3 pl-4 border-l-2 border-zinc-950 bg-zinc-100/60 p-3 rounded-r-xl text-zinc-700 italic dark:border-zinc-100 dark:bg-zinc-900 dark:text-zinc-300">
                {children}
              </blockquote>
            );
          },
          h1({ children }) {
            return <h1 className="text-xl font-bold text-zinc-950 mt-6 mb-3 tracking-tight border-b border-zinc-200 pb-2 dark:text-zinc-50 dark:border-zinc-800">{children}</h1>;
          },
          h2({ children }) {
            return <h2 className="text-lg font-bold text-zinc-950 mt-5 mb-2 tracking-tight dark:text-zinc-50">{children}</h2>;
          },
          h3({ children }) {
            return <h3 className="text-base font-semibold text-zinc-900 mt-4 mb-2 dark:text-zinc-100">{children}</h3>;
          },
          ul({ children }) {
            return <ul className="list-disc pl-5 my-2 space-y-1 text-zinc-800 dark:text-zinc-200">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal pl-5 my-2 space-y-1 text-zinc-800 dark:text-zinc-200">{children}</ol>;
          },
          a({ href, children }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noreferrer"
                className="text-zinc-950 hover:text-black underline underline-offset-4 font-semibold transition-colors dark:text-white"
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
