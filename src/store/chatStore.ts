import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Conversation, Message, ModelId, ProjectFolder, SavedPrompt, UserProfileData, SettingsTab } from '../types/chat';
import { INITIAL_CONVERSATIONS } from '../services/mockResponses';
import { INITIAL_SAVED_PROMPTS } from '../constants/models';

const INITIAL_USER_PROFILE: UserProfileData = {
  name: 'ProgrammerKR',
  username: 'programmerkr',
  email: 'programmerkr@prox.ai',
  role: 'Senior AI & Software Architect',
  bio: 'Building next-gen AI applications with React 19, TypeScript & LLMs.',
  avatarInitials: 'KR',
  plan: 'Pro Unlimited',
  joinedDate: 'August 2026',
  customInstructions: {
    userContext: 'Senior software engineer specializing in frontend & fullstack web applications using React, TypeScript, Vite, Tailwind CSS, and Node.js.',
    responseStyle: 'Direct, modern, concise, and production-ready code examples with top-tier aesthetic UI/UX patterns.',
  },
  userApiKeys: [
    {
      id: 'key-1',
      name: 'Default Production Key',
      key: 'prox_sk_live_9f8a37d2b1c4e567890123456789abcd',
      createdAt: '2026-08-01',
      lastUsed: 'Just now',
    },
    {
      id: 'key-2',
      name: 'Development & Testing',
      key: 'prox_sk_test_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d',
      createdAt: '2026-08-03',
      lastUsed: '2 hours ago',
    },
  ],
  stats: {
    conversationsCount: 42,
    messagesCount: 384,
    tokensUsed: '2.4M',
    savedHours: 128,
  },
};

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  activeModelId: ModelId;
  folders: ProjectFolder[];
  savedPrompts: SavedPrompt[];
  searchQuery: string;
  isStreaming: boolean;
  streamingMessageId: string | null;
  sidebarOpen: boolean;
  pinnedDrawerOpen: boolean;
  settingsModalOpen: boolean;
  activeSettingsTab: SettingsTab;
  profileModalOpen: boolean;
  searchModalOpen: boolean;
  savedPromptsModalOpen: boolean;
  webSearchEnabled: boolean;
  activePersonaId: string;
  userProfile: UserProfileData;
  exploreOpen: boolean;

  // Actions
  setActiveConversation: (id: string | null) => void;
  setActiveModel: (modelId: ModelId) => void;
  createNewConversation: (folderId?: string | null) => string;
  deleteConversation: (id: string) => void;
  togglePinConversation: (id: string) => void;
  renameConversation: (id: string, newTitle: string) => void;
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => Message;
  updateMessageContent: (conversationId: string, messageId: string, content: string) => void;
  updateMessage: (conversationId: string, messageId: string, patch: Partial<Message>) => void;
  deleteMessage: (conversationId: string, messageId: string) => void;
  setStreaming: (isStreaming: boolean, messageId?: string | null) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  togglePinnedDrawer: () => void;
  setSettingsModalOpen: (open: boolean, tab?: SettingsTab) => void;
  setActiveSettingsTab: (tab: SettingsTab) => void;
  setProfileModalOpen: (open: boolean) => void;
  setSearchModalOpen: (open: boolean) => void;
  setSavedPromptsModalOpen: (open: boolean) => void;
  setSearchQuery: (query: string) => void;
  toggleWebSearch: () => void;
  setActivePersonaId: (id: string) => void;
  updateUserProfile: (updates: Partial<UserProfileData>) => void;
  setExploreOpen: (open: boolean) => void;

  addSavedPrompt: (prompt: Omit<SavedPrompt, 'id' | 'createdAt'>) => void;
  deleteSavedPrompt: (id: string) => void;
  addFolder: (name: string, color?: string) => void;
  deleteFolder: (id: string) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: INITIAL_CONVERSATIONS,
      activeConversationId: 'conv-react-19',
      activeModelId: 'neurix',
      folders: [
        { id: 'folder-tech', name: 'Engineering & Tech', color: '#10A37F', createdAt: '2026-08-01' },
        { id: 'folder-research', name: 'Deep Research', color: '#3B82F6', createdAt: '2026-08-02' },
      ],
      savedPrompts: INITIAL_SAVED_PROMPTS,
      searchQuery: '',
      isStreaming: false,
      streamingMessageId: null,
      sidebarOpen: true,
      pinnedDrawerOpen: false,
      settingsModalOpen: false,
      activeSettingsTab: 'profile',
      profileModalOpen: false,
      searchModalOpen: false,
      savedPromptsModalOpen: false,
      webSearchEnabled: false,
      activePersonaId: 'default',
      exploreOpen: false,
      userProfile: INITIAL_USER_PROFILE,

      setActiveConversation: (id) => set({ activeConversationId: id }),
      
      setActiveModel: (modelId) => set({ activeModelId: modelId }),


      createNewConversation: (folderId = null) => {
        const id = 'conv-' + Date.now();
        const newConv: Conversation = {
          id,
          title: 'New Conversation',
          folderId,
          modelId: get().activeModelId,
          isPinned: false,
          isArchived: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages: [],
        };

        set((state) => ({
          conversations: [newConv, ...state.conversations],
          activeConversationId: id,
        }));

        return id;
      },

      deleteConversation: (id) => {
        set((state) => {
          const nextConversations = state.conversations.filter((c) => c.id !== id);
          const nextActive = state.activeConversationId === id
            ? (nextConversations[0]?.id || null)
            : state.activeConversationId;
          return {
            conversations: nextConversations,
            activeConversationId: nextActive,
          };
        });
      },

      togglePinConversation: (id) => {
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === id ? { ...c, isPinned: !c.isPinned } : c
          ),
        }));
      },

      renameConversation: (id, newTitle) => {
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === id ? { ...c, title: newTitle, updatedAt: new Date().toISOString() } : c
          ),
        }));
      },

      addMessage: (conversationId, messageData) => {
        const newMessage: Message = {
          ...messageData,
          id: 'msg-' + Date.now() + '-' + Math.random().toString(36).substring(2, 7),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        set((state) => ({
          conversations: state.conversations.map((c) => {
            if (c.id !== conversationId) return c;
            // Auto generate conversation title if first user message
            const title = c.messages.length === 0 && messageData.role === 'user'
              ? (messageData.content.slice(0, 36) + (messageData.content.length > 36 ? '...' : ''))
              : c.title;

            return {
              ...c,
              title,
              updatedAt: new Date().toISOString(),
              messages: [...c.messages, newMessage],
            };
          }),
        }));

        return newMessage;
      },

      updateMessageContent: (conversationId, messageId, content) => {
        set((state) => ({
          conversations: state.conversations.map((c) => {
            if (c.id !== conversationId) return c;
            return {
              ...c,
              messages: c.messages.map((m) =>
                m.id === messageId ? { ...m, content } : m
              ),
            };
          }),
        }));
      },

      updateMessage: (conversationId, messageId, patch) => {
        set((state) => ({
          conversations: state.conversations.map((c) => {
            if (c.id !== conversationId) return c;
            return {
              ...c,
              messages: c.messages.map((m) =>
                m.id === messageId ? { ...m, ...patch } : m
              ),
            };
          }),
        }));
      },

      deleteMessage: (conversationId, messageId) => {
        set((state) => ({
          conversations: state.conversations.map((c) => {
            if (c.id !== conversationId) return c;
            return {
              ...c,
              messages: c.messages.filter((m) => m.id !== messageId),
            };
          }),
        }));
      },

      setStreaming: (isStreaming, messageId = null) =>
        set({ isStreaming, streamingMessageId: messageId }),

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      togglePinnedDrawer: () => set((state) => ({ pinnedDrawerOpen: !state.pinnedDrawerOpen })),

      setSettingsModalOpen: (open, tab) =>
        set((state) => ({
          settingsModalOpen: open,
          activeSettingsTab: tab || state.activeSettingsTab || 'profile',
        })),
      setActiveSettingsTab: (tab) => set({ activeSettingsTab: tab }),
      setProfileModalOpen: (open) => set({ settingsModalOpen: open, activeSettingsTab: 'profile' }),
      setSearchModalOpen: (open) => set({ searchModalOpen: open }),
      setSavedPromptsModalOpen: (open) => set({ savedPromptsModalOpen: open }),
      setExploreOpen: (open) => set({ exploreOpen: open }),

      setSearchQuery: (query) => set({ searchQuery: query }),
      toggleWebSearch: () => set((state) => ({ webSearchEnabled: !state.webSearchEnabled })),
      setActivePersonaId: (id) => set({ activePersonaId: id }),

      updateUserProfile: (updates) =>
        set((state) => ({
          userProfile: { ...state.userProfile, ...updates },
        })),

      addSavedPrompt: (promptData) => {
        const newPrompt: SavedPrompt = {
          ...promptData,
          id: 'sp-' + Date.now(),
          createdAt: new Date().toISOString().split('T')[0],
        };
        set((state) => ({ savedPrompts: [newPrompt, ...state.savedPrompts] }));
      },

      deleteSavedPrompt: (id) =>
        set((state) => ({ savedPrompts: state.savedPrompts.filter((p) => p.id !== id) })),

      addFolder: (name, color = '#10A37F') => {
        const newFolder: ProjectFolder = {
          id: 'folder-' + Date.now(),
          name,
          color,
          createdAt: new Date().toISOString(),
        };
        set((state) => ({ folders: [...state.folders, newFolder] }));
      },

      deleteFolder: (id) =>
        set((state) => ({
          folders: state.folders.filter((f) => f.id !== id),
          conversations: state.conversations.map((c) =>
            c.folderId === id ? { ...c, folderId: null } : c
          ),
        })),
    }),
    {
      name: 'prox-ai-chat-store',
      partialize: (state) => ({
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
        activeModelId: state.activeModelId,
        folders: state.folders,
        savedPrompts: state.savedPrompts,
        webSearchEnabled: state.webSearchEnabled,
        activePersonaId: state.activePersonaId,
        userProfile: state.userProfile,
      }),
    }
  )
);

