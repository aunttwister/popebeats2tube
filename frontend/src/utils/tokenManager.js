import { googleOAuthService } from '../services/googleOAuthService.ts';

export const setLocalStorage = (token, expiresIn, userId) => {
    localStorage.setItem('jwt', token);
    localStorage.setItem('jwtExpiry', getFutureTimestamp(expiresIn));
    localStorage.setItem('userId', userId);
};

export const getToken = async () => {
    try {
        const token = getStoredToken();
        if (!token) return;

        if (isTokenExpired()) {
            console.warn("Token has expired or is invalid. Refreshing...");
            await googleOAuthService.refreshToken();
            return getStoredToken();
        }

        return token;
    } catch (error) {
        console.error("Error in getToken:", error);
        throw error;
    }
};

const isTokenExpired = () => {
    const expiryTime = getTokenExpiry();
    const now = Date.now();
    return isNaN(expiryTime) || now >= expiryTime;
};

const getStoredToken = () => localStorage.getItem('jwt');

const getTokenExpiry = () => {
    const expiry = localStorage.getItem('jwtExpiry');
    return expiry ? parseInt(expiry, 10) : NaN;
};

const getFutureTimestamp = (expiresInSeconds) => {
    return (Date.now() + expiresInSeconds * 1000).toString();
};

export const getUserId = () => {
    const userId = localStorage.getItem('userId');
    if (!userId) throw new Error('No user ID found in local storage.');
    return userId;
};

export const clearStorage = () => {
    localStorage.removeItem('jwt');
    localStorage.removeItem('jwtExpiry');
    localStorage.removeItem('userId');
};