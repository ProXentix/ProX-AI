import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Code2, BrainCircuit, PenTool, Zap, ArrowRight, Command } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { AI_MODELS } from '../../constants/models';

interface WelcomeScreenProps {
  onSelectPrompt: (promptText: string) => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectPrompt }) => {
  const [activeCategory, setActiveCategory] = useState<'All' | '⚡ Build' | '🧠 Think' | '💻 Code' | '🎨 Design' | '🌍 Search'>('All');
  const { activeModelId, userProfile } = useChatStore();
  const activeModel = AI_MODELS.find((m) => m.id === activeModelId) || AI_MODELS[0];

  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const suggestions = [
    {
      title: 'React 19 Form Actions & Hooks',
      prompt: 'Explain React 19 useActionState and useOptimistic with a TypeScript code example.',
      category: '💻 Code',
      icon: <Code2 className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />,
    },
    {
      title: 'Gaussian Integral & Math Derivation',
      prompt: 'Derive the Gaussian Integral \\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi} using polar coordinates.',
      category: '🧠 Think',
      icon: <BrainCircuit className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />,
    },
    {
      title: 'Microservices System Architecture',
      prompt: 'Design a real-time event streaming architecture with Kafka and Redis. Include a Mermaid flowchart.',
      category: '⚡ Build',
      icon: <Zap className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />,
    },
    {
      title: 'Executive Strategic Memo',
      prompt: 'Draft a compelling Q3 product strategy update for investors highlighting AI integration milestones.',
      category: '🎨 Design',
      icon: <PenTool className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />,
    },
  ];

  const filteredSuggestions = activeCategory === 'All'
    ? suggestions
    : suggestions.filter((s) => s.category === activeCategory);

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] max-w-3xl mx-auto px-4 py-8 text-center">

      {/* Greeting Title */}
      <motion.h1
        initial={{ y: 10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="hero-text text-3xl sm:text-4xl text-zinc-950 font-bold tracking-tight mb-2 dark:text-zinc-50"
      >
        {getTimeGreeting()}, <span className="underline decoration-blue-500 underline-offset-4">{userProfile?.name || 'Creator'}</span>
      </motion.h1>

      <motion.p
        initial={{ y: 10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.15 }}
        className="text-zinc-500 text-sm sm:text-base max-w-md mb-8 dark:text-zinc-400"
      >
        Let's build something extraordinary with <strong className="text-blue-600 font-semibold dark:text-blue-400">{activeModel.name}</strong>.
      </motion.p>

      {/* Category Pills */}
      <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
        {(['All', '⚡ Build', '🧠 Think', '💻 Code', '🎨 Design', '🌍 Search'] as const).map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
              activeCategory === cat
                ? 'bg-zinc-950 text-white shadow-xs dark:bg-white dark:text-zinc-950 font-semibold'
                : 'bg-zinc-100 text-zinc-600 hover:text-zinc-900 border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Suggested Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left mb-8">
        {filteredSuggestions.map((item, idx) => (
          <motion.button
            key={idx}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + idx * 0.05 }}
            onClick={() => onSelectPrompt(item.prompt)}
            className="group p-4 rounded-2xl bg-white hover:bg-zinc-50 border border-zinc-200 hover:border-zinc-900 transition-all shadow-2xs hover:-translate-y-0.5 dark:bg-zinc-900 dark:border-zinc-800 dark:hover:border-zinc-600"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-zinc-100 border border-zinc-200 dark:bg-zinc-800 dark:border-zinc-700">
                  {item.icon}
                </span>
                <span className="text-xs font-semibold text-zinc-900 group-hover:text-black transition-colors dark:text-zinc-100">
                  {item.title}
                </span>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-950 group-hover:translate-x-0.5 transition-all dark:group-hover:text-zinc-100" />
            </div>
            <p className="text-xs text-zinc-500 line-clamp-2 leading-relaxed dark:text-zinc-400">
              {item.prompt}
            </p>
          </motion.button>
        ))}
      </div>

      {/* Keyboard Shortcut Hints */}
      <div className="flex items-center gap-4 text-xs text-zinc-400 border-t border-zinc-200 pt-4 w-full justify-center dark:border-zinc-800">
        <span className="flex items-center gap-1">
          <kbd className="px-1.5 py-0.5 rounded bg-zinc-100 border border-zinc-200 text-zinc-700 font-mono text-[10px] dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-300">
            <Command className="w-2.5 h-2.5 inline" /> K
          </kbd>{' '}
          Search
        </span>
        <span>•</span>
        <span className="flex items-center gap-1">
          <kbd className="px-1.5 py-0.5 rounded bg-zinc-100 border border-zinc-200 text-zinc-700 font-mono text-[10px] dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-300">
            Shift + O
          </kbd>{' '}
          New Chat
        </span>
      </div>
    </div>
  );
};
