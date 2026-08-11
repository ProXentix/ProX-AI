import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles, TrendingUp, Star, Clock, Zap, Users,
  ArrowRight, ArrowLeft, Flame, BookOpen, Cpu, BrainCircuit,
  Code2, PenTool, Globe, Search
} from 'lucide-react';

interface ExplorePageProps {
  onSelectPrompt: (prompt: string) => void;
  onClose: () => void;
}

const FEATURED_PROMPTS = [
  {
    title: 'Full-Stack App Generator',
    description: 'Generate a production-ready Next.js app with auth, DB schema, and API routes.',
    prompt: 'Create a production-ready Next.js 14 app with Prisma ORM, NextAuth.js, and a full dashboard UI using Tailwind CSS.',
    category: 'Build',
    icon: <Zap className="w-4 h-4" />,
    color: 'from-blue-500 to-cyan-500',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800/50',
    badge: '⚡ Featured',
  },
  {
    title: 'Code Review & Refactor',
    description: 'Deep code review with security checks, performance analysis, and modern patterns.',
    prompt: 'Perform an expert-level code review of the following code. Check for security vulnerabilities, performance bottlenecks, and TypeScript best practices:\n\n```ts\n// paste code here\n```',
    category: 'Code',
    icon: <Code2 className="w-4 h-4" />,
    color: 'from-violet-500 to-purple-500',
    bg: 'bg-violet-50 dark:bg-violet-950/30',
    border: 'border-violet-200 dark:border-violet-800/50',
    badge: '🔥 Popular',
  },
  {
    title: 'System Design Interview',
    description: 'Practice system design with architecture diagrams and trade-off analysis.',
    prompt: 'Design a highly scalable real-time chat system like WhatsApp supporting 1 billion users. Include architecture diagram in Mermaid, database schema, and key trade-offs.',
    category: 'Think',
    icon: <BrainCircuit className="w-4 h-4" />,
    color: 'from-emerald-500 to-teal-500',
    bg: 'bg-emerald-50 dark:bg-emerald-950/30',
    border: 'border-emerald-200 dark:border-emerald-800/50',
    badge: '⭐ Top Rated',
  },
];

const TRENDING_PROMPTS = [
  {
    title: 'React 19 Migration Guide',
    prompt: 'Provide a complete step-by-step React 19 migration guide covering useActionState, useOptimistic, server components, and ref breaking changes.',
    category: '💻 Code',
    uses: '12.4k',
    icon: <Code2 className="w-3.5 h-3.5" />
  },
  {
    title: 'LLM Fine-tuning Walkthrough',
    prompt: 'Write a comprehensive guide on fine-tuning an open-weight LLM using LLaMA-Factory / QLoRA with PyTorch and Hugging Face.',
    category: '🧠 Think',
    uses: '9.8k',
    icon: <BrainCircuit className="w-3.5 h-3.5" />
  },
  {
    title: 'Landing Page Copy Generator',
    prompt: 'Generate compelling, high-converting SaaS landing page copy for an AI developer tool, including hero headline, subhead, features grid, and FAQ section.',
    category: '🎨 Design',
    uses: '8.3k',
    icon: <PenTool className="w-3.5 h-3.5" />
  },
  {
    title: 'SQL Query Optimizer',
    prompt: 'Act as a Senior Database Administrator. Analyze and optimize the following SQL query for PostgreSQL performance, indexing, and execution plan:\n\nSELECT * FROM orders WHERE status = "pending"...',
    category: '💻 Code',
    uses: '7.1k',
    icon: <Code2 className="w-3.5 h-3.5" />
  },
  {
    title: 'Market Research Report',
    prompt: 'Conduct a thorough market research analysis on the current generative AI developer tooling landscape. Include key players, market size, growth drivers, and strategic recommendations.',
    category: '🌍 Search',
    uses: '6.9k',
    icon: <Globe className="w-3.5 h-3.5" />
  },
  {
    title: 'API Documentation Writer',
    prompt: 'Generate clean OpenAPI 3.0 specs and Markdown developer documentation for a RESTful User Authentication & Auth Token API.',
    category: '⚡ Build',
    uses: '5.2k',
    icon: <Zap className="w-3.5 h-3.5" />
  },
];

const OFFICIAL_TEMPLATES = [
  {
    title: 'PRD Writer',
    description: 'Generate a complete Product Requirements Document with user stories and acceptance criteria.',
    prompt: 'Write a comprehensive PRD for: [product feature]. Include executive summary, user personas, user stories, technical requirements, success metrics, and a Mermaid timeline.',
    icon: <BookOpen className="w-5 h-5" />,
    tag: 'Productivity',
    color: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-50 dark:bg-amber-950/30',
    border: 'border-amber-200 dark:border-amber-800/40',
  },
  {
    title: 'AI Agent Builder',
    description: 'Design and scaffold an autonomous AI agent with tools and memory.',
    prompt: 'Design a LangChain/LangGraph autonomous AI agent that can: [task]. Include the agent architecture, tool definitions, memory setup, and Python implementation code.',
    icon: <Cpu className="w-5 h-5" />,
    tag: 'AI Workflows',
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800/40',
  },
  {
    title: 'Technical Blog Post',
    description: 'Write an SEO-optimized technical deep dive with code examples.',
    prompt: 'Write a high-quality, SEO-optimized technical blog post about: [topic]. Target audience: senior engineers. Include code examples, architecture diagrams in Mermaid, and actionable takeaways.',
    icon: <PenTool className="w-5 h-5" />,
    tag: 'Writing',
    color: 'text-rose-600 dark:text-rose-400',
    bg: 'bg-rose-50 dark:bg-rose-950/30',
    border: 'border-rose-200 dark:border-rose-800/40',
  },
  {
    title: 'Data Pipeline Architect',
    description: 'Design an ETL pipeline with schema, transformations, and monitoring.',
    prompt: 'Design a real-time data pipeline for: [use case]. Include the ingestion layer, transformation logic, storage schema (dbt models), and observability setup with Mermaid flowchart.',
    icon: <Zap className="w-5 h-5" />,
    tag: 'Build',
    color: 'text-cyan-600 dark:text-cyan-400',
    bg: 'bg-cyan-50 dark:bg-cyan-950/30',
    border: 'border-cyan-200 dark:border-cyan-800/40',
  },
];

const AI_WORKFLOWS = [
  {
    title: 'Code → Review → Deploy',
    steps: ['Write feature code', 'AI code review', 'Generate tests', 'Write deploy docs'],
    prompt: 'Act as a senior engineering team. First write the implementation for [feature], then perform a security and performance code review, then generate Jest unit tests, then write deployment documentation.',
    color: 'bg-gradient-to-r from-blue-600 to-violet-600',
  },
  {
    title: 'Research → Analyze → Report',
    steps: ['Deep research', 'Data analysis', 'Visualize insights', 'Write report'],
    prompt: 'Act as a research analyst. First research [topic] thoroughly, then analyze key data points and trends, then create a structured summary with visualizations described in detail, then write an executive report.',
    color: 'bg-gradient-to-r from-emerald-600 to-teal-600',
  },
  {
    title: 'Idea → PRD → MVP',
    steps: ['Refine idea', 'Write PRD', 'Design system', 'Build MVP plan'],
    prompt: 'Act as a product team. Take this idea: [idea], refine it into a validated concept, write a PRD, design the system architecture, and create a 4-week MVP development plan.',
    color: 'bg-gradient-to-r from-orange-500 to-rose-600',
  },
];

export const ExplorePage: React.FC<ExplorePageProps> = ({ onSelectPrompt, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');

  const filters = ['All', '⚡ Build', '🧠 Think', '💻 Code', '🎨 Design', '🌍 Search'];

  return (
    <div className="flex-1 overflow-y-auto bg-white dark:bg-zinc-950 h-full">
      {/* Hero Header */}
      <div className="sticky top-0 z-10 bg-white/90 dark:bg-zinc-950/90 backdrop-blur-md border-b border-zinc-100 dark:border-zinc-800 px-6 py-4">
        <div className="w-full flex items-center justify-between gap-4">
          {/* Left: Back Button */}
          <button
            onClick={onClose}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-zinc-900 bg-zinc-100 hover:bg-zinc-200/80 border border-zinc-200/80 transition-all dark:text-zinc-300 dark:hover:text-zinc-100 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:border-zinc-800 shrink-0 shadow-2xs"
            title="Back to Chat"
          >
            <ArrowLeft className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span className="hidden sm:inline">Back</span>
          </button>

          {/* Center: Title & Subtitle */}
          <div className="text-center min-w-0 flex-1">
            <h1 className="text-xl sm:text-2xl font-extrabold text-zinc-900 dark:text-zinc-100 flex items-center justify-center gap-2 tracking-tight">
              <Sparkles className="w-5.5 h-5.5 text-blue-600 dark:text-blue-400" />
              Explore
            </h1>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 font-medium truncate">
              Featured prompts, templates & AI workflows
            </p>
          </div>

          {/* Right: Search Bar */}
          <div className="relative w-44 sm:w-64 shrink-0">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-400" />
            <input
              type="text"
              placeholder="Search prompts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-xl text-xs bg-zinc-100 border border-zinc-200 text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-blue-500 dark:bg-zinc-900 dark:border-zinc-700 dark:text-zinc-100 dark:placeholder-zinc-500 shadow-2xs"
            />
          </div>
        </div>

        {/* Filter Pills */}
        <div className="max-w-5xl mx-auto flex items-center justify-center gap-2 mt-4 flex-wrap">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                activeFilter === f
                  ? 'bg-zinc-950 text-white dark:bg-white dark:text-zinc-950 font-semibold shadow-xs'
                  : 'bg-zinc-100 text-zinc-600 hover:text-zinc-900 border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-6 space-y-10">

        {/* ── FEATURED PROMPTS ── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-4 h-4 text-amber-500" />
            <h2 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">Featured Prompts</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {FEATURED_PROMPTS.map((p, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => { onSelectPrompt(p.prompt); onClose(); }}
                className={`group relative p-4 rounded-2xl text-left border ${p.bg} ${p.border} hover:shadow-md transition-all hover:-translate-y-0.5`}
              >
                <div className={`w-8 h-8 rounded-xl bg-gradient-to-br ${p.color} flex items-center justify-center text-white mb-3 shadow-sm`}>
                  {p.icon}
                </div>
                <span className="text-[10px] font-mono font-semibold text-zinc-400 dark:text-zinc-500">{p.badge}</span>
                <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mt-1 mb-1">{p.title}</h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2 leading-relaxed">{p.description}</p>
                <div className="flex items-center gap-1 mt-3 text-xs text-zinc-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors font-medium">
                  Use prompt <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </motion.button>
            ))}
          </div>
        </section>

        {/* ── TRENDING PROMPTS ── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-rose-500" />
            <h2 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">Trending</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {TRENDING_PROMPTS.map((p, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                onClick={() => { onSelectPrompt(p.prompt); onClose(); }}
                className="group flex items-center gap-3 p-3 rounded-xl text-left bg-zinc-50 hover:bg-zinc-100 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800 dark:hover:bg-zinc-800/80 transition-all"
              >
                <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 shrink-0">
                  {p.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 truncate">{p.title}</p>
                  <p className="text-[10px] text-zinc-400">{p.category} · {p.uses} uses</p>
                </div>
                <Flame className="w-3.5 h-3.5 text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.button>
            ))}
          </div>
        </section>

        {/* ── OFFICIAL TEMPLATES ── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 text-blue-500" />
            <h2 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">Official ProX Templates</h2>
            <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400 text-[10px] font-semibold border border-blue-200 dark:border-blue-800/50">Official</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {OFFICIAL_TEMPLATES.map((t, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => { onSelectPrompt(t.prompt); onClose(); }}
                className={`group flex items-start gap-3.5 p-4 rounded-2xl text-left border ${t.bg} ${t.border} hover:shadow-sm transition-all hover:-translate-y-0.5`}
              >
                <span className={`p-2.5 rounded-xl bg-white dark:bg-zinc-900 border ${t.border} ${t.color} shrink-0 shadow-xs`}>
                  {t.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-xs font-bold text-zinc-900 dark:text-zinc-100">{t.title}</h3>
                    <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 font-medium border border-zinc-200 dark:border-zinc-700">{t.tag}</span>
                  </div>
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1 line-clamp-2 leading-relaxed">{t.description}</p>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-300 dark:text-zinc-600 group-hover:text-zinc-700 dark:group-hover:text-zinc-300 group-hover:translate-x-0.5 transition-all shrink-0 mt-1" />
              </motion.button>
            ))}
          </div>
        </section>

        {/* ── AI WORKFLOWS ── */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4 text-violet-500" />
            <h2 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">AI Workflows</h2>
            <span className="text-[10px] text-zinc-400 dark:text-zinc-500">Multi-step AI pipelines</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {AI_WORKFLOWS.map((w, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.06 }}
                onClick={() => { onSelectPrompt(w.prompt); onClose(); }}
                className="group p-4 rounded-2xl text-left bg-zinc-50 border border-zinc-200 dark:bg-zinc-900 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-600 shadow-2xs hover:shadow-md transition-all hover:-translate-y-0.5"
              >
                <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg ${w.color} text-white text-[10px] font-bold mb-3`}>
                  <Zap className="w-3 h-3" />
                  Workflow
                </div>
                <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-3">{w.title}</h3>
                <div className="space-y-1.5">
                  {w.steps.map((step, si) => (
                    <div key={si} className="flex items-center gap-2">
                      <span className="w-4 h-4 rounded-full bg-zinc-200 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 text-[10px] font-bold flex items-center justify-center shrink-0">{si + 1}</span>
                      <span className="text-[11px] text-zinc-600 dark:text-zinc-400">{step}</span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-1 mt-4 text-xs text-zinc-500 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors font-medium">
                  Run workflow <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </motion.button>
            ))}
          </div>
        </section>

        {/* ── COMMUNITY PROMPTS ── */}
        <section className="pb-8">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-4 h-4 text-teal-500" />
            <h2 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">Community Picks</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {[
              { title: 'Explain Like I\'m 5', prompt: 'Explain [concept] as if I\'m 5 years old, then explain it again for a senior engineer.', author: '@dev_alice', likes: '2.1k' },
              { title: 'Rubber Duck Debugger', prompt: 'Act as a rubber duck debugger. Ask me questions to help me find the bug in my code. Start by asking me to describe what my code is supposed to do.', author: '@codewitch', likes: '1.8k' },
              { title: 'Socratic Teacher', prompt: 'Teach me [topic] using the Socratic method. Ask me leading questions to help me discover the answers myself.', author: '@learn_ai', likes: '1.5k' },
              { title: 'Devil\'s Advocate', prompt: 'Act as devil\'s advocate for this idea: [idea]. Give me the strongest possible counterarguments.', author: '@critical_thinker', likes: '1.2k' },
            ].map((p, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.04 }}
                onClick={() => { onSelectPrompt(p.prompt); onClose(); }}
                className="group flex items-start justify-between gap-3 p-3.5 rounded-xl text-left bg-zinc-50 hover:bg-zinc-100 border border-zinc-200 dark:bg-zinc-900/50 dark:border-zinc-800 dark:hover:bg-zinc-800/60 transition-all"
              >
                <div>
                  <p className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 mb-1">{p.title}</p>
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 line-clamp-1">{p.prompt}</p>
                  <p className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-1.5">{p.author} · ♥ {p.likes}</p>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-300 dark:text-zinc-600 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors shrink-0 mt-0.5" />
              </motion.button>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
};
