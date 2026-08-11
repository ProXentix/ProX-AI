import React from 'react';
import { Sparkles, Settings } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { Tooltip } from '../ui/Tooltip';

export const UserProfile: React.FC = () => {
  const { setSettingsModalOpen, setProfileModalOpen, userProfile } = useChatStore();

  return (
    <div className="p-3 border-t border-zinc-200 bg-zinc-100/60 dark:border-zinc-800 dark:bg-zinc-950/60">
      <div className="flex items-center justify-between p-2 rounded-xl bg-white border border-zinc-200 hover:border-zinc-300 transition-all shadow-2xs dark:bg-zinc-900 dark:border-zinc-800">
        <div
          onClick={() => setProfileModalOpen(true)}
          className="flex items-center gap-2.5 min-w-0 flex-1 cursor-pointer group"
          title="Open Profile & Account"
        >
          <div className="w-8 h-8 rounded-xl bg-zinc-950 text-white flex items-center justify-center font-extrabold text-xs shrink-0 dark:bg-white dark:text-zinc-950 group-hover:scale-105 transition-transform">
            {userProfile.avatarInitials || 'KR'}
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-zinc-900 truncate group-hover:text-zinc-950 dark:text-zinc-100 dark:group-hover:text-white">
              {userProfile.name}
            </div>
            <div className="flex items-center gap-1 text-[10px] text-zinc-500 font-mono font-medium dark:text-zinc-400 truncate">
              <Sparkles className="w-3 h-3 text-zinc-900 shrink-0 dark:text-zinc-100" />
              <span className="truncate">{userProfile.plan}</span>
            </div>
          </div>
        </div>

        <Tooltip content="Open Settings" position="top">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSettingsModalOpen(true);
            }}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-900 hover:bg-zinc-100 transition-colors dark:hover:text-zinc-100 dark:hover:bg-zinc-800 shrink-0"
          >
            <Settings className="w-4 h-4" />
          </button>
        </Tooltip>
      </div>
    </div>
  );
};

