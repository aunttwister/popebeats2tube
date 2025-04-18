import { googleOAuthService } from '../services/googleOAuthService.ts';

export const setLocalStorage = (token, expiresIn, userId, userEmail) => {
    localStorage.setItem('jwt', token);
    localStorage.setItem('jwtExpiry', getFutureTimestamp(expiresIn));

    // ✅ Optional unified object, purely for convenience access
    localStorage.setItem('user', JSON.stringify({ id: userId, email: userEmail }));
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
        clearStorage(); // Prevent infinite redirect loops
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

// ✅ Fallback-compatible user getter
export const getUser = () => {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : {};
};

export const getUserId = () => {
    const userId = getUser()?.id;
    if (!userId) throw new Error('No user ID found in local storage.');
    return userId;
};

export const getUserEmail = () => {
    const userEmail = getUser()?.email;
    if (!userEmail) throw new Error('No user email found in local storage.');
    return userEmail;
};

export const clearStorage = () => {
    localStorage.removeItem("jwt");
    localStorage.removeItem("jwtExpiry");
    localStorage.removeItem("user");
};
