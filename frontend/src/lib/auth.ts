/**
 * Authentication Utilities
 * 
 * Manages JWT tokens, authentication state, and token refresh logic.
 */

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  created_at: string;
  last_sign_in_at?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Storage keys
const ACCESS_TOKEN_KEY = 'smartquery_access_token';
const REFRESH_TOKEN_KEY = 'smartquery_refresh_token';
const TOKEN_EXPIRY_KEY = 'smartquery_token_expiry';
const USER_KEY = 'smartquery_user';

// Token management utilities
export const TokenManager = {
  getAccessToken: (): string | null => {
    return localStorage.getItem('accessToken');
  },
  
  getRefreshToken: (): string | null => {
    return localStorage.getItem('refreshToken');
  },
  
  getTokenExpiry: (): number | null => {
    const expiry = localStorage.getItem('tokenExpiry');
    return expiry ? parseInt(expiry, 10) : null;
  },
  
  setTokens: (accessToken: string, refreshToken: string, expiresIn: number): void => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('tokenExpiry', (Date.now() + expiresIn * 1000).toString());
  },
  
  clearTokens: (): void => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('tokenExpiry');
  },
  
  isTokenExpired: (): boolean => {
    const expiry = TokenManager.getTokenExpiry();
    return expiry ? Date.now() > expiry : true;
  },
  
  hasValidTokens: (): boolean => {
    const accessToken = TokenManager.getAccessToken();
    const refreshToken = TokenManager.getRefreshToken();
    return !!(accessToken && refreshToken && !TokenManager.isTokenExpired());
  },
};

// User management utilities
export const UserManager = {
  getUser: (): any => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  setUser: (user: any): void => {
    localStorage.setItem('user', JSON.stringify(user));
  },
  
  clearUser: (): void => {
    localStorage.removeItem('user');
  },
};

/**
 * Authentication service
 */
export class AuthService {
  private static refreshPromise: Promise<AuthTokens> | null = null;

  /**
   * Refresh access token using refresh token
   */
  static async refreshToken(): Promise<AuthTokens> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.performTokenRefresh();
    
    try {
      const result = await this.refreshPromise;
      return result;
    } finally {
      this.refreshPromise = null;
    }
  }

  /**
   * Perform the actual token refresh request
   */
  private static async performTokenRefresh(): Promise<AuthTokens> {
    const refreshToken = TokenManager.getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error(`Token refresh failed: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.success || !data.data) {
        throw new Error('Invalid refresh response');
      }

      const { access_token, refresh_token, expires_in } = data.data;
      
      // Store new tokens
      TokenManager.setTokens(access_token, refresh_token, expires_in);
      
      return {
        accessToken: access_token,
        refreshToken: refresh_token,
        expiresAt: Date.now() + expires_in * 1000,
      };
    } catch (error) {
      // Clear tokens on refresh failure
      TokenManager.clearTokens();
      UserManager.clearUser();
      throw error;
    }
  }

  /**
   * Get current authentication state
   */
  static getAuthState(): AuthState {
    const user = UserManager.getUser();
    const isAuthenticated = TokenManager.hasValidTokens();
    
    return {
      user,
      isAuthenticated,
      isLoading: false,
    };
  }

  /**
   * Logout user
   */
  static async logout(): Promise<void> {
    try {
      // Call logout endpoint if we have a valid token
      const accessToken = TokenManager.getAccessToken();
      if (accessToken) {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      // Always clear local storage
      TokenManager.clearTokens();
      UserManager.clearUser();
    }
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    return TokenManager.hasValidTokens();
  }

  /**
   * Get current user
   */
  static getCurrentUser(): User | null {
    return UserManager.getUser();
  }
}

// Export convenience functions
export const getAccessToken = TokenManager.getAccessToken;
export const setTokens = TokenManager.setTokens;
export const clearTokens = TokenManager.clearTokens;
export const refreshToken = AuthService.refreshToken;
export const logout = AuthService.logout;
export const isAuthenticated = AuthService.isAuthenticated;
export const getCurrentUser = AuthService.getCurrentUser;

// Additional convenience functions for backward compatibility
export const authApi = {
  googleLogin: async (data: { google_token: string }) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
  getCurrentUser: async () => {
    const accessToken = getAccessToken();
    if (!accessToken) {
      throw new Error('No access token available');
    }
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    return response.json();
  },
  logout: async () => {
    return logout();
  },
  refreshToken: async () => {
    return refreshToken();
  },
}; 