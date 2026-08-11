import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'emerald' | 'blue' | 'purple' | 'slate' | 'amber' | 'mono';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'mono', className }) => {
  const variants = {
    mono: 'bg-zinc-100 text-zinc-900 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700',
    emerald: 'bg-zinc-100 text-zinc-900 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700',
    blue: 'bg-zinc-100 text-zinc-900 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700',
    purple: 'bg-zinc-100 text-zinc-900 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700',
    slate: 'bg-zinc-100 text-zinc-900 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700',
    amber: 'bg-zinc-100 text-zinc-900 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700',
  };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md border tracking-wide uppercase',
          variants[variant],
          className
        )
      )}
    >
      {children}
    </span>
  );
};
