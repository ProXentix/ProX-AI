import { ModelInfo, SystemPersona, SavedPrompt } from '../types/chat';

export const AI_MODELS: ModelInfo[] = [
  {
    id: 'neurix',
    name: 'Neurix',
    provider: 'ProX AI',
    description: 'General-purpose AI for everyday tasks, conversation, writing, and broad knowledge.',
    badge: 'General AI',
    icon: 'Sparkles',
    isPopular: true,
    capabilities: {
      vision: false,
      webSearch: true,
      codeExecution: true,
      reasoning: true,
      contextWindow: '256k',
    },
  },
  {
    id: 'logix',
    name: 'Logix',
    provider: 'ProX AI',
    description: 'Specialized for complex coding, deep reasoning, algorithms, and step-by-step logic.',
    badge: 'Coding & Reasoning',
    icon: 'BrainCircuit',
    isNew: true,
    capabilities: {
      vision: false,
      webSearch: true,
      codeExecution: true,
      reasoning: true,
      contextWindow: '128k',
    },
  },
  {
    id: 'optix',
    name: 'Optix',
    provider: 'ProX AI',
    description: 'Multimodal vision model for image understanding, generation, and visual analysis.',
    badge: 'Images & Vision',
    icon: 'Cpu',
    capabilities: {
      vision: true,
      webSearch: false,
      codeExecution: false,
      reasoning: true,
      contextWindow: '64k',
    },
  },
];

export const SYSTEM_PERSONAS: SystemPersona[] = [
  {
    id: 'default',
    name: 'Standard AI Assistant',
    description: 'Helpful, precise, clear, and balanced response style.',
    prompt: 'You are ProX AI, a helpful, precise, and highly capable AI assistant.',
    icon: 'Bot',
  },
  {
    id: 'developer',
    name: 'Senior Software Engineer',
    description: 'Provides clean, production-ready code with concise technical explanations.',
    prompt: 'You are an elite Staff Software Engineer. Write clean, modern, well-typed, and high-performance code with minimal boilerplate.',
    icon: 'Code2',
  },
  {
    id: 'creative',
    name: 'Creative Content Writer',
    description: 'Engaging, vivid storytelling and polished prose.',
    prompt: 'You are a world-class editor and writer. Craft elegant, persuasive, and beautifully formatted text.',
    icon: 'PenTool',
  },
  {
    id: 'academic',
    name: 'Research & Math Scholar',
    description: 'Rigorous explanations with formulas, citations, and step-by-step logic.',
    prompt: 'You are a Senior Scientist and Mathematician. Use clear step-by-step reasoning, LaTeX formulas, and rigorous analytical clarity.',
    icon: 'GraduationCap',
  },
];

export const INITIAL_SAVED_PROMPTS: SavedPrompt[] = [
  {
    id: 'sp-1',
    title: 'Code Refactor & Optimize',
    content: 'Review the following code for performance bottlenecks, edge cases, and modern React 19 / TypeScript best practices:\n\n```ts\n// paste code here\n```',
    category: 'Coding',
    shortcut: '/refactor',
    tags: ['react', 'typescript', 'clean-code'],
    createdAt: '2026-08-01',
  },
  {
    id: 'sp-2',
    title: 'Architectural System Design',
    content: 'Design a high-scale microservices architecture for real-time notification streaming. Provide Mermaid sequence and architecture diagrams.',
    category: 'Analysis',
    shortcut: '/sysdesign',
    tags: ['architecture', 'mermaid', 'backend'],
    createdAt: '2026-08-02',
  },
  {
    id: 'sp-3',
    title: 'Executive Summary Brief',
    content: 'Summarize the following document into 5 key bullet points, key takeaways, and action items for leadership:\n\n',
    category: 'Productivity',
    shortcut: '/summary',
    tags: ['summary', 'executive', 'notes'],
    createdAt: '2026-08-03',
  },
];
