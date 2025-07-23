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
    logout: async () => {
      return { success: true };
    },
    refreshToken: async () => {
      return {
        success: true,
        data: {
          access_token: 'new-access-token',
          refresh_token: 'new-refresh-token',
          expires_in: 3600,
        },
      };
    },
  },
  projects: {
    getProjects: async () => {
      return {
        success: true,
        data: {
          projects: [],
        },
      };
    },
    createProject: async (data: any) => {
      return {
        success: true,
        data: {
          project: {
            id: '1',
            name: data.name,
            created_at: '2024-01-01T00:00:00Z',
          },
        },
      };
    },
    getProject: async (id: string) => {
      return {
        success: true,
        data: {
          project: {
            id,
            name: 'Test Project',
            created_at: '2024-01-01T00:00:00Z',
          },
        },
      };
    },
    deleteProject: async (id: string) => {
      return { success: true };
    },
    getUploadUrl: async (id: string) => {
      return {
        success: true,
        data: {
          upload_url: 'https://example.com/upload',
        },
      };
    },
    getProjectStatus: async (id: string) => {
      return {
        success: true,
        data: {
          status: 'completed',
        },
      };
    },
  },
  chat: {
    sendMessage: async (projectId: string, message: string) => {
      return {
        success: true,
        data: {
          response: 'Mock response',
        },
      };
    },
    getMessages: async (projectId: string) => {
      return {
        success: true,
        data: {
          messages: [],
        },
      };
    },
    getPreview: async (projectId: string) => {
      return {
        success: true,
        data: {
          preview: [],
        },
      };
    },
    getSuggestions: async (projectId: string) => {
      return {
        success: true,
        data: {
          suggestions: [],
        },
      };
    },
  },
  system: {
    healthCheck: async () => {
      return {
        success: true,
        data: {
          status: 'healthy',
        },
      };
    },
    systemStatus: async () => {
      return {
        success: true,
        data: {
          status: 'operational',
        },
      };
    },
  },
}; 