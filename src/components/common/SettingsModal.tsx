import React, { useState, useEffect } from 'react';
import {
  Settings,
  Sliders,
  Moon,
  Zap,
  Keyboard,
  Check,
  User,
  Brain,
  Key,
  CreditCard,
  Shield,
  Sparkles,
  MessageSquare,
  MessageCircle,
  Clock,
  Save,
  Eye,
  EyeOff,
  CheckCircle2,
  Download,
  Trash2,
  Plus,
  Copy,
  AlertTriangle,
  Pencil,
  Quote,
  RotateCcw,
} from 'lucide-react';
import { Modal } from '../ui/Modal';
import { useChatStore } from '../../store/chatStore';
import { useSettingsStore } from '../../store/settingsStore';
import { SYSTEM_PERSONAS } from '../../constants/models';
import { ThemeToggle } from '../ui/ThemeToggle';
import { SettingsTab, UserApiKey } from '../../types/chat';
import { toast } from 'sonner';

export interface CustomShortcut {
  id: string;
  action: string;
  keys: string;
}

const DEFAULT_SHORTCUTS: CustomShortcut[] = [
  { id: 'sc-1', action: 'Open Global Search Modal', keys: 'Ctrl / Cmd + K' },
  { id: 'sc-2', action: 'Create New Conversation', keys: 'Ctrl / Cmd + Shift + O' },
  { id: 'sc-3', action: 'Toggle Collapsible Sidebar', keys: 'Ctrl / Cmd + /' },
  { id: 'sc-4', action: 'Send Prompt Message', keys: 'Enter' },
  { id: 'sc-5', action: 'Insert New Line in Composer', keys: 'Shift + Enter' },
  { id: 'sc-6', action: 'Close Modals & Search Bar', keys: 'Escape' },
];

export const SettingsModal: React.FC = () => {
  const {
    settingsModalOpen,
    setSettingsModalOpen,
    activeSettingsTab,
    setActiveSettingsTab,
    activePersonaId,
    setActivePersonaId,
    userProfile,
    updateUserProfile,
    conversations,
  } = useChatStore();

  const {
    showLineNumbers,
    setShowLineNumbers,
    enableWordWrap,
    setEnableWordWrap,
    streamingSpeedMs,
    setStreamingSpeedMs,
    autoScrollEnabled,
    setAutoScrollEnabled,
  } = useSettingsStore();

  // Local form state for profile & settings
  const [formData, setFormData] = useState({
    name: userProfile.name,
    username: userProfile.username,
    email: userProfile.email,
    role: userProfile.role,
    bio: userProfile.bio,
    avatarInitials: userProfile.avatarInitials,
    userContext: userProfile.customInstructions.userContext,
    responseStyle: userProfile.customInstructions.responseStyle,
  });

  useEffect(() => {
    setFormData({
      name: userProfile.name,
      username: userProfile.username,
      email: userProfile.email,
      role: userProfile.role,
      bio: userProfile.bio,
      avatarInitials: userProfile.avatarInitials,
      userContext: userProfile.customInstructions.userContext,
      responseStyle: userProfile.customInstructions.responseStyle,
    });
  }, [userProfile, settingsModalOpen]);

  // Edit profile popup state
  const [editProfileModalOpen, setEditProfileModalOpen] = useState(false);

  // API Key modal states for center popups
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<{ name: string; key: string } | null>(null);
  const [keyToRevoke, setKeyToRevoke] = useState<{ id: string; name: string } | null>(null);
  const [resetCacheModalOpen, setResetCacheModalOpen] = useState(false);

  // Hidden by default for all keys
  const [visibleKeys, setVisibleKeys] = useState<Record<string, boolean>>({});
  const [copiedKeyId, setCopiedKeyId] = useState<string | null>(null);

  // Keyboard Shortcuts State
  const [shortcuts, setShortcuts] = useState<CustomShortcut[]>(() => {
    const saved = localStorage.getItem('prox_custom_shortcuts');
    return saved ? JSON.parse(saved) : DEFAULT_SHORTCUTS;
  });

  useEffect(() => {
    localStorage.setItem('prox_custom_shortcuts', JSON.stringify(shortcuts));
  }, [shortcuts]);

  const [addShortcutModalOpen, setAddShortcutModalOpen] = useState(false);
  const [newShortcutAction, setNewShortcutAction] = useState('');
  const [newShortcutKeys, setNewShortcutKeys] = useState('');

  const [editingShortcut, setEditingShortcut] = useState<CustomShortcut | null>(null);
  const [shortcutToConfirmDelete, setShortcutToConfirmDelete] = useState<CustomShortcut | null>(null);

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    updateUserProfile({
      name: formData.name,
      username: formData.username,
      email: formData.email,
      role: formData.role,
      bio: formData.bio,
      avatarInitials: formData.avatarInitials || formData.name.slice(0, 2).toUpperCase(),
    });
    setEditProfileModalOpen(false);
    toast.success('Profile updated successfully!');
  };

  const handleSaveInstructions = (e: React.FormEvent) => {
    e.preventDefault();
    updateUserProfile({
      customInstructions: {
        userContext: formData.userContext,
        responseStyle: formData.responseStyle,
      },
    });
    toast.success('Custom AI instructions saved!');
  };

  const handleCreateApiKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;

    const randomBytes = Array.from({ length: 24 }, () =>
      Math.floor(Math.random() * 16).toString(16)
    ).join('');
    const generatedKey = `prox_sk_live_${randomBytes}`;

    const newApiKey: UserApiKey = {
      id: `key-${Date.now()}`,
      name: newKeyName.trim(),
      key: generatedKey,
      createdAt: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      lastUsed: 'Never',
    };

    const updatedKeys = [newApiKey, ...(userProfile.userApiKeys || [])];
    updateUserProfile({ userApiKeys: updatedKeys });

    setNewlyCreatedKey({ name: newApiKey.name, key: generatedKey });
    setNewKeyName('');
    setCreateModalOpen(false);
    toast.success(`API Key "${newApiKey.name}" generated!`);
  };

  const confirmRevokeKey = () => {
    if (!keyToRevoke) return;
    const updatedKeys = (userProfile.userApiKeys || []).filter((k) => k.id !== keyToRevoke.id);
    updateUserProfile({ userApiKeys: updatedKeys });
    toast.success(`API Key "${keyToRevoke.name}" revoked.`);
    setKeyToRevoke(null);
  };

  const handleCopyKey = (id: string, keyValue: string) => {
    navigator.clipboard.writeText(keyValue);
    setCopiedKeyId(id);
    toast.success('API Key copied to clipboard!');
    setTimeout(() => setCopiedKeyId(null), 2500);
  };

  const handleExportData = () => {
    const exportData = {
      userProfile,
      conversationsCount: conversations.length,
      conversations,
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `prox-ai-profile-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Profile and chat data exported as JSON!');
  };

  // Shortcut CRUD handlers
  const handleAddShortcut = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newShortcutAction.trim() || !newShortcutKeys.trim()) return;

    const newSc: CustomShortcut = {
      id: `sc-${Date.now()}`,
      action: newShortcutAction.trim(),
      keys: newShortcutKeys.trim(),
    };

    setShortcuts([...shortcuts, newSc]);
    setNewShortcutAction('');
    setNewShortcutKeys('');
    setAddShortcutModalOpen(false);
    toast.success(`Shortcut "${newSc.action}" added!`);
  };

  const handleUpdateShortcut = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingShortcut || !editingShortcut.action.trim() || !editingShortcut.keys.trim()) return;

    setShortcuts(shortcuts.map((s) => (s.id === editingShortcut.id ? editingShortcut : s)));
    setEditingShortcut(null);
    toast.success('Shortcut updated!');
  };

  const handleDeleteShortcut = () => {
    if (!shortcutToConfirmDelete) return;
    setShortcuts(shortcuts.filter((s) => s.id !== shortcutToConfirmDelete.id));
    toast.success(`Shortcut "${shortcutToConfirmDelete.action}" removed.`);
    setShortcutToConfirmDelete(null);
  };

  const handleResetShortcuts = () => {
    setShortcuts(DEFAULT_SHORTCUTS);
    toast.success('Shortcuts reset to system defaults!');
  };

  const navItems: { id: SettingsTab; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'profile', label: 'Profile & Overview', icon: User },
    { id: 'instructions', label: 'AI Memory & Context', icon: Brain },
    { id: 'apikeys', label: 'API Keys', icon: Key },
    { id: 'subscription', label: 'Subscription', icon: CreditCard },
    { id: 'privacy', label: 'Data & Privacy', icon: Shield },
    { id: 'general', label: 'General & Personas', icon: Sliders },
    { id: 'appearance', label: 'Appearance', icon: Moon },
    { id: 'ai', label: 'AI Engine', icon: Zap },
    { id: 'shortcuts', label: 'Shortcuts', icon: Keyboard },
  ];

  return (
    <>
      <Modal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <Settings className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Profile & Application Settings</span>
          </div>
        }
        maxWidth="2xl"
      >
        <div className="flex flex-col sm:flex-row gap-5 h-[480px] max-h-[75vh] overflow-hidden">
          {/* Left Vertical Navigation Sidebar */}
          <div className="sm:w-52 flex sm:flex-col gap-1 border-b sm:border-b-0 sm:border-r border-zinc-200 pb-2 sm:pb-0 sm:pr-3 shrink-0 dark:border-zinc-800 h-full overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isSelected = activeSettingsTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveSettingsTab(item.id)}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all shrink-0 text-left ${
                    isSelected
                      ? 'bg-blue-600 text-white shadow-sm dark:bg-blue-600 dark:text-white font-semibold'
                      : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-800'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5 shrink-0" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Main Panel Content Body */}
          <div className="flex-1 h-full overflow-y-auto text-xs pr-2 space-y-4">
            {/* 1. OVERVIEW & STATS */}
            {activeSettingsTab === 'profile' && (
              <div className="space-y-5">
                {/* Profile Card Header with Embedded Bio & Edit Profile Button */}
                <div className="p-4 rounded-2xl bg-white border border-zinc-200 dark:bg-zinc-900/80 dark:border-zinc-800 shadow-xs relative overflow-hidden space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3.5 min-w-0 flex-1">
                      {/* Avatar with Status Dot */}
                      <div className="relative shrink-0">
                        <div className="w-13 h-13 rounded-2xl bg-zinc-950 text-white dark:bg-white dark:text-zinc-950 font-black text-base flex items-center justify-center shadow-sm border border-zinc-200 dark:border-zinc-800">
                          {userProfile.avatarInitials || 'KR'}
                        </div>
                        <span className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-white dark:border-zinc-900" title="Active Pro Member" />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-100 tracking-tight">{userProfile.name}</h3>
                          <span className="px-2.5 py-0.5 rounded-md bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400 text-[11px] font-medium border border-blue-200 dark:border-blue-800/60 flex items-center gap-1">
                            <Sparkles className="w-3 h-3 text-blue-600 dark:text-blue-400" />
                            <span>{userProfile.plan}</span>
                          </span>
                        </div>
                        <p className="text-[13px] text-zinc-500 dark:text-zinc-400 font-medium mt-0.5">
                          @{userProfile.username}
                        </p>
                        <p className="text-[11px] text-zinc-700 dark:text-zinc-300 font-medium mt-0.5">
                          {userProfile.role}
                        </p>
                      </div>
                    </div>

                    {/* Edit Profile Button - Horizontally aligned beside profile pic & header */}
                    <button
                      onClick={() => setEditProfileModalOpen(true)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-100 hover:bg-zinc-200 text-zinc-800 dark:bg-zinc-800 dark:hover:bg-zinc-700 dark:text-zinc-100 font-semibold text-xs transition-all shrink-0 border border-zinc-200/80 dark:border-zinc-700/80 shadow-2xs"
                    >
                      <Pencil className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                      <span>Edit Profile</span>
                    </button>
                  </div>

                  {/* Bio display inside top header box */}
                  {userProfile.bio && (
                    <div className="pt-2.5 border-t border-zinc-100 dark:border-zinc-800/80 text-[11px] text-zinc-600 dark:text-zinc-300 flex items-start gap-1.5">
                      <Quote className="w-3.5 h-3.5 text-zinc-400 shrink-0 mt-0.5" />
                      <span className="italic font-medium">{userProfile.bio}</span>
                    </div>
                  )}
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800">
                    <div className="flex items-center gap-1.5 text-zinc-500 mb-1">
                      <MessageSquare className="w-3.5 h-3.5 text-blue-500" />
                      <span className="font-medium text-[11px]">Chats Created</span>
                    </div>
                    <div className="text-base font-extrabold text-zinc-900 dark:text-zinc-100">
                      {conversations.length}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800">
                    <div className="flex items-center gap-1.5 text-zinc-500 mb-1">
                      <MessageCircle className="w-3.5 h-3.5 text-emerald-500" />
                      <span className="font-medium text-[11px]">Messages Sent</span>
                    </div>
                    <div className="text-base font-extrabold text-zinc-900 dark:text-zinc-100">
                      {userProfile.stats.messagesCount}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800">
                    <div className="flex items-center gap-1.5 text-zinc-500 mb-1">
                      <Zap className="w-3.5 h-3.5 text-amber-500" />
                      <span className="font-medium text-[11px]">Tokens Used</span>
                    </div>
                    <div className="text-base font-extrabold text-zinc-900 dark:text-zinc-100">
                      {userProfile.stats.tokensUsed}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800">
                    <div className="flex items-center gap-1.5 text-zinc-500 mb-1">
                      <Clock className="w-3.5 h-3.5 text-purple-500" />
                      <span className="font-medium text-[11px]">Hours Saved</span>
                    </div>
                    <div className="text-base font-extrabold text-zinc-900 dark:text-zinc-100">
                      {userProfile.stats.savedHours}h
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 2. AI MEMORY & CONTEXT */}
            {activeSettingsTab === 'instructions' && (
              <form onSubmit={handleSaveInstructions} className="space-y-4">
                <div>
                  <h4 className="font-semibold text-zinc-900 dark:text-zinc-100 text-sm mb-1">
                    AI Memory & Custom Instructions
                  </h4>
                  <p className="text-zinc-500 dark:text-zinc-400 text-xs">
                    ProX AI models will automatically adapt to these background preferences across all chats.
                  </p>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
                      What would you like ProX AI to know about you to provide better responses?
                    </label>
                    <textarea
                      rows={3}
                      placeholder="e.g. I am a software engineer building web applications with React 19, TypeScript, and Vite..."
                      value={formData.userContext}
                      onChange={(e) => setFormData({ ...formData, userContext: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 dark:focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
                      How would you like ProX AI to structure its responses?
                    </label>
                    <textarea
                      rows={3}
                      placeholder="e.g. Provide production-grade code, maintain high aesthetics, avoid unnecessary fluff..."
                      value={formData.responseStyle}
                      onChange={(e) => setFormData({ ...formData, responseStyle: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 dark:focus:border-blue-500"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-1">
                  <button
                    type="submit"
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-all shadow-sm"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>Save AI Memory</span>
                  </button>
                </div>
              </form>
            )}

            {/* 3. API KEYS */}
            {activeSettingsTab === 'apikeys' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between gap-2 border-b border-zinc-200 dark:border-zinc-800 pb-3">
                  <div>
                    <h4 className="font-semibold text-zinc-900 dark:text-zinc-100 text-sm">
                      API Tokens & Secret Keys
                    </h4>
                    <p className="text-zinc-500 dark:text-zinc-400 text-xs">
                      Create secret API keys to authenticate requests with ProX AI. Keys are hidden by default.
                    </p>
                  </div>

                  <button
                    onClick={() => setCreateModalOpen(true)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-sm transition-all shrink-0"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Create API Key</span>
                  </button>
                </div>

                {/* API Keys List */}
                <div className="space-y-2.5">
                  {(!userProfile.userApiKeys || userProfile.userApiKeys.length === 0) ? (
                    <div className="p-6 text-center text-zinc-500 dark:text-zinc-400 rounded-xl bg-zinc-50 border border-zinc-200 border-dashed dark:bg-zinc-900/40 dark:border-zinc-800">
                      <Key className="w-8 h-8 mx-auto text-zinc-400 mb-2" />
                      <p className="font-semibold text-zinc-700 dark:text-zinc-300">No API keys created yet</p>
                      <p className="text-[11px] mt-0.5">Click "Create API Key" above to generate your first secret token.</p>
                    </div>
                  ) : (
                    userProfile.userApiKeys.map((k) => {
                      const isVisible = !!visibleKeys[k.id];
                      const isCopied = copiedKeyId === k.id;
                      const maskedValue = k.key.slice(0, 14) + '••••••••••••••••••••';

                      return (
                        <div key={k.id} className="p-3.5 rounded-xl bg-white border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800 space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="font-semibold text-zinc-900 dark:text-zinc-100 text-xs flex items-center gap-2">
                              <span>{k.name}</span>
                              <span className="px-1.5 py-0.5 rounded text-[10px] bg-zinc-100 border border-zinc-200 text-zinc-600 font-mono dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-400">
                                Created: {k.createdAt}
                              </span>
                            </div>

                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleCopyKey(k.id, k.key)}
                                className="p-1.5 rounded-lg text-zinc-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors flex items-center gap-1 font-medium text-[11px]"
                                title="Copy API key"
                              >
                                {isCopied ? <Check className="w-3.5 h-3.5 text-blue-600" /> : <Copy className="w-3.5 h-3.5" />}
                                <span>{isCopied ? 'Copied' : 'Copy'}</span>
                              </button>

                              <button
                                onClick={() => setVisibleKeys({ ...visibleKeys, [k.id]: !isVisible })}
                                className="p-1.5 rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 dark:hover:text-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                                title={isVisible ? 'Hide API Key' : 'Unhide API Key'}
                              >
                                {isVisible ? <EyeOff className="w-3.5 h-3.5 text-blue-600" /> : <Eye className="w-3.5 h-3.5" />}
                              </button>

                              <button
                                onClick={() => setKeyToRevoke({ id: k.id, name: k.name })}
                                className="p-1.5 rounded-lg text-zinc-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                                title="Revoke API Key"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="px-3 py-1.5 rounded-lg bg-zinc-50 border border-zinc-200 font-mono text-[11px] text-zinc-800 dark:bg-zinc-900 dark:border-zinc-800 dark:text-zinc-200 truncate">
                            {isVisible ? k.key : maskedValue}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}

            {/* 4. SUBSCRIPTION */}
            {activeSettingsTab === 'subscription' && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-bold text-zinc-900 dark:text-zinc-100 text-sm">
                      Active Subscription: {userProfile.plan}
                    </div>
                    <p className="text-zinc-600 dark:text-zinc-400 text-xs mt-0.5">
                      Your Pro subscription renews on <span className="font-semibold text-blue-600 dark:text-blue-400">September 5, 2026</span> ($20/month).
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold text-zinc-900 dark:text-zinc-100">Included Pro Features:</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {[
                      'Unlimited Neurix, Logix & Optix Model Access',
                      'Logix Advanced Chain-of-Thought Reasoning',
                      'Interactive Canvas Code Artifact Execution',
                      'High-speed Web Search Integration',
                      'Priority API Throughput & Zero Queue',
                      'Voice Synthesizer & Multimodal Vision',
                    ].map((feat, idx) => (
                      <div key={idx} className="flex items-center gap-2 p-2.5 rounded-xl bg-zinc-50 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800">
                        <Check className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 shrink-0" />
                        <span className="text-zinc-800 dark:text-zinc-200 font-medium">{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* 5. DATA & PRIVACY */}
            {activeSettingsTab === 'privacy' && (
              <div className="space-y-4">
                <div className="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 dark:bg-zinc-900/60 dark:border-zinc-800 flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-zinc-900 dark:text-zinc-100">Export Workspace JSON</div>
                    <div className="text-[11px] text-zinc-500 dark:text-zinc-400">Download all conversations, profile data & saved prompts</div>
                  </div>
                  <button
                    onClick={handleExportData}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-600 text-white hover:bg-blue-700 font-semibold shadow-sm transition-all"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export JSON</span>
                  </button>
                </div>

                <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-red-600 dark:text-red-400">Clear Cache & Local Storage</div>
                    <div className="text-[11px] text-zinc-500 dark:text-zinc-400">Reset local browser state and application memory</div>
                  </div>
                  <button
                    onClick={() => setResetCacheModalOpen(true)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-600 text-white hover:bg-red-700 font-medium"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Reset Cache</span>
                  </button>
                </div>
              </div>
            )}

            {/* 6. GENERAL & PERSONAS */}
            {activeSettingsTab === 'general' && (
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-zinc-900 mb-2 dark:text-zinc-100">Default System Persona</h4>
                  <div className="space-y-2">
                    {SYSTEM_PERSONAS.map((p) => {
                      const isSelected = activePersonaId === p.id;
                      return (
                        <button
                          key={p.id}
                          onClick={() => setActivePersonaId(p.id)}
                          className={`w-full flex items-start justify-between p-2.5 rounded-xl border text-left transition-all ${
                            isSelected
                              ? 'bg-blue-50 border-blue-600 text-blue-950 font-medium dark:bg-blue-950/40 dark:border-blue-500 dark:text-blue-100'
                              : 'bg-white border-zinc-200 text-zinc-600 hover:text-zinc-900 hover:bg-zinc-50 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-400'
                          }`}
                        >
                          <div>
                            <div className="font-semibold text-zinc-900 dark:text-zinc-100">{p.name}</div>
                            <div className="text-[11px] text-zinc-500 mt-0.5 dark:text-zinc-400">{p.description}</div>
                          </div>
                          {isSelected && <Check className="w-4 h-4 text-blue-600 shrink-0 mt-0.5 dark:text-blue-400" />}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-xl bg-white border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800">
                  <div>
                    <div className="font-semibold text-zinc-900 dark:text-zinc-100">Auto Scroll on Response</div>
                    <div className="text-[11px] text-zinc-500 dark:text-zinc-400">Keep viewport scrolled to latest streaming token</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={autoScrollEnabled}
                    onChange={(e) => setAutoScrollEnabled(e.target.checked)}
                    className="accent-blue-600 w-4 h-4 rounded dark:accent-blue-500"
                  />
                </div>
              </div>
            )}

            {/* 7. APPEARANCE */}
            {activeSettingsTab === 'appearance' && (
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-zinc-900 mb-2 dark:text-zinc-100">Theme Mode</h4>
                  <ThemeToggle />
                </div>

                <div className="space-y-2 pt-2 border-t border-zinc-200 dark:border-zinc-800">
                  <h4 className="font-semibold text-zinc-900 dark:text-zinc-100">Code Block Viewer</h4>

                  <div className="flex items-center justify-between p-3 rounded-xl bg-white border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800">
                    <span className="font-medium text-zinc-800 dark:text-zinc-200">Show Line Numbers in Code Snippets</span>
                    <input
                      type="checkbox"
                      checked={showLineNumbers}
                      onChange={(e) => setShowLineNumbers(e.target.checked)}
                      className="accent-blue-600 w-4 h-4 rounded dark:accent-blue-500"
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-xl bg-white border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800">
                    <span className="font-medium text-zinc-800 dark:text-zinc-200">Enable Word Wrap by Default</span>
                    <input
                      type="checkbox"
                      checked={enableWordWrap}
                      onChange={(e) => setEnableWordWrap(e.target.checked)}
                      className="accent-blue-600 w-4 h-4 rounded dark:accent-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* 8. AI ENGINE */}
            {activeSettingsTab === 'ai' && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-semibold text-zinc-900 dark:text-zinc-100">Token Streaming Speed ({streamingSpeedMs}ms)</h4>
                  <input
                    type="range"
                    min={5}
                    max={80}
                    value={streamingSpeedMs}
                    onChange={(e) => setStreamingSpeedMs(Number(e.target.value))}
                    className="w-full accent-blue-600 dark:accent-blue-500"
                  />
                  <div className="flex justify-between text-[11px] text-zinc-500">
                    <span>Fast (5ms)</span>
                    <span>Balanced (25ms)</span>
                    <span>Relaxed (80ms)</span>
                  </div>
                </div>
              </div>
            )}

            {/* 9. SHORTCUTS (DYNAMIC EDIT, ADD, REMOVE) */}
            {activeSettingsTab === 'shortcuts' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between gap-2 border-b border-zinc-200 dark:border-zinc-800 pb-3">
                  <div>
                    <h4 className="font-semibold text-zinc-900 dark:text-zinc-100 text-sm">
                      Keyboard Shortcuts
                    </h4>
                    <p className="text-zinc-500 dark:text-zinc-400 text-xs">
                      Customize hotkeys for rapid application navigation and actions.
                    </p>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <button
                      onClick={handleResetShortcuts}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 text-xs font-medium transition-all"
                      title="Reset shortcuts to system defaults"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Reset</span>
                    </button>
                    <button
                      onClick={() => setAddShortcutModalOpen(true)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-sm transition-all"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Add Shortcut</span>
                    </button>
                  </div>
                </div>

                <div className="space-y-2 font-mono text-[11px]">
                  {shortcuts.map((s) => (
                    <div
                      key={s.id}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800 group"
                    >
                      <span className="text-zinc-800 font-medium font-sans text-xs dark:text-zinc-200">
                        {s.action}
                      </span>

                      <div className="flex items-center gap-2">
                        <kbd className="px-2.5 py-1 rounded-lg bg-zinc-100 border border-zinc-200 text-zinc-900 font-bold text-xs dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100">
                          {s.keys}
                        </kbd>

                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => setEditingShortcut(s)}
                            className="p-1 rounded-lg text-zinc-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors"
                            title="Edit shortcut"
                          >
                            <Pencil className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => setShortcutToConfirmDelete(s)}
                            className="p-1 rounded-lg text-zinc-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                            title="Remove shortcut"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </Modal>

      {/* CENTER POPUP 1: EDIT PROFILE MODAL */}
      <Modal
        isOpen={editProfileModalOpen}
        onClose={() => setEditProfileModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <Pencil className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Edit Personal Profile</span>
          </div>
        }
        maxWidth="md"
      >
        <form onSubmit={handleSaveProfile} className="space-y-3.5 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-zinc-700 dark:text-zinc-300 font-medium mb-1">Display Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 dark:focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-zinc-700 dark:text-zinc-300 font-medium mb-1">Username Handle</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 dark:focus:border-blue-500"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-zinc-700 dark:text-zinc-300 font-medium mb-1">Email Address</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 dark:focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-zinc-700 dark:text-zinc-300 font-medium mb-1">Role / Headline</label>
              <input
                type="text"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 dark:focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-zinc-700 dark:text-zinc-300 font-medium mb-1">Bio</label>
            <textarea
              rows={2}
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600 dark:focus:border-blue-500"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setEditProfileModalOpen(false)}
              className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      </Modal>

      {/* CENTER POPUP 2: CREATE API KEY MODAL */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title={
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Create new API Key</span>
          </div>
        }
        maxWidth="sm"
      >
        <form onSubmit={handleCreateApiKey} className="space-y-4 text-xs">
          <p className="text-zinc-500 dark:text-zinc-400">
            Enter a descriptive name for your API key to help identify where it is being used.
          </p>

          <div>
            <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
              Key Name
            </label>
            <input
              type="text"
              placeholder="e.g. First API, Cursor Agent, CLI Integration..."
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
              autoFocus
              required
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
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
              <Check className="w-3.5 h-3.5" />
              <span>Create secret key</span>
            </button>
          </div>
        </form>
      </Modal>

      {/* CENTER POPUP 3: NEWLY CREATED KEY DISPLAY MODAL */}
      {newlyCreatedKey && (
        <Modal
          isOpen={!!newlyCreatedKey}
          onClose={() => setNewlyCreatedKey(null)}
          title={
            <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>API Key Generated</span>
            </div>
          }
          maxWidth="md"
        >
          <form onSubmit={(e) => { e.preventDefault(); setNewlyCreatedKey(null); }} className="space-y-4 text-xs">
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-2.5 text-amber-800 dark:text-amber-300">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-amber-600 dark:text-amber-400" />
              <div>
                <span className="font-bold block">Save your secret key</span>
                <p className="text-[11px]">
                  Please store this key securely. You will not be able to view the full key again after closing this window.
                </p>
              </div>
            </div>

            <div>
              <div className="font-semibold text-zinc-800 dark:text-zinc-200 mb-1">
                {newlyCreatedKey.name}
              </div>
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-zinc-50 border border-zinc-200 font-mono text-xs text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100">
                <span className="flex-1 truncate">{newlyCreatedKey.key}</span>
                <button
                  type="button"
                  onClick={() => handleCopyKey('new-key', newlyCreatedKey.key)}
                  className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-sans font-semibold flex items-center gap-1"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </button>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                autoFocus
                className="px-5 py-2 rounded-xl bg-zinc-950 hover:bg-black text-white dark:bg-white dark:hover:bg-zinc-100 dark:text-zinc-950 font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                Done
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* CENTER POPUP 4: REVOKE KEY CONFIRMATION MODAL */}
      {keyToRevoke && (
        <Modal
          isOpen={!!keyToRevoke}
          onClose={() => setKeyToRevoke(null)}
          title={
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span>Revoke API Key</span>
            </div>
          }
          maxWidth="sm"
        >
          <form onSubmit={(e) => { e.preventDefault(); confirmRevokeKey(); }} className="space-y-4 text-xs">
            <p className="text-zinc-700 dark:text-zinc-300">
              Are you sure you want to revoke API Key <strong className="text-zinc-900 dark:text-zinc-100 font-semibold">"{keyToRevoke.name}"</strong>?
            </p>
            <p className="text-zinc-500 dark:text-zinc-400 text-[11px]">
              Any applications, SDKs, or scripts using this key will immediately lose access to ProX AI APIs. Press <kbd className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 font-mono font-bold">Enter ↵</kbd> to confirm.
            </p>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setKeyToRevoke(null)}
                className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                autoFocus
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold shadow-xs focus:ring-2 focus:ring-red-500 focus:outline-none"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Revoke Key</span>
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* CENTER POPUP 5: RESET CACHE CONFIRMATION MODAL */}
      {resetCacheModalOpen && (
        <Modal
          isOpen={resetCacheModalOpen}
          onClose={() => setResetCacheModalOpen(false)}
          title={
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span>Reset Local Cache & Memory</span>
            </div>
          }
          maxWidth="sm"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              localStorage.clear();
              window.location.reload();
            }}
            className="space-y-4 text-xs"
          >
            <p className="text-zinc-700 dark:text-zinc-300">
              Are you sure you want to clear your local browser storage and cache?
            </p>
            <p className="text-zinc-500 dark:text-zinc-400 text-[11px]">
              This action will reset locally cached chat sessions and settings on this device. Press <kbd className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 font-mono font-bold">Enter ↵</kbd> to confirm.
            </p>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setResetCacheModalOpen(false)}
                className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                autoFocus
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold shadow-xs focus:ring-2 focus:ring-red-500 focus:outline-none"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Reset Cache</span>
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* CENTER POPUP 6: ADD SHORTCUT MODAL */}
      {addShortcutModalOpen && (
        <Modal
          isOpen={addShortcutModalOpen}
          onClose={() => setAddShortcutModalOpen(false)}
          title={
            <div className="flex items-center gap-2">
              <Keyboard className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Add Custom Keyboard Shortcut</span>
            </div>
          }
          maxWidth="sm"
        >
          <form onSubmit={handleAddShortcut} className="space-y-4 text-xs">
            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
                Action Description
              </label>
              <input
                type="text"
                placeholder="e.g. Export Code Snippet, Open Persona Menu..."
                value={newShortcutAction}
                onChange={(e) => setNewShortcutAction(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
                autoFocus
                required
              />
            </div>

            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
                Key Combination
              </label>
              <input
                type="text"
                placeholder="e.g. Ctrl / Cmd + Shift + E"
                value={newShortcutKeys}
                onChange={(e) => setNewShortcutKeys(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 font-mono dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setAddShortcutModalOpen(false)}
                className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Shortcut</span>
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* CENTER POPUP 7: EDIT SHORTCUT MODAL */}
      {editingShortcut && (
        <Modal
          isOpen={!!editingShortcut}
          onClose={() => setEditingShortcut(null)}
          title={
            <div className="flex items-center gap-2">
              <Pencil className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Edit Keyboard Shortcut</span>
            </div>
          }
          maxWidth="sm"
        >
          <form onSubmit={handleUpdateShortcut} className="space-y-4 text-xs">
            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
                Action Description
              </label>
              <input
                type="text"
                value={editingShortcut.action}
                onChange={(e) => setEditingShortcut({ ...editingShortcut, action: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <div>
              <label className="block text-zinc-800 dark:text-zinc-200 font-semibold mb-1">
                Key Combination
              </label>
              <input
                type="text"
                value={editingShortcut.keys}
                onChange={(e) => setEditingShortcut({ ...editingShortcut, keys: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-white border border-zinc-200 text-zinc-900 font-mono dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 focus:outline-none focus:border-blue-600"
                required
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setEditingShortcut(null)}
                className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs"
              >
                <Save className="w-3.5 h-3.5" />
                <span>Save Changes</span>
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* CENTER POPUP 8: DELETE SHORTCUT CONFIRMATION MODAL */}
      {shortcutToConfirmDelete && (
        <Modal
          isOpen={!!shortcutToConfirmDelete}
          onClose={() => setShortcutToConfirmDelete(null)}
          title={
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span>Remove Shortcut</span>
            </div>
          }
          maxWidth="sm"
        >
          <form onSubmit={(e) => { e.preventDefault(); handleDeleteShortcut(); }} className="space-y-4 text-xs">
            <p className="text-zinc-700 dark:text-zinc-300">
              Are you sure you want to remove the shortcut for <strong className="text-zinc-900 dark:text-zinc-100 font-semibold">"{shortcutToConfirmDelete.action}"</strong> ({shortcutToConfirmDelete.keys})?
            </p>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShortcutToConfirmDelete(null)}
                className="px-3.5 py-2 rounded-xl text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                autoFocus
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold shadow-xs focus:ring-2 focus:ring-red-500 focus:outline-none"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Remove Shortcut</span>
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
};
