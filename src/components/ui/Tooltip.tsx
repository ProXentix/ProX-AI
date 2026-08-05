import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TooltipProps {
  content: string | React.ReactNode;
  children: React.ReactElement;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  delay = 200,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [timer, setTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  const handleMouseEnter = () => {
    const t = setTimeout(() => setIsVisible(true), delay);
    setTimer(t);
  };

  const handleMouseLeave = () => {
    if (timer) clearTimeout(timer);
    setIsVisible(false);
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'bottom':
        return 'top-full mt-2 left-1/2 -translate-x-1/2';
      case 'left':
        return 'right-full mr-2 top-1/2 -translate-y-1/2';
      case 'right':
        return 'left-full ml-2 top-1/2 -translate-y-1/2';
      case 'top':
      default:
        return 'bottom-full mb-2 left-1/2 -translate-x-1/2';
    }
  };

  return (
    <div
      className="relative inline-flex items-center"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}

      <AnimatePresence>
        {isVisible && content && (
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: position === 'top' ? 4 : position === 'bottom' ? -4 : 0 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: position === 'top' ? 4 : position === 'bottom' ? -4 : 0 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className={`absolute ${getPositionClasses()} z-50 pointer-events-none whitespace-nowrap px-2.5 py-1 rounded-lg bg-zinc-950 text-white font-medium text-[11px] shadow-lg border border-zinc-800 dark:bg-zinc-100 dark:text-zinc-950 dark:border-zinc-200 tracking-tight`}
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
