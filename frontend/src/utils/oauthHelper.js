// utils/oauthHelper.js
import { setLocalStorage, getUserId } from './tokenManager';
import { toastHelper } from './toastHelper';

/**
 * Redirect user to Google OAuth URL.
 */
export const redirectToOAuth = (oauthUrl) => {
    if (!oauthUrl) return;
    window.location.href = oauthUrl;
};

/**
 * Handles redirect if the backend tells us to.
 */
export const handleOAuthRedirect = (data) => {
    if (data.redirect && data.oauth_url) {
        redirectToOAuth(data.oauth_url);
        return true;
    }
    return false;
};

/**
 * Handles successful OAuth response.
 */
export const handleOAuthResponse = (data, setIsAuthenticated, setUser = null, navigate = null) => {
    if (data.jwt && data.user_id && data.user_email) {
        setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
        setIsAuthenticated(true);
        if (setUser) setUser({ id: data.user_id, email: data.user_email });
        toastHelper.newMessage('success', 'Login Successful', 'You are now authenticated.');
        if (navigate) navigate('/');
    } else {
        throw new Error('Authentication failed: Missing token or user info.');
    }
};

/**
 * Handles errors during the OAuth flow.
 */
export const handleOAuthError = (message = 'OAuth failed', navigate = null) => {
    toastHelper.newMessage('error', 'Login Failed', message);
    if (navigate) navigate('/');
};

/**
 * Handles refresh token response from backend and either redirects or stores new token.
 */
let isRedirecting = false;

export const handleOAuthRefresh = async (googleOAuthService) => {
    const userId = getUserId();

    try {
        const response = await googleOAuthService.refreshToken({ user_id: userId });
        const data = response;

        if (data.redirect && data.oauth_url) {
            if (isRedirecting) return;
            isRedirecting = true;
            redirectToOAuth(data.oauth_url);
            return;
        }

        if (!data.jwt) throw new Error('Failed to refresh token: No JWT in response.');

        setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
    } catch (err) {
        console.error('Refresh token failed:', err);
        throw err;
    }
};
