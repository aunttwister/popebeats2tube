export const setToken = (token, expiresIn, userId) => {
    localStorage.setItem('jwt', token);
    const expiryTime = Date.now() + expiresIn * 1000;
    localStorage.setItem('jwtExpiry', expiryTime);
    localStorage.setItem('userId', userId)
};

export const getToken = async () => {
    try {
        const token = localStorage.getItem('jwt');
        const expiryTime = parseInt(localStorage.getItem('jwtExpiry'), 10);
        const now = Date.now();
        if (token == null)
            return;

        if (isNaN(expiryTime) || now >= expiryTime) {
            console.error("Invalid expiry time. Refreshing token...");
            await refreshToken();
            return localStorage.getItem('jwt'); // Return the refreshed token
        } else if (now >= expiryTime) {
            console.warn("Token has expired. Refreshing token...");
        } else {
            console.log("Token is still valid.");
        }

        return token; // Return the existing token if valid
    } catch (error) {
        console.error("Error in getToken:", error);
        throw error; // Re-throw the error to handle it upstream
    }
};

export const refreshToken = async () => {
    const userId = localStorage.getItem('userId');
    console.log(`${process.env.REACT_APP_API_BASE_URL}`)
    const apiUrl = `${process.env.REACT_APP_API_BASE_URL}/auth/token-refresh`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
    });

    if (!response.ok) throw new Error('Failed to refresh token.');
    const data = await response.json();
    setToken(data.jwt, data.expires_in, data.user_id);
};
