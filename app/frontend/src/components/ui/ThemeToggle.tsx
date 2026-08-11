import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useSettingsStore, ThemeMode } from '../../store/settingsStore';
import { motion } from 'framer-motion';
import { Tooltip } from './Tooltip';

export const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useSettingsStore();

  const options: { mode: ThemeMode; label: string; icon: React.ReactNode }[] = [
    { mode: 'light', label: 'Light', icon: <Sun className="w-3.5 h-3.5" /> },
    { mode: 'dark', label: 'Dark', icon: <Moon className="w-3.5 h-3.5" /> },
    { mode: 'system', label: 'System', icon: <Monitor className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="flex items-center p-0.5 bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl">
      {options.map((opt) => {
        const isActive = theme === opt.mode;
        return (
          <Tooltip key={opt.mode} content={`Switch to ${opt.label} theme`}>
            <button
              onClick={() => setTheme(opt.mode)}
              className={`relative flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg transition-colors duration-150 ${
                isActive ? 'text-zinc-950 dark:text-white font-semibold' : 'text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="activeThemeBg"
                  className="absolute inset-0 bg-white dark:bg-zinc-800 rounded-lg shadow-xs border border-zinc-200 dark:border-zinc-700"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative z-10">{opt.icon}</span>
              <span className="relative z-10 hidden sm:inline">{opt.label}</span>
            </button>
          </Tooltip>
        );
      })}
    </div>
  );
};
