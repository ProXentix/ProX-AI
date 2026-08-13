import { useState, useEffect, useCallback } from 'react';
import { useSettingsStore } from '../store/settingsStore';

export function useSpeech() {
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const { speechVoiceRate, speechVoicePitch } = useSettingsStore();

  const stopSpeech = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
    }
  }, []);

  const speakText = useCallback(
    (messageId: string, text: string) => {
      if (!('speechSynthesis' in window)) {
        alert('Text-to-Speech is not supported in this browser.');
        return;
      }

      if (speakingMessageId === messageId) {
        stopSpeech();
        return;
      }

      window.speechSynthesis.cancel();

      // Clean markdown symbols for natural speech reading
      const cleanText = text
        .replace(/```[\s\S]*?```/g, 'Code block omitted.')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/[#*_~$]/g, '')
        .trim();

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = speechVoiceRate;
      utterance.pitch = speechVoicePitch;

      utterance.onend = () => {
        setSpeakingMessageId(null);
      };

      utterance.onerror = () => {
        setSpeakingMessageId(null);
      };

      setSpeakingMessageId(messageId);
      window.speechSynthesis.speak(utterance);
    },
    [speakingMessageId, speechVoiceRate, speechVoicePitch, stopSpeech]
  );

  useEffect(() => {
    return () => {
      stopSpeech();
    };
  }, [stopSpeech]);

  return {
    speakingMessageId,
    speakText,
    stopSpeech,
  };
}
