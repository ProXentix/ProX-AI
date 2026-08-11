import React, { useState } from 'react';
import {
  Folder,
  Search,
  Plus,
  ArrowLeft,
  Share2,
  MoreHorizontal,
  Mic,
  Lightbulb,
  Trash2,
  MessageSquare,
  Sparkles,
  ChevronDown,
  AudioLines,
} from 'lucide-react';
import { ProjectItem } from '../../types/chat';
import { useChatStore } from '../../store/chatStore';
import { Modal } from '../ui/Modal';
import { toast } from 'sonner';

interface ProjectsPageProps {
  onClose: () => void;
  onStartChatInProject: (projectId: string, initialPrompt?: string) => void;
}

export const ProjectsPage: React.FC<ProjectsPageProps> = ({ onClose, onStartChatInProject }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<'all' | 'created' | 'shared'>('all');
  const [selectedProject, setSelectedProject] = useState<ProjectItem | null>(null);
  const [activeDetailTab, setActiveDetailTab] = useState<'chats' | 'sources'>('chats');
  const [newChatInput, setNewChatInput] = useState('');

  // Create Project Modal State
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [memoryOption, setMemoryOption] = useState('Default memory');

  const { projects, addProject, deleteProject, conversations } = useChatStore();

  const filteredProjects = projects.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    if (activeFilter === 'created') return matchesSearch && !p.shared;
    if (activeFilter === 'shared') return matchesSearch && p.shared;
    return matchesSearch;
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName.trim()) return;

    addProject(projectName.trim(), memoryOption);
    toast.success(`Project "${projectName.trim()}" created!`);
    setProjectName('');
    setCreateModalOpen(false);
  };

  const projectConversations = selectedProject
    ? conversations.filter((c) => c.folderId === selectedProject.id)
    : [];

  return (
    <div className="flex-1 overflow-y-auto bg-white dark:bg-zinc-950 h-full select-none text-zinc-900 dark:text-zinc-100">
      {selectedProject ? (
        /* PROJECT DETAIL VIEW (SCREENSHOT 4) */
        <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
          {/* Top Bar: Back & Header */}
          <div className="flex items-center justify-between gap-4">
            <button
              onClick={() => setSelectedProject(null)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-zinc-900 bg-zinc-100 hover:bg-zinc-200/80 border border-zinc-200/80 transition-all dark:text-zinc-300 dark:hover:text-zinc-100 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:border-zinc-800 shrink-0 shadow-2xs"
              title="Back to Projects"
            >
              <ArrowLeft className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Back</span>
            </button>

            {/* Right Action Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                  toast.success('Project link copied!');
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-100 hover:bg-zinc-200/80 text-zinc-800 text-xs font-medium border border-zinc-200/80 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-800 transition-all"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Share</span>
              </button>
              <button
                onClick={() => {
                  deleteProject(selectedProject.id);
                  setSelectedProject(null);
                  toast.success('Project deleted');
                }}
                className="p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-900 text-zinc-500 hover:text-red-600 transition-colors"
                title="Delete Project"
              >
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Project Title Header */}
          <div className="flex items-center gap-3 pt-2">
            <div className="w-10 h-10 rounded-2xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 flex items-center justify-center text-zinc-900 dark:text-zinc-100 shadow-2xs">
              <Folder className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight">{selectedProject.name}</h1>
          </div>

          {/* Prompt / New Chat Input Box */}
          <div className="relative">
            <div className="flex items-center gap-3 p-3.5 rounded-3xl bg-white border border-zinc-200/90 shadow-sm dark:bg-zinc-900 dark:border-zinc-800">
              <Plus className="w-4 h-4 text-zinc-400 ml-1 shrink-0" />
              <input
                type="text"
                placeholder={`New chat in ${selectedProject.name}`}
                value={newChatInput}
                onChange={(e) => setNewChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && newChatInput.trim()) {
                    onStartChatInProject(selectedProject.id, newChatInput.trim());
                    setNewChatInput('');
                  }
                }}
                className="w-full bg-transparent text-sm text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none"
              />
              <div className="flex items-center gap-1.5 shrink-0">
                <button
                  type="button"
                  className="p-1.5 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                >
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (newChatInput.trim()) {
                      onStartChatInProject(selectedProject.id, newChatInput.trim());
                      setNewChatInput('');
                    } else {
                      onStartChatInProject(selectedProject.id);
                    }
                  }}
                  className="w-7 h-7 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center transition-all shadow-2xs"
                >
                  <AudioLines className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Detail Tabs: Chats | Sources */}
          <div className="flex items-center gap-2 pt-2 border-b border-zinc-200/60 dark:border-zinc-800/60 pb-3">
            <button
              onClick={() => setActiveDetailTab('chats')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeDetailTab === 'chats'
                  ? 'bg-zinc-100 text-zinc-950 dark:bg-zinc-800 dark:text-zinc-100'
                  : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200'
              }`}
            >
              Chats
            </button>
            <button
              onClick={() => setActiveDetailTab('sources')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeDetailTab === 'sources'
                  ? 'bg-zinc-100 text-zinc-950 dark:bg-zinc-800 dark:text-zinc-100'
                  : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200'
              }`}
            >
              Sources
            </button>
          </div>

          {/* Content area: Chats list or Empty state */}
          {activeDetailTab === 'chats' ? (
            projectConversations.length === 0 ? (
              <div className="py-20 text-center space-y-2">
                <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">No chats yet</h3>
                <p className="text-xs text-zinc-400">Chats in {selectedProject.name} will live here</p>
              </div>
            ) : (
              <div className="space-y-2">
                {projectConversations.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => onStartChatInProject(selectedProject.id)}
                    className="p-3.5 rounded-2xl bg-zinc-50 hover:bg-zinc-100/80 border border-zinc-200/80 dark:bg-zinc-900/60 dark:hover:bg-zinc-800/80 dark:border-zinc-800 cursor-pointer transition-all flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <MessageSquare className="w-4 h-4 text-blue-500" />
                      <span className="text-xs font-bold text-zinc-900 dark:text-zinc-100">
                        {conv.title}
                      </span>
                    </div>
                    <span className="text-[10px] text-zinc-400 font-mono">
                      {conv.messages.length} messages
                    </span>
                  </div>
                ))}
              </div>
            )
          ) : (
            <div className="py-20 text-center space-y-2">
              <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">No sources added yet</h3>
              <p className="text-xs text-zinc-400">Project files, context documents, and instructions will appear here</p>
            </div>
          )}
        </div>
      ) : (
        /* PROJECTS LIST VIEW (SCREENSHOT 1 & 3) */
        <div>
          {/* Top Sticky Header */}
          <div className="sticky top-0 z-10 bg-white/90 dark:bg-zinc-950/90 backdrop-blur-md border-b border-zinc-100 dark:border-zinc-800 px-3 sm:px-6 py-3 sm:py-4">
            <div className="w-full flex items-center justify-between gap-2 sm:gap-4">
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={onClose}
                  className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-zinc-900 bg-zinc-100 hover:bg-zinc-200/80 border border-zinc-200/80 transition-all dark:text-zinc-300 dark:hover:text-zinc-100 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:border-zinc-800 shrink-0 shadow-2xs"
                  title="Back to Chat"
                >
                  <ArrowLeft className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span className="hidden sm:inline">Back</span>
                </button>
              </div>

              {/* Centered Title */}
              <div className="flex-1 flex justify-center items-center px-1 sm:px-4">
                <h1 className="text-lg sm:text-2xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-100 text-center truncate">
                  Projects
                </h1>
              </div>

              {/* Search Input & New Button */}
              <div className="flex items-center gap-2 sm:gap-3 shrink-0">
                <div className="relative w-28 sm:w-56">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 sm:w-4 sm:h-4 text-zinc-400" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-8 sm:pl-9 pr-2.5 sm:pr-3.5 py-1.5 sm:py-2 rounded-2xl text-xs bg-zinc-100/80 border border-zinc-200/60 text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 dark:bg-zinc-900/80 dark:border-zinc-800 dark:text-zinc-100 shadow-2xs transition-all"
                  />
                </div>

                <button
                  onClick={() => setCreateModalOpen(true)}
                  className="flex items-center gap-1 sm:gap-1.5 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-all shadow-md active:scale-95 shrink-0"
                >
                  <Plus className="w-4 h-4" />
                  <span className="hidden sm:inline">New Project</span>
                  <span className="inline sm:hidden">New</span>
                </button>
              </div>
            </div>
          </div>

        <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
            {/* Filter Pills */}
            <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveFilter('all')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeFilter === 'all'
                  ? 'bg-zinc-950 text-white dark:bg-white dark:text-zinc-950 shadow-2xs'
                  : 'text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setActiveFilter('created')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeFilter === 'created'
                  ? 'bg-zinc-950 text-white dark:bg-white dark:text-zinc-950 shadow-2xs'
                  : 'text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200'
              }`}
            >
              Created by you
            </button>
            <button
              onClick={() => setActiveFilter('shared')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                activeFilter === 'shared'
                  ? 'bg-zinc-950 text-white dark:bg-white dark:text-zinc-950 shadow-2xs'
                  : 'text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200'
              }`}
            >
              Shared with you
            </button>
          </div>

          {/* Projects Content: Empty State vs Table List */}
          {filteredProjects.length === 0 ? (
            /* EMPTY STATE (SCREENSHOT 1) */
            <div className="py-24 flex flex-col items-center justify-center text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 flex items-center justify-center text-zinc-900 dark:text-zinc-100 shadow-2xs">
                <Folder className="w-6 h-6 stroke-[1.5]" />
              </div>
              <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">No projects yet</h3>
            </div>
          ) : (
            /* TABLE LIST (SCREENSHOT 3) */
            <div className="space-y-2">
              <div className="grid grid-cols-12 px-3 py-2 text-xs font-medium text-zinc-400">
                <span className="col-span-8">Name</span>
                <span className="col-span-4 text-right">Modified</span>
              </div>

              <div className="space-y-1">
                {filteredProjects.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => setSelectedProject(project)}
                    className="grid grid-cols-12 items-center px-3 py-2.5 rounded-2xl hover:bg-zinc-100/80 dark:hover:bg-zinc-900/80 cursor-pointer transition-all group"
                  >
                    <div className="col-span-8 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-xl bg-zinc-100 dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 flex items-center justify-center text-zinc-800 dark:text-zinc-200">
                        <Folder className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                        {project.name}
                      </span>
                    </div>

                    <div className="col-span-4 flex items-center justify-end gap-3 text-xs text-zinc-500 dark:text-zinc-400">
                      <span>{project.updatedAt}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteProject(project.id);
                          toast.success(`Project "${project.name}" deleted.`);
                        }}
                        className="p-1 rounded-lg hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 opacity-0 group-hover:opacity-100 transition-all"
                        title="Delete project"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      )}

      {/* CREATE PROJECT MODAL (SCREENSHOT 2) */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title={<span className="text-sm font-extrabold">Create project</span>}
        maxWidth="sm"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1.5">
              Project name
            </label>
            <div className="relative">
              <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
              <input
                type="text"
                placeholder="Copenhagen Trip"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-white border border-zinc-300 text-zinc-900 dark:bg-zinc-950 dark:border-zinc-700 dark:text-zinc-100 focus:outline-none focus:border-zinc-900 dark:focus:border-zinc-400"
                required
                autoFocus
              />
            </div>
          </div>

          {/* Info Callout Box */}
          <div className="p-3.5 rounded-2xl bg-zinc-100/80 border border-zinc-200/60 dark:bg-zinc-900/60 dark:border-zinc-800 flex items-start gap-2.5 text-zinc-600 dark:text-zinc-400 leading-relaxed text-[11px]">
            <Lightbulb className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
            <span>
              Projects keep chats, files, and custom instructions in one place. Use them for ongoing work, or just to keep things tidy.
            </span>
          </div>

          {/* Bottom Controls */}
          <div className="flex items-center justify-between pt-2 border-t border-zinc-100 dark:border-zinc-800">
            {/* Memory Dropdown */}
            <div className="relative">
              <button
                type="button"
                className="flex items-center gap-1 text-zinc-700 dark:text-zinc-300 font-medium hover:text-zinc-900 dark:hover:text-zinc-100"
              >
                <span>{memoryOption}</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Action submit button */}
            <button
              type="submit"
              disabled={!projectName.trim()}
              className={`px-4 py-2 rounded-full font-semibold text-xs transition-all ${
                projectName.trim()
                  ? 'bg-zinc-950 text-white hover:bg-black dark:bg-white dark:text-zinc-950 dark:hover:bg-zinc-100 shadow-2xs cursor-pointer'
                  : 'bg-zinc-200 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-600 cursor-not-allowed'
              }`}
            >
              Create project
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
