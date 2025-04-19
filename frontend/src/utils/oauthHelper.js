// utils/oauthHelper.js
import { googleOAuthService } from '../services/googleOAuthService.ts';
import { setLocalStorage, getStoredToken, isTokenExpired, getUser, clearStorage } from './tokenManager';
import { redirectToOAuth } from './redirectHelper.js';

export const getUserId = () => {
    const user = getUser();
    if (!user?.id) throw new Error('No user ID found in local storage.');
    return user.id;
};

export const getUserEmail = () => {
    const user = getUser();
    if (!user?.email) throw new Error('No user email found in local storage.');
    return user.email;
};

export const handleGoogleLoginResponse = async (data) => {
    if (data.redirect && data.oauth_url) {
        window.location.href = data.oauth_url;
        return null;
    }
    if (data.jwt && data.user_id && data.user_email) {
        setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
        return;
    }

    throw new Error('Invalid login response from backend.');
};

export const handleGoogleCallbackFlow = async ({ code, user_id, user_email }) => {
    const data = await googleOAuthService.callback({ code, user_id, user_email });

    if (!data.jwt || !data.user_id || !data.user_email) {
        throw new Error('Invalid callback response from backend.');
    }

    setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
    return { id: data.user_id, email: data.user_email };
};

export const handleGoogleRefreshFlow = async () => {
    const data = await googleOAuthService.refreshToken();

    if (data.redirect && data.oauth_url) {
        redirectToOAuth(data.oauth_url)
    }

    if (!data.jwt) throw new Error('Failed to refresh token: No JWT in response.');
    setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
};

export const getToken = async () => {
    const token = getStoredToken();
    if (!token) return null;

    if (isTokenExpired()) {
        console.warn("Token expired. Attempting refresh...");
        try {
            await handleGoogleRefreshFlow();
            return token;
        } catch (err) {
            console.error("Token refresh failed:", err);
            clearStorage();
            return null;
        }
    }

    return token;
};
