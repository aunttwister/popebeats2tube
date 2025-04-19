// services/googleOAuthService.ts
import apiClient from './apiClient.ts';
import { getUserId } from '../utils/oauthHelper.js';

interface OAuthLoginResponse {
  redirect?: boolean;
  oauth_url?: string;
  user_id?: string;
  jwt?: string;
  expires_in?: number;
  user_email?: string;
}

interface GoogleCallbackPayload {
  code: string;
  user_id: string;
  user_email: string;
}

export const googleOAuthService = {
  login: async (token: string): Promise<OAuthLoginResponse> => {
    const response = await apiClient.post<OAuthLoginResponse>('/google-oauth/login', { token });
    return response.data;
  },

  callback: async (payload: GoogleCallbackPayload): Promise<OAuthLoginResponse> => {
    const response = await apiClient.post<OAuthLoginResponse>('/google-oauth/login-callback', payload);
    return response.data;
  },

  refreshToken: async (): Promise<OAuthLoginResponse> => {
    const userId = getUserId();
    const response = await apiClient.post<OAuthLoginResponse>('/google-oauth/token-refresh', {
        user_id: userId,
    });
    return response.data;
  }
};
