import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, LoginCredentials, User } from '../services/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = authService.getToken();
        if (token) {
          // TODO: Decode JWT token to get user info
          // For now, we'll just check if token exists
          // In production, decode token and extract user info
          const tokenParts = token.split('.');
          if (tokenParts.length === 3) {
            try {
              const payload = JSON.parse(atob(tokenParts[1]));
              setUser({
                user_id: payload.sub || '',
                tenant_id: payload.tenant_id || '',
                roles: payload.roles || [],
              });
            } catch (e) {
              // Invalid token, clear it
              authService.logout();
            }
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        authService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      await authService.login(credentials);
      
      // Decode token to get user info
      const token = authService.getToken();
      if (token) {
        const tokenParts = token.split('.');
        if (tokenParts.length === 3) {
          const payload = JSON.parse(atob(tokenParts[1]));
          setUser({
            user_id: payload.sub || '',
            tenant_id: payload.tenant_id || '',
            roles: payload.roles || [],
          });
        }
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
