import { create } from 'zustand';
import type { Project, CreateProjectRequest, UploadStatusResponse } from '../../../../shared/api-contract';
import { api } from '../api';

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  uploadStatus: UploadStatusResponse | null;
  isLoading: boolean;
  isCreating: boolean;
  isDeleting: boolean;
  isUploading: boolean;
  error: string | null;
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
  
  fetchProjects: (page?: number, limit?: number) => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: CreateProjectRequest) => Promise<Project | null>;
  deleteProject: (id: string) => Promise<boolean>;
  uploadFile: (projectId: string, file: File) => Promise<boolean>;
  checkUploadStatus: (projectId: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
  clearError: () => void;
  reset: () => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  currentProject: null,
  uploadStatus: null,
  isLoading: false,
  isCreating: false,
  isDeleting: false,
  isUploading: false,
  error: null,
  page: 1,
  limit: 10,
  total: 0,
  hasMore: false,

  fetchProjects: async (page = 1, limit = 10) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.projects.getProjects({ page, limit });
      if (response.success && response.data) {
        set({
          projects: response.data.items,
          page,
          limit,
          total: response.data.total,
          hasMore: response.data.hasMore,
          isLoading: false,
        });
      } else {
        set({ 
          error: response.error || 'Failed to fetch projects',
          isLoading: false 
        });
      }
    } catch (error) {
      set({ 
        error: 'Network error while fetching projects',
        isLoading: false 
      });
    }
  },

  fetchProject: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.projects.getProject(id);
      if (response.success && response.data) {
        set({
          currentProject: response.data,
          isLoading: false,
        });
        
        const existingProjects = get().projects;
        const index = existingProjects.findIndex(p => p.id === id);
        if (index !== -1) {
          existingProjects[index] = response.data;
          set({ projects: [...existingProjects] });
        }
      } else {
        set({ 
          error: response.error || 'Failed to fetch project',
          isLoading: false 
        });
      }
    } catch (error) {
      set({ 
        error: 'Network error while fetching project',
        isLoading: false 
      });
    }
  },

  createProject: async (data: CreateProjectRequest) => {
    set({ isCreating: true, error: null });
    try {
      const response = await api.projects.createProject(data);
      if (response.success && response.data) {
        const newProject = response.data.project;
        const projects = get().projects;
        set({
          projects: [newProject, ...projects],
          currentProject: newProject,
          isCreating: false,
        });
        return newProject;
      } else {
        set({ 
          error: response.error || 'Failed to create project',
          isCreating: false 
        });
        return null;
      }
    } catch (error) {
      set({ 
        error: 'Network error while creating project',
        isCreating: false 
      });
      return null;
    }
  },

  deleteProject: async (id: string) => {
    set({ isDeleting: true, error: null });
    try {
      const response = await api.projects.deleteProject(id);
      if (response.success) {
        const projects = get().projects.filter(p => p.id !== id);
        const currentProject = get().currentProject;
        set({
          projects,
          currentProject: currentProject?.id === id ? null : currentProject,
          isDeleting: false,
        });
        return true;
      } else {
        set({ 
          error: response.error || 'Failed to delete project',
          isDeleting: false 
        });
        return false;
      }
    } catch (error) {
      set({ 
        error: 'Network error while deleting project',
        isDeleting: false 
      });
      return false;
    }
  },

  uploadFile: async (projectId: string, file: File) => {
    set({ isUploading: true, error: null });
    try {
      const uploadUrlResponse = await api.projects.getUploadUrl(projectId);
      if (!uploadUrlResponse.success || !uploadUrlResponse.data) {
        set({ 
          error: uploadUrlResponse.error || 'Failed to get upload URL',
          isUploading: false 
        });
        return false;
      }

      const { upload_url, upload_fields } = uploadUrlResponse.data;
      
      const formData = new FormData();
      Object.entries(upload_fields).forEach(([key, value]) => {
        formData.append(key, value);
      });
      formData.append('file', file);

      const uploadResponse = await fetch(upload_url, {
        method: 'POST',
        body: formData,
      });

      if (uploadResponse.ok) {
        set({ isUploading: false });
        
        await get().checkUploadStatus(projectId);
        return true;
      } else {
        set({ 
          error: 'Failed to upload file',
          isUploading: false 
        });
        return false;
      }
    } catch (error) {
      set({ 
        error: 'Network error while uploading file',
        isUploading: false 
      });
      return false;
    }
  },

  checkUploadStatus: async (projectId: string) => {
    try {
      const response = await api.projects.getProjectStatus(projectId);
      if (response.success && response.data) {
        set({ uploadStatus: response.data });
        
        if (response.data.status === 'ready') {
          await get().fetchProject(projectId);
        }
      }
    } catch (error) {
      console.error('Failed to check upload status:', error);
    }
  },

  setCurrentProject: (project: Project | null) => {
    set({ currentProject: project });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      projects: [],
      currentProject: null,
      uploadStatus: null,
      isLoading: false,
      isCreating: false,
      isDeleting: false,
      isUploading: false,
      error: null,
      page: 1,
      limit: 10,
      total: 0,
      hasMore: false,
    });
  },
}));

export const useProjects = () => {
  return useProjectStore((state) => ({
    projects: state.projects,
    isLoading: state.isLoading,
    error: state.error,
    hasMore: state.hasMore,
    total: state.total,
    fetchProjects: state.fetchProjects,
  }));
};

export const useCurrentProject = () => {
  return useProjectStore((state) => state.currentProject);
};

export const useProjectActions = () => {
  return useProjectStore((state) => ({
    createProject: state.createProject,
    deleteProject: state.deleteProject,
    uploadFile: state.uploadFile,
    setCurrentProject: state.setCurrentProject,
    fetchProject: state.fetchProject,
    clearError: state.clearError,
  }));
};

export const useUploadStatus = () => {
  return useProjectStore((state) => ({
    uploadStatus: state.uploadStatus,
    isUploading: state.isUploading,
    checkUploadStatus: state.checkUploadStatus,
  }));
};