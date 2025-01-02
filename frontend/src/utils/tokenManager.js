export const setToken = (token, expiresIn) => {
    localStorage.setItem('jwt', token);
    const expiryTime = Date.now() + expiresIn * 1000;
    localStorage.setItem('jwtExpiry', expiryTime);
};

export const getToken = async () => {
    const token = localStorage.getItem('jwt');
    const expiryTime = parseInt(localStorage.getItem('jwtExpiry'), 10);

    if (Date.now() >= expiryTime) {
        await refreshToken();
        return localStorage.getItem('jwt');
    } else {
        return token;
    }
};

export const refreshToken = async () => {
    const email = localStorage.getItem('userEmail');
    const response = await fetch('http://localhost:8000/auth/token-refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: email }),
    });

    if (!response.ok) throw new Error('Failed to refresh token.');
    const data = await response.json();
    setToken(data.jwt, data.expires_in);
};
