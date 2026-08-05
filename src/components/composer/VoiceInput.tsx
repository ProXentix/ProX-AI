import React, { useState } from 'react';
import { Mic, Square } from 'lucide-react';
import { Tooltip } from '../ui/Tooltip';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript }) => {
  const [isRecording, setIsRecording] = useState(false);

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      setTimeout(() => {
        onTranscript('Explain React 19 server actions and performance optimizations.');
        setIsRecording(false);
      }, 3500);
    } else {
      setIsRecording(false);
    }
  };

  return (
    <div className="relative flex items-center">
      <Tooltip content={isRecording ? 'Stop Recording' : 'Voice Input'}>
        <button
          type="button"
          onClick={toggleRecording}
          className={`p-2 rounded-xl transition-all ${
            isRecording
              ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30 animate-pulse'
              : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-zinc-800'
          }`}
        >
          {isRecording ? <Square className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>
      </Tooltip>

      {isRecording && (
        <span className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 px-2.5 py-1 rounded-lg bg-rose-600 text-white text-[11px] font-medium whitespace-nowrap shadow-lg animate-bounce">
          Listening... (speak now)
        </span>
      )}
    </div>
  );
};
