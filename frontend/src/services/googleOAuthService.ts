import apiClient from './apiClient.ts';
import { getUserId, setLocalStorage } from '../utils/tokenManager.js';

interface OAuthLoginResponse {
  redirect?: boolean;
  oauth_url?: string;
  user_id?: string;
  jwt?: string;
  expires_in?: number;
}

interface GoogleCallbackPayload {
  code: string;
  user_id: string;
}

let isRedirecting = false;

export const googleOAuthService = {
  login: async (token: string): Promise<OAuthLoginResponse> => {
    const response = await apiClient.post<OAuthLoginResponse>('/google-oauth/login', { token });
    return response.data;
  },

  callback: async (payload: GoogleCallbackPayload): Promise<OAuthLoginResponse> => {
    const response = await apiClient.post<OAuthLoginResponse>('/google-oauth/login-callback', payload);
    return response.data;
  },

  refreshToken: async (): Promise<void> => {
    const userId = getUserId();

    const response = await apiClient.post<OAuthLoginResponse>('/google-oauth/token-refresh', {
      user_id: userId,
    });

    const data = response.data;

    if (data.redirect && data.oauth_url && data.user_id) {
      if (isRedirecting) return; // ✅ lock it
      isRedirecting = true;
      const oauthUrl = `${data.oauth_url}&state=${encodeURIComponent(data.user_id)}`;
      window.location.href = oauthUrl;
      return;
    }

    if (!data.jwt) throw new Error('Failed to refresh token: No JWT in response.');

    setLocalStorage(data.jwt, data.expires_in, data.user_id);
  }
};
