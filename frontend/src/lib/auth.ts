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

/**
 * Token management utilities
 */
export class TokenManager {
  /**
   * Get access token from storage
   */
  static getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  /**
   * Get refresh token from storage
   */
  static getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Get token expiry time
   */
  static getTokenExpiry(): number | null {
    if (typeof window === 'undefined') return null;
    const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY);
    return expiry ? parseInt(expiry, 10) : null;
  }

  /**
   * Set tokens in storage
   */
  static setTokens(accessToken: string, refreshToken: string, expiresIn: number): void {
    if (typeof window === 'undefined') return;
    
    const expiresAt = Date.now() + expiresIn * 1000;
    
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiresAt.toString());
  }

  /**
   * Clear all tokens from storage
   */
  static clearTokens(): void {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
    localStorage.removeItem(USER_KEY);
  }

  /**
   * Check if access token is expired
   */
  static isTokenExpired(): boolean {
    const expiry = this.getTokenExpiry();
    if (!expiry) return true;
    
    // Consider token expired if it expires within 30 seconds
    return Date.now() >= (expiry - 30000);
  }

  /**
   * Check if user has valid tokens
   */
  static hasValidTokens(): boolean {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();
    
    return !!(accessToken && refreshToken && !this.isTokenExpired());
  }
}

/**
 * User management utilities
 */
export class UserManager {
  /**
   * Get user from storage
   */
  static getUser(): User | null {
    if (typeof window === 'undefined') return null;
    
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  }

  /**
   * Set user in storage
   */
  static setUser(user: User): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * Clear user from storage
   */
  static clearUser(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(USER_KEY);
  }
}

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