export type Role = 'user' | 'assistant' | 'system';

export type ModelId = 
  | 'neurix'
  | 'logix'
  | 'optix';

export interface ModelCapability {
  vision: boolean;
  webSearch: boolean;
  codeExecution: boolean;
  reasoning: boolean;
  contextWindow: string;
}

export interface ModelInfo {
  id: ModelId;
  name: string;
  provider: 'OpenAI' | 'Anthropic' | 'Google' | 'DeepSeek' | 'Meta' | 'ProX AI';
  description: string;
  badge?: string;
  icon: string; // Lucide icon name or emoji
  capabilities: ModelCapability;
  isPopular?: boolean;
  isNew?: boolean;
}

export interface Citation {
  id: string;
  title: string;
  url: string;
  snippet: string;
  domain: string;
  favIcon?: string;
}

export interface ReasoningStep {
  id: string;
  title: string;
  content: string;
  timestamp?: string;
  durationMs?: number;
}

export interface Attachment {
  id: string;
  name: string;
  size: number;
  type: 'image' | 'code' | 'pdf' | 'text' | 'archive';
  url?: string;
  previewUrl?: string;
}

export interface Message {
  id: string;
  conversationId: string;
  role: Role;
  content: string;
  timestamp: string;
  modelId?: ModelId;
  reasoning?: {
    thinkingTimeSeconds?: number;
    steps: ReasoningStep[];
  };
  citations?: Citation[];
  attachments?: Attachment[];
  isStreaming?: boolean;
  isError?: boolean;
  rating?: 'like' | 'dislike' | null;
  feedbackText?: string;
  parentId?: string; // For thread branching
  isPinned?: boolean;
}

export interface ProjectFolder {
  id: string;
  name: string;
  color: string;
  icon?: string;
  createdAt: string;
}

export interface ProjectItem {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  shared?: boolean;
  memoryOption?: string;
  conversationsCount?: number;
  sourcesCount?: number;
}

export interface Conversation {
  id: string;
  title: string;
  folderId?: string | null;
  modelId: ModelId;
  systemPrompt?: string;
  isPinned: boolean;
  isArchived: boolean;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
  tokenCount?: number;
}

export interface SavedPrompt {
  id: string;
  title: string;
  content: string;
  category: 'Coding' | 'Writing' | 'Analysis' | 'Productivity' | 'Custom';
  shortcut?: string;
  tags: string[];
  createdAt: string;
}

export interface SystemPersona {
  id: string;
  name: string;
  description: string;
  prompt: string;
  icon: string;
}

export interface UserApiKey {
  id: string;
  name: string;
  key: string;
  createdAt: string;
  lastUsed: string;
}

export interface UserProfileData {
  name: string;
  username: string;
  email: string;
  role: string;
  bio: string;
  avatarInitials: string;
  avatarUrl?: string;
  plan: string;
  joinedDate: string;
  customInstructions: {
    userContext: string;
    responseStyle: string;
  };
  userApiKeys: UserApiKey[];
  stats: {
    conversationsCount: number;
    messagesCount: number;
    tokensUsed: string;
    savedHours: number;
  };
}


export interface AIAgent {
  id: string;
  name: string;
  role: string;
  description: string;
  systemPrompt: string;
  category: 'Development' | 'Data & Research' | 'Writing & Content' | 'Security & DevOps' | 'Design & Strategy' | 'Custom';
  avatar: string;
  modelId: ModelId;
  capabilities: string[];
  gradient: string;
  bg: string;
  border: string;
  isPopular?: boolean;
  isCustom?: boolean;
  starterPrompts: string[];
}

export type SettingsTab =
  | 'profile'
  | 'instructions'
  | 'apikeys'
  | 'subscription'
  | 'privacy'
  | 'general'
  | 'appearance'
  | 'ai'
  | 'shortcuts';




