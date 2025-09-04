import { describe, it, expect, beforeEach, vi } from 'vitest';
import { act } from '@testing-library/react';
import { useProjectStore } from '../project';
import { api } from '../../api';

// Mock the API client
vi.mock('../../api', () => ({
  api: {
    projects: {
      getProjects: vi.fn(),
      getProject: vi.fn(),
      createProject: vi.fn(),
      deleteProject: vi.fn(),
      getUploadUrl: vi.fn(),
      getProjectStatus: vi.fn(),
    },
  },
}));

// Mock fetch for file upload
global.fetch = vi.fn();

describe('Project Store', () => {
  beforeEach(() => {
    // Reset store state
    useProjectStore.setState({
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
    
    // Clear all mocks
    vi.clearAllMocks();
  });

  describe('fetchProjects', () => {
    it('should fetch projects successfully', async () => {
      const mockProjects = [
        { id: '1', name: 'Project 1', description: 'Test project 1', status: 'ready', user_id: 'user1', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        { id: '2', name: 'Project 2', description: 'Test project 2', status: 'processing', user_id: 'user1', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      ];

      vi.mocked(api.projects.getProjects).mockResolvedValue({
        success: true,
        data: {
          items: mockProjects,
          total: 2,
          page: 1,
          limit: 10,
          hasMore: false,
        },
      });

      const { fetchProjects } = useProjectStore.getState();
      
      await act(async () => {
        await fetchProjects();
      });

      const state = useProjectStore.getState();
      expect(state.projects).toEqual(mockProjects);
      expect(state.total).toBe(2);
      expect(state.hasMore).toBe(false);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle fetch error', async () => {
      vi.mocked(api.projects.getProjects).mockResolvedValue({
        success: false,
        error: 'Failed to fetch projects',
      });

      const { fetchProjects } = useProjectStore.getState();
      
      await act(async () => {
        await fetchProjects();
      });

      const state = useProjectStore.getState();
      expect(state.projects).toEqual([]);
      expect(state.error).toBe('Failed to fetch projects');
      expect(state.isLoading).toBe(false);
    });
  });

  describe('createProject', () => {
    it('should create project successfully', async () => {
      const newProject = {
        id: '3',
        name: 'New Project',
        description: 'A new test project',
        status: 'uploading' as const,
        user_id: 'user1',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      vi.mocked(api.projects.createProject).mockResolvedValue({
        success: true,
        data: {
          project: newProject,
          upload_url: 'https://minio.example.com/upload',
        },
      });

      const { createProject } = useProjectStore.getState();
      
      const result = await act(async () => {
        return await createProject({ name: 'New Project', description: 'A new test project' });
      });

      expect(result).toEqual(newProject);
      
      const state = useProjectStore.getState();
      expect(state.projects).toContainEqual(newProject);
      expect(state.currentProject).toEqual(newProject);
      expect(state.isCreating).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle create error', async () => {
      vi.mocked(api.projects.createProject).mockResolvedValue({
        success: false,
        error: 'Failed to create project',
      });

      const { createProject } = useProjectStore.getState();
      
      const result = await act(async () => {
        return await createProject({ name: 'New Project', description: 'Test' });
      });

      expect(result).toBeNull();
      
      const state = useProjectStore.getState();
      expect(state.error).toBe('Failed to create project');
      expect(state.isCreating).toBe(false);
    });
  });

  describe('deleteProject', () => {
    it('should delete project successfully', async () => {
      // Set initial projects
      useProjectStore.setState({
        projects: [
          { id: '1', name: 'Project 1', description: 'Test', status: 'ready', user_id: 'user1', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: '2', name: 'Project 2', description: 'Test', status: 'ready', user_id: 'user1', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ],
      });

      vi.mocked(api.projects.deleteProject).mockResolvedValue({
        success: true,
        data: { message: 'Project deleted' },
      });

      const { deleteProject } = useProjectStore.getState();
      
      const result = await act(async () => {
        return await deleteProject('1');
      });

      expect(result).toBe(true);
      
      const state = useProjectStore.getState();
      expect(state.projects).toHaveLength(1);
      expect(state.projects[0].id).toBe('2');
      expect(state.isDeleting).toBe(false);
    });
  });

  describe('uploadFile', () => {
    it('should upload file successfully', async () => {
      const mockFile = new File(['test content'], 'test.csv', { type: 'text/csv' });
      
      vi.mocked(api.projects.getUploadUrl).mockResolvedValue({
        success: true,
        data: {
          upload_url: 'https://minio.example.com/upload',
          upload_fields: {
            key: 'test-key',
            policy: 'test-policy',
          },
        },
      });

      vi.mocked(api.projects.getProjectStatus).mockResolvedValue({
        success: true,
        data: {
          status: 'processing',
          message: 'Processing file',
          progress: 50,
        },
      });

      vi.mocked(global.fetch).mockResolvedValue({
        ok: true,
      } as Response);

      const { uploadFile } = useProjectStore.getState();
      
      const result = await act(async () => {
        return await uploadFile('project1', mockFile);
      });

      expect(result).toBe(true);
      expect(vi.mocked(global.fetch)).toHaveBeenCalledWith(
        'https://minio.example.com/upload',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      );
      
      const state = useProjectStore.getState();
      expect(state.isUploading).toBe(false);
      expect(state.uploadStatus).toEqual({
        status: 'processing',
        message: 'Processing file',
        progress: 50,
      });
    });

    it('should handle upload error', async () => {
      const mockFile = new File(['test content'], 'test.csv', { type: 'text/csv' });
      
      vi.mocked(api.projects.getUploadUrl).mockResolvedValue({
        success: false,
        error: 'Failed to get upload URL',
      });

      const { uploadFile } = useProjectStore.getState();
      
      const result = await act(async () => {
        return await uploadFile('project1', mockFile);
      });

      expect(result).toBe(false);
      
      const state = useProjectStore.getState();
      expect(state.error).toBe('Failed to get upload URL');
      expect(state.isUploading).toBe(false);
    });
  });

  describe('convenience hooks', () => {
    it('useProjects should return projects data', () => {
      const mockProjects = [
        { id: '1', name: 'Project 1', description: 'Test', status: 'ready' as const, user_id: 'user1', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
      ];
      
      useProjectStore.setState({
        projects: mockProjects,
        isLoading: false,
        error: null,
        hasMore: false,
        total: 1,
      });

      const state = useProjectStore.getState();
      expect(state.projects).toEqual(mockProjects);
      expect(state.isLoading).toBe(false);
    });

    it('setCurrentProject should update current project', () => {
      const project = { 
        id: '1', 
        name: 'Project 1', 
        description: 'Test', 
        status: 'ready' as const, 
        user_id: 'user1',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      const { setCurrentProject } = useProjectStore.getState();
      
      act(() => {
        setCurrentProject(project);
      });

      const state = useProjectStore.getState();
      expect(state.currentProject).toEqual(project);
    });

    it('reset should clear all state', () => {
      useProjectStore.setState({
        projects: [{ id: '1', name: 'Test', description: 'Test', status: 'ready', user_id: 'user1', created_at: new Date().toISOString(), updated_at: new Date().toISOString() }],
        currentProject: { id: '1', name: 'Test', description: 'Test', status: 'ready', user_id: 'user1', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        error: 'Some error',
      });

      const { reset } = useProjectStore.getState();
      
      act(() => {
        reset();
      });

      const state = useProjectStore.getState();
      expect(state.projects).toEqual([]);
      expect(state.currentProject).toBeNull();
      expect(state.error).toBeNull();
    });
  });
});