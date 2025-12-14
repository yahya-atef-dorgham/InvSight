import apiClient from './api';

export interface LoginCredentials {
  username: string;
  password: string;
  tenant_id: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface User {
  user_id: string;
  tenant_id: string;
  roles: string[];
}

export const authService = {
  /**
   * Login user and store token.
   */
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const response = await apiClient.post<AuthToken>('/auth/login', credentials);
    const token = response.data;
    
    // Store token in localStorage
    localStorage.setItem('auth_token', token.access_token);
    
    return token;
  },

  /**
   * Logout user and clear token.
   */
  logout(): void {
    localStorage.removeItem('auth_token');
  },

  /**
   * Get stored auth token.
   */
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  /**
   * Check if user is authenticated.
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};

