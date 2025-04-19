// utils/tokenManager.js

export const setLocalStorage = (token, expiresIn, userId, userEmail) => {
    localStorage.setItem('jwt', token);
    localStorage.setItem('jwtExpiry', getFutureTimestamp(expiresIn));
    localStorage.setItem('user', JSON.stringify({ id: userId, email: userEmail }));
};

export const getStoredToken = () => localStorage.getItem('jwt');

export const getTokenExpiry = () => {
    const expiry = localStorage.getItem('jwtExpiry');
    return expiry ? parseInt(expiry, 10) : NaN;
};

export const isTokenExpired = () => {
    const expiry = getTokenExpiry();
    return isNaN(expiry) || Date.now() >= expiry;
};

export const getUser = () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : {};
};

export const clearStorage = () => {
    localStorage.removeItem('jwt');
    localStorage.removeItem('jwtExpiry');
    localStorage.removeItem('user');
};

const getFutureTimestamp = (expiresInSeconds) => {
    return (Date.now() + expiresInSeconds * 1000).toString();
};