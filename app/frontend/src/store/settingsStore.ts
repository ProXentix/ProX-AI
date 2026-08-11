import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark' | 'system';
export type FontSizeOption = 'sm' | 'base' | 'lg';

interface SettingsState {
  theme: ThemeMode;
  fontSize: FontSizeOption;
  showLineNumbers: boolean;
  enableWordWrap: boolean;
  streamingSpeedMs: number;
  soundEffectsEnabled: boolean;
  autoScrollEnabled: boolean;
  speechVoiceRate: number;
  speechVoicePitch: number;

  // Actions
  setTheme: (theme: ThemeMode) => void;
  setFontSize: (size: FontSizeOption) => void;
  setShowLineNumbers: (show: boolean) => void;
  setEnableWordWrap: (wrap: boolean) => void;
  setStreamingSpeedMs: (speed: number) => void;
  setSoundEffectsEnabled: (enabled: boolean) => void;
  setAutoScrollEnabled: (enabled: boolean) => void;
  setSpeechVoiceRate: (rate: number) => void;
  setSpeechVoicePitch: (pitch: number) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'dark', // Default to dark theme
      fontSize: 'base',
      showLineNumbers: true,
      enableWordWrap: true,
      streamingSpeedMs: 20,
      soundEffectsEnabled: true,
      autoScrollEnabled: true,
      speechVoiceRate: 1.0,
      speechVoicePitch: 1.0,

      setTheme: (theme) => set({ theme }),
      setFontSize: (fontSize) => set({ fontSize }),
      setShowLineNumbers: (showLineNumbers) => set({ showLineNumbers }),
      setEnableWordWrap: (enableWordWrap) => set({ enableWordWrap }),
      setStreamingSpeedMs: (streamingSpeedMs) => set({ streamingSpeedMs }),
      setSoundEffectsEnabled: (soundEffectsEnabled) => set({ soundEffectsEnabled }),
      setAutoScrollEnabled: (autoScrollEnabled) => set({ autoScrollEnabled }),
      setSpeechVoiceRate: (speechVoiceRate) => set({ speechVoiceRate }),
      setSpeechVoicePitch: (speechVoicePitch) => set({ speechVoicePitch }),
    }),
    {
      name: 'prox-ai-settings-store',
    }
  )
);
