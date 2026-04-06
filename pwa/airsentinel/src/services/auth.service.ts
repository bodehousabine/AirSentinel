import apiClient from "./apiClient";

export interface UserResponse {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  avatar_url?: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  /**
   * Enregistre un nouvel utilisateur
   */
  register: async (email: string, full_name: string, password: string): Promise<UserResponse> => {
    const response = await apiClient.post<UserResponse>("auth/register", {
      email,
      full_name,
      password,
    });
    return response.data;
  },

  /**
   * Connecte un utilisateur et retourne le token
   */
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>("auth/login", {
      email,
      password,
    });
    // Store token automatically upon successful login
    if (response.data.access_token && typeof window !== "undefined") {
      localStorage.setItem("access_token", response.data.access_token);
    }
    return response.data;
  },

  /**
   * Récupère le profil de l'utilisateur connecté
   */
  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>("auth/me");
    return response.data;
  },

  /**
   * Déconnexion de l'utilisateur (nettoyage local)
   */
  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
    }
  },
  
  /**
   * Vérifie si un utilisateur est actuellement connecté
   */
  isAuthenticated: (): boolean => {
    if (typeof window !== "undefined") {
      return !!localStorage.getItem("access_token");
    }
    return false;
  }
};
