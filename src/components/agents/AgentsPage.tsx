import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bot,
  Sparkles,
  ArrowLeft,
  Search,
  Plus,
  Cpu,
  ShieldCheck,
  Zap,
  Code2,
  Terminal,
  Database,
  PenTool,
  BrainCircuit,
  ArrowRight,
  Trash2,
} from 'lucide-react';
import { AIAgent, ModelId } from '../../types/chat';
import { useChatStore } from '../../store/chatStore';
import { Modal } from '../ui/Modal';
import { toast } from 'sonner';

interface AgentsPageProps {
  onLaunchAgent: (agent: AIAgent, prompt?: string) => void;
  onClose: () => void;
}

const PREBUILT_AGENTS: AIAgent[] = [
  {
    id: 'agent-fullstack',
    name: 'Full-Stack Architect',
    role: 'System Architecture & Next.js Expert',
    description: 'Specializes in React 19, TypeScript, Next.js 14, Prisma ORM, API design & scalable web architecture.',
    systemPrompt: 'You are a Senior Full-Stack Architect specializing in React 19, Next.js 14, TypeScript, Prisma, and Tailwind CSS. Provide production-ready code with top-tier UI/UX aesthetics.',
    category: 'Development',
    avatar: 'Code2',
    modelId: 'neurix',
    capabilities: ['Code Generation', 'System Architecture', 'React 19 & Next.js', 'Database Schema'],
    gradient: 'from-blue-600 to-cyan-600',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800/50',
    isPopular: true,
    starterPrompts: [
      'Design a production-ready Next.js 14 app with auth, Prisma ORM, and Tailwind CSS.',
      'Refactor this component for optimal React 19 performance and accessibility.',
      'Create a complete REST & GraphQL API schema for an e-commerce platform.',
    ],
  },
  {
    id: 'agent-logix-cot',
    name: 'Logix Reasoning Engine',
    role: 'CoT Math & Algorithmic Logic',
    description: 'Employs multi-step chain-of-thought reasoning for math proofs, algorithm optimization, and complex bug isolation.',
    systemPrompt: 'You are the Logix Deep Reasoning Agent. Break down every problem step-by-step using rigorous logic, verification stages, and explicit mathematical trade-offs.',
    category: 'Data & Research',
    avatar: 'BrainCircuit',
    modelId: 'logix',
    capabilities: ['Chain-of-Thought', 'Math & Derivations', 'Algorithm Optimization', 'Deep Debugging'],
    gradient: 'from-purple-600 to-indigo-600',
    bg: 'bg-purple-50 dark:bg-purple-950/30',
    border: 'border-purple-200 dark:border-purple-800/50',
    isPopular: true,
    starterPrompts: [
      'Solve and explain the dynamic programming solution for the Traveling Salesperson Problem.',
      'Derive the mathematical proof for gradient descent with momentum.',
      'Identify hidden race conditions in a concurrent async Go/Node.js pipeline.',
    ],
  },
  {
    id: 'agent-devops',
    name: 'DevOps & Infrastructure',
    role: 'Docker, K8s & Terraform Specialist',
    description: 'Expert in multi-stage Dockerfiles, Kubernetes manifests, GitHub Actions CI/CD pipelines & cloud automation.',
    systemPrompt: 'You are a Senior DevOps & Cloud Infrastructure Engineer. Provide secure, battle-tested Dockerfiles, K8s manifests, Terraform code, and CI/CD pipelines.',
    category: 'Security & DevOps',
    avatar: 'Terminal',
    modelId: 'optix',
    capabilities: ['Docker & K8s', 'Terraform & AWS', 'CI/CD Pipelines', 'Linux Sysadmin'],
    gradient: 'from-amber-500 to-orange-600',
    bg: 'bg-amber-50 dark:bg-amber-950/30',
    border: 'border-amber-200 dark:border-amber-800/50',
    starterPrompts: [
      'Write a production Dockerfile and multi-stage build setup for a Node.js TypeScript API.',
      'Design a Kubernetes deployment manifest with HPA, ingress, and secret management.',
      'Create a GitHub Actions CI/CD workflow for automated linting, testing, and deployment.',
    ],
  },
  {
    id: 'agent-security',
    name: 'Cybersecurity Auditor',
    role: 'OWASP Security & Vulnerability Auditor',
    description: 'Audits code for SQL injection, XSS, CSRF, insecure token storage, and OWASP top 10 vulnerabilities.',
    systemPrompt: 'You are a Lead Cybersecurity Auditor & Penetration Tester. Analyze code for security vulnerabilities, OWASP Top 10 risks, and suggest hardened remediation.',
    category: 'Security & DevOps',
    avatar: 'ShieldCheck',
    modelId: 'logix',
    capabilities: ['Vulnerability Scan', 'OWASP Top 10', 'JWT & OAuth Audit', 'Hardening Checklists'],
    gradient: 'from-rose-600 to-red-600',
    bg: 'bg-rose-50 dark:bg-rose-950/30',
    border: 'border-rose-200 dark:border-rose-800/50',
    starterPrompts: [
      'Perform a security audit on a JWT authentication flow and suggest security hardening.',
      'Check this SQL query and API endpoint for injection and authorization bypass risks.',
      'Write a security checklist for deploying a production microservice.',
    ],
  },
  {
    id: 'agent-datascience',
    name: 'Data Science & Analytics',
    role: 'Pandas, ML & Data Pipelines',
    description: 'Processes datasets, writes pandas/numpy pipelines, builds statistical models & generates visual plots.',
    systemPrompt: 'You are a Senior Data Scientist & Analytics Engineer. Write efficient Python pandas/numpy scripts, SQL queries, and data visualization pipelines.',
    category: 'Data & Research',
    avatar: 'Database',
    modelId: 'neurix',
    capabilities: ['Pandas & NumPy', 'Data Cleaning', 'SQL Analytics', 'Machine Learning'],
    gradient: 'from-emerald-500 to-teal-600',
    bg: 'bg-emerald-50 dark:bg-emerald-950/30',
    border: 'border-emerald-200 dark:border-emerald-800/50',
    starterPrompts: [
      'Write a Python pandas script to clean missing values and detect anomalies in financial data.',
      'Create an ETL pipeline with data transformation and data visualization.',
      'Build a scikit-learn machine learning classification pipeline with feature engineering.',
    ],
  },
  {
    id: 'agent-product',
    name: 'UI/UX & Product Manager',
    role: 'PRDs, Wireframes & Strategy',
    description: 'Crafts detailed PRDs, user personas, wireframe design systems, and product roadmaps.',
    systemPrompt: 'You are a Lead Product Manager & UI/UX Strategist. Write clear PRDs, user stories, acceptance criteria, and Tailwind UI component specifications.',
    category: 'Design & Strategy',
    avatar: 'PenTool',
    modelId: 'optix',
    capabilities: ['PRD Writing', 'UI/UX Systems', 'User Stories', 'Feature Roadmaps'],
    gradient: 'from-indigo-500 to-blue-600',
    bg: 'bg-indigo-50 dark:bg-indigo-950/30',
    border: 'border-indigo-200 dark:border-indigo-800/50',
    starterPrompts: [
      'Draft a complete PRD for an AI-powered note-taking app with user personas and criteria.',
      'Create a modern dark/light Tailwind CSS design system with HSL color tokens.',
      'Define the user flow and interactive state transitions for a multi-step checkout funnel.',
    ],
  },
];

export const AgentsPage: React.FC<AgentsPageProps> = ({ onLaunchAgent, onClose }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('All');
  const [selectedAgent, setSelectedAgent] = useState<AIAgent | null>(null);

  // Custom Agent Modal Form State
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentRole, setNewAgentRole] = useState('');
  const [newAgentDesc, setNewAgentDesc] = useState('');
  const [newAgentSystemPrompt, setNewAgentSystemPrompt] = useState('');
  const [newAgentModel, setNewAgentModel] = useState<ModelId>('neurix');
  const [newAgentPrompt1, setNewAgentPrompt1] = useState('');

  const { customAgents, addCustomAgent, deleteCustomAgent } = useChatStore();

  const allAgents = [...customAgents, ...PREBUILT_AGENTS];

  const categories = [
    'All',
    'Development',
    'Data & Research',
    'Security & DevOps',
    'Design & Strategy',
    'Custom',
  ];

  const filteredAgents = allAgents.filter((agent) => {
    const matchesCategory =
      activeCategory === 'All'
        ? true
        : activeCategory === 'Custom'
        ? agent.isCustom
        : agent.category === activeCategory;

    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  const handleCreateAgentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAgentName.trim() || !newAgentSystemPrompt.trim()) return;

    addCustomAgent({
      name: newAgentName.trim(),
      role: newAgentRole.trim() || 'Custom AI Specialist',
      description: newAgentDesc.trim() || 'Custom user-created autonomous AI agent.',
      systemPrompt: newAgentSystemPrompt.trim(),
      category: 'Development',
      avatar: 'Bot',
      modelId: newAgentModel,
      capabilities: ['Custom Persona', 'Tailored System Instructions', 'Domain Specialist'],
      gradient: 'from-blue-600 to-indigo-600',
      bg: 'bg-blue-50 dark:bg-blue-950/30',
      border: 'border-blue-200 dark:border-blue-800/50',
      starterPrompts: newAgentPrompt1.trim() ? [newAgentPrompt1.trim()] : ['Hello agent, please introduce your capabilities.'],
    });

    toast.success(`Custom Agent "${newAgentName.trim()}" created!`);
    setNewAgentName('');
    setNewAgentRole('');
    setNewAgentDesc('');
    setNewAgentSystemPrompt('');
    setNewAgentPrompt1('');
    setCreateModalOpen(false);
  };

  const renderAgentIcon = (iconName: string) => {
    switch (iconName) {
      case 'Code2':
        return <Code2 className="w-5 h-5" />;
      case 'BrainCircuit':
        return <BrainCircuit className="w-5 h-5" />;
      case 'Terminal':
        return <Terminal className="w-5 h-5" />;
      case 'ShieldCheck':
        return <ShieldCheck className="w-5 h-5" />;
      case 'Database':
        return <Database className="w-5 h-5" />;
      case 'PenTool':
        return <PenTool className="w-5 h-5" />;
      default:
        return <Bot className="w-5 h-5" />;
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-white dark:bg-zinc-950 h-full select-none">
      {/* Top Sticky Header */}
      <div className="sticky top-0 z-10 bg-white/90 dark:bg-zinc-950/90 backdrop-blur-md border-b border-zinc-100 dark:border-zinc-800 px-6 py-4">
        <div className="w-full flex items-center justify-between gap-4">
          {/* Left: Back Button */}
          <button
            onClick={onClose}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-zinc-900 bg-zinc-100 hover:bg-zinc-200/80 border border-zinc-200/80 transition-all dark:text-zinc-300 dark:hover:text-zinc-100 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:border-zinc-800 shrink-0 shadow-2xs"
            title="Back to Chat"
          >
            <ArrowLeft className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span className="hidden sm:inline">Back</span>
          </button>

          {/* Center: Title */}
          <div className="text-center min-w-0 flex-1">
            <h1 className="text-xl sm:text-2xl font-extrabold text-zinc-900 dark:text-zinc-100 flex items-center justify-center gap-2 tracking-tight">
              <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              AI Agent Hub
            </h1>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 font-medium truncate">
              Autonomous AI Assistants tailored for Code, Research, DevOps & Strategy
            </p>
          </div>

          {/* Right: Search & Create Agent Button */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="relative w-36 sm:w-52">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-400" />
              <input
                type="text"
                placeholder="Search agents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 rounded-xl text-xs bg-zinc-100 border border-zinc-200 text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-blue-500 dark:bg-zinc-900 dark:border-zinc-700 dark:text-zinc-100 dark:placeholder-zinc-500 shadow-2xs"
              />
            </div>

            <button
              onClick={() => setCreateModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-xs transition-all shrink-0"
            >
              <Plus className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Agent</span>
            </button>
          </div>
        </div>

        {/* Category Filters */}
        <div className="max-w-5xl mx-auto flex items-center justify-center gap-2 mt-4 flex-wrap">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                activeCategory === cat
                  ? 'bg-zinc-950 text-white dark:bg-white dark:text-zinc-950 font-semibold shadow-xs'
                  : 'bg-zinc-100 text-zinc-600 hover:text-zinc-900 border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid View */}
      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Spotlight Banner */}
        <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-md flex items-center justify-between gap-4 flex-wrap">
          <div className="space-y-1 max-w-xl">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-white/20 text-[10px] font-bold tracking-wider uppercase backdrop-blur-md">
              <Sparkles className="w-3 h-3" /> Autonomous Workflows
            </span>
            <h2 className="text-lg font-bold">Deploy Persona-Trained AI Agents</h2>
            <p className="text-xs text-blue-100 leading-relaxed">
              Launch pre-configured specialized AI agents with tailored system instructions, tool capabilities, and CoT reasoning pipelines.
            </p>
          </div>

          <button
            onClick={() => setCreateModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-white text-zinc-950 hover:bg-zinc-100 font-bold text-xs shadow-sm transition-all flex items-center gap-1.5 shrink-0"
          >
            <Plus className="w-4 h-4 text-blue-600" />
            <span>Create Custom Agent</span>
          </button>
        </div>

        {/* Agents Grid */}
        <div>
          <h2 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-500" />
            <span>Available Agents ({filteredAgents.length})</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAgents.map((agent, i) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={`group relative p-4 rounded-2xl text-left border ${agent.bg} ${agent.border} hover:shadow-md transition-all flex flex-col justify-between`}
              >
                <div>
                  {/* Top Bar: Icon, Badges & Delete if custom */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div
                      className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.gradient} text-white flex items-center justify-center shadow-xs shrink-0`}
                    >
                      {renderAgentIcon(agent.avatar)}
                    </div>

                    <div className="flex items-center gap-1.5">
                      {agent.isCustom && (
                        <span className="px-2 py-0.5 rounded-md bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400 text-[10px] font-bold border border-blue-200 dark:border-blue-800">
                          Custom
                        </span>
                      )}
                      {agent.isPopular && (
                        <span className="px-2 py-0.5 rounded-md bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400 text-[10px] font-bold border border-amber-200 dark:border-amber-800">
                          🔥 Popular
                        </span>
                      )}
                      {agent.isCustom && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteCustomAgent(agent.id);
                            toast.success(`Agent "${agent.name}" deleted.`);
                          }}
                          className="p-1 rounded-lg text-zinc-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                          title="Delete Custom Agent"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  <h3 className="text-sm font-extrabold text-zinc-900 dark:text-zinc-100 tracking-tight">
                    {agent.name}
                  </h3>
                  <p className="text-[11px] font-semibold text-blue-600 dark:text-blue-400 mb-1.5">
                    {agent.role}
                  </p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2 leading-relaxed mb-3">
                    {agent.description}
                  </p>

                  {/* Capabilities Tags */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {agent.capabilities.slice(0, 3).map((cap: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded-md bg-white/80 dark:bg-zinc-900/80 border border-zinc-200 dark:border-zinc-800 text-[10px] font-medium text-zinc-600 dark:text-zinc-400"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Bottom Action Button */}
                <div className="pt-2 border-t border-zinc-200/60 dark:border-zinc-800/60 flex items-center justify-between gap-2">
                  <span className="text-[10px] font-mono text-zinc-400 uppercase font-semibold">
                    Model: {agent.modelId}
                  </span>

                  <button
                    onClick={() => setSelectedAgent(agent)}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-black text-white dark:bg-white dark:hover:bg-zinc-100 dark:text-zinc-950 font-bold text-xs transition-all shadow-2xs"
                  >
                    <span>Launch Agent</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* AGENT LAUNCH / DETAILS MODAL */}
      {selectedAgent && (
        <Modal
          isOpen={!!selectedAgent}
          onClose={() => setSelectedAgent(null)}
          title={
            <div className="flex items-center gap-2">
              <Bot className="w-4.5 h-4.5 text-blue-600 dark:text-blue-400" />
              <span>{selectedAgent.name} Agent Setup</span>
            </div>
          }
          maxWidth="md"
        >
          <div className="space-y-4 text-xs">
            <div className="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800 space-y-2">
              <div className="flex items-center gap-2 font-bold text-zinc-900 dark:text-zinc-100 text-sm">
                <span>{selectedAgent.name}</span>
                <span className="text-xs font-normal text-blue-600 dark:text-blue-400">({selectedAgent.role})</span>
              </div>
              <p className="text-zinc-600 dark:text-zinc-300">{selectedAgent.description}</p>
            </div>

            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
                System Persona Instructions
              </label>
              <div className="p-3 rounded-xl bg-zinc-900 text-zinc-200 font-mono text-[11px] leading-relaxed border border-zinc-800 max-h-28 overflow-y-auto">
                {selectedAgent.systemPrompt}
              </div>
            </div>

            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1.5">
                Starter Prompts (Click to run):
              </label>
              <div className="space-y-1.5">
                {selectedAgent.starterPrompts.map((promptText, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      onLaunchAgent(selectedAgent, promptText);
                      setSelectedAgent(null);
                    }}
                    className="w-full p-2.5 rounded-xl bg-white hover:bg-blue-50 border border-zinc-200 hover:border-blue-300 dark:bg-zinc-950 dark:hover:bg-blue-950/40 dark:border-zinc-800 text-left transition-all flex items-center justify-between gap-2 group"
                  >
                    <span className="text-zinc-700 dark:text-zinc-300 font-medium group-hover:text-blue-700 dark:group-hover:text-blue-300">
                      {promptText}
                    </span>
                    <ArrowRight className="w-3.5 h-3.5 text-zinc-400 group-hover:text-blue-600 shrink-0" />
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-200 dark:border-zinc-800">
              <button
                type="button"
                onClick={() => setSelectedAgent(null)}
                className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  onLaunchAgent(selectedAgent);
                  setSelectedAgent(null);
                }}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs"
              >
                <Zap className="w-3.5 h-3.5" />
                <span>Launch Empty Chat</span>
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* CREATE CUSTOM AGENT MODAL */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <Plus className="w-4.5 h-4.5 text-blue-600 dark:text-blue-400" />
            <span>Create Custom AI Agent</span>
          </div>
        }
        maxWidth="md"
      >
        <form onSubmit={handleCreateAgentSubmit} className="space-y-3.5 text-xs">
          <div>
            <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
              Agent Name *
            </label>
            <input
              type="text"
              placeholder="e.g. Python Security Auditor, React Refactor Agent..."
              value={newAgentName}
              onChange={(e) => setNewAgentName(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
              required
              autoFocus
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">Role / Subtitle</label>
              <input
                type="text"
                placeholder="e.g. Senior Security Auditor"
                value={newAgentRole}
                onChange={(e) => setNewAgentRole(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">AI Engine Model</label>
              <select
                value={newAgentModel}
                onChange={(e) => setNewAgentModel(e.target.value as ModelId)}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
              >
                <option value="neurix">Neurix (High-Speed Multimodal)</option>
                <option value="logix">Logix (Deep Chain-of-Thought)</option>
                <option value="optix">Optix (Creative & Code Spec)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
              Short Description
            </label>
            <input
              type="text"
              placeholder="e.g. Audits Python scripts for security flaws and performance leaks."
              value={newAgentDesc}
              onChange={(e) => setNewAgentDesc(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
            />
          </div>

          <div>
            <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
              Custom System Instructions (Persona Prompt) *
            </label>
            <textarea
              rows={3}
              placeholder="e.g. You are a Senior Security Engineer. Audit all input code for security flaws, memory leaks, and performance bottlenecks..."
              value={newAgentSystemPrompt}
              onChange={(e) => setNewAgentSystemPrompt(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 font-mono text-[11px]"
              required
            />
          </div>

          <div>
            <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
              Starter Prompt Example
            </label>
            <input
              type="text"
              placeholder="e.g. Audit my authentication pipeline for OWASP top 10 risks."
              value={newAgentPrompt1}
              onChange={(e) => setNewAgentPrompt1(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-200 dark:border-zinc-800">
            <button
              type="button"
              onClick={() => setCreateModalOpen(false)}
              className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Save Agent</span>
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
