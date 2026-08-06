import React, { useRef, useEffect } from 'react';
import { PanelLeft } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { useSettingsStore } from '../../store/settingsStore';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { WelcomeScreen } from './WelcomeScreen';
import { PromptComposer } from '../composer/PromptComposer';
import { Tooltip } from '../ui/Tooltip';
import { ModelSelector } from '../ui/ModelSelector';
import { generateStreamResponse } from '../../services/aiService';
import { Attachment } from '../../types/chat';

export const ChatArea: React.FC = () => {
  const {
    sidebarOpen,
    toggleSidebar,
    conversations,
    activeConversationId,
    activeModelId,
    webSearchEnabled,
    addMessage,
    updateMessageContent,
    updateMessage,
    isStreaming,
    setStreaming,
  } = useChatStore();

  const { autoScrollEnabled } = useSettingsStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const activeConv = conversations.find((c) => c.id === activeConversationId);
  const messages = activeConv?.messages || [];

  // Auto scroll effect
  useEffect(() => {
    if (autoScrollEnabled && messages.length > 0) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length, messages[messages.length - 1]?.content, autoScrollEnabled]);

  // Listen for prompt send event (e.g. from Explore Page)
  useEffect(() => {
    const handleSendPromptEvent = (e: Event) => {
      const customEv = e as CustomEvent<{ text: string }>;
      if (customEv.detail?.text) {
        handleSendMessage(customEv.detail.text, []);
      }
    };
    window.addEventListener('prox:send-prompt', handleSendPromptEvent);
    return () => {
      window.removeEventListener('prox:send-prompt', handleSendPromptEvent);
    };
  }, [activeConversationId]);

  const handleSendMessage = async (text: string, attachments: Attachment[]) => {
    if (!activeConversationId) return;

    // 1. Add User Message
    addMessage(activeConversationId, {
      conversationId: activeConversationId,
      role: 'user',
      content: text,
      attachments,
    });

    // 2. Add Initial Assistant Streaming Placeholder Message
    const assistantMsg = addMessage(activeConversationId, {
      conversationId: activeConversationId,
      role: 'assistant',
      content: '',
      modelId: activeModelId,
      isStreaming: true,
      reasoning: { steps: [] },
      citations: [],
    });

    setStreaming(true, assistantMsg.id);

    // 3. Initiate Stream
    abortControllerRef.current = new AbortController();
    let accumulatedContent = '';

    await generateStreamResponse(
      text,
      activeModelId,
      webSearchEnabled,
      {
        onReasoningStep: (step) => {
          updateMessage(activeConversationId, assistantMsg.id, {
            reasoning: {
              thinkingTimeSeconds: 2.1,
              steps: [
                ...(activeConv?.messages.find((m) => m.id === assistantMsg.id)?.reasoning?.steps || []),
                step,
              ],
            },
          });
        },
        onCitations: (citations) => {
          updateMessage(activeConversationId, assistantMsg.id, { citations });
        },
        onToken: (token) => {
          accumulatedContent += token;
          updateMessageContent(activeConversationId, assistantMsg.id, accumulatedContent);
        },
        onComplete: () => {
          updateMessage(activeConversationId, assistantMsg.id, { isStreaming: false });
          setStreaming(false, null);
        },
        onError: () => {
          updateMessage(activeConversationId, assistantMsg.id, {
            isStreaming: false,
            isError: true,
          });
          setStreaming(false, null);
        },
      },
      abortControllerRef.current.signal
    );
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setStreaming(false, null);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full relative overflow-hidden bg-white dark:bg-zinc-950">
      {/* Top Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-zinc-100 dark:border-zinc-800/70 shrink-0">
        {/* Left: Sidebar toggle + Model Selector */}
        <div className="flex items-center gap-2 min-w-0">
          <button
            onClick={toggleSidebar}
            className={`${!sidebarOpen ? 'block' : 'block md:hidden'} p-2 rounded-xl text-zinc-500 hover:text-zinc-900 bg-zinc-100 hover:bg-zinc-200/80 border border-zinc-200 shadow-xs transition-colors dark:text-zinc-400 dark:hover:text-zinc-100 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:border-zinc-800 shrink-0`}
            title="Toggle Sidebar"
          >
            <PanelLeft className="w-4 h-4" />
          </button>
          <ModelSelector />
        </div>
        {/* Right: empty for now */}
        <div />
      </div>

      {/* Scrollable Message Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <WelcomeScreen onSelectPrompt={(promptText) => handleSendMessage(promptText, [])} />
          ) : (
            messages.map((msg) =>
              msg.role === 'user' ? (
                <UserMessage key={msg.id} message={msg} />
              ) : (
                <AssistantMessage
                  key={msg.id}
                  message={msg}
                  onRetry={() => {
                    const prevUserMsg = [...messages]
                      .reverse()
                      .find((m) => m.role === 'user');
                    if (prevUserMsg) {
                      handleSendMessage(prevUserMsg.content, prevUserMsg.attachments || []);
                    }
                  }}
                />
              )
            )
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Floating Prompt Composer */}
      <PromptComposer
        onSendMessage={handleSendMessage}
        onStopGeneration={handleStopGeneration}
        isStreaming={isStreaming}
      />
    </div>
  );
};
