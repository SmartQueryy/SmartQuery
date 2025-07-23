// Basic API client for tests
export const api = {
  auth: {
    googleLogin: async (data: { google_token: string }) => {
      // Mock implementation
      return {
        success: true,
        data: {
          user: {
            id: '1',
            name: 'Test User',
            email: 'test@example.com',
            avatar_url: '',
            created_at: '2024-01-01T00:00:00Z',
            last_sign_in_at: '2024-01-01T12:00:00Z',
          },
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          expires_in: 3600,
        },
      };
    },
    getCurrentUser: async () => {
      return {
        success: true,
        data: {
          user: {
            id: '1',
            name: 'Test User',
            email: 'test@example.com',
            avatar_url: '',
            created_at: '2024-01-01T00:00:00Z',
            last_sign_in_at: '2024-01-01T12:00:00Z',
          },
        },
      };
    },
    logout: async () => ({ success: true }),
    refreshToken: async () => ({
      success: true,
      data: {
        access_token: 'new-mock-access-token',
        refresh_token: 'new-mock-refresh-token',
        expires_in: 3600,
      },
    }),
  },
  projects: {
    getProjects: async () => ({ success: true, data: [] }),
    createProject: async (data: any) => ({ success: true, data: { id: '1', name: data.name } }),
    getProject: async (id: string) => ({ success: true, data: { id, name: 'Mock Project' } }),
    deleteProject: async (id: string) => ({ success: true }),
    getUploadUrl: async (projectId: string) => ({ success: true, data: { upload_url: 'http://mock.upload.url' } }),
    getProjectStatus: async (projectId: string) => ({ success: true, data: { status: 'completed' } }),
  },
  chat: {
    sendMessage: async (projectId: string, message: string) => ({ success: true, data: { message: 'Mock response', result_type: 'text', result: 'Mock result' } }),
    getMessages: async (projectId: string) => ({ success: true, data: [] }),
    getPreview: async (projectId: string) => ({ success: true, data: { headers: ['col1'], rows: [['val1']] } }),
    getSuggestions: async (projectId: string) => ({ success: true, data: ['suggestion1'] }),
  },
  system: {
    healthCheck: async () => ({ success: true }),
    systemStatus: async () => ({ success: true, data: { status: 'healthy' } }),
  },
};

// Export individual API modules for backward compatibility
export const authApi = api.auth;
export const projectApi = api.projects;
export const chatApi = api.chat;
export const systemApi = api.system; 