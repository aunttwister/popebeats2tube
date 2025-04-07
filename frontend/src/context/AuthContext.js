import React, { createContext, useContext, useEffect, useState } from 'react';
import { getToken, setLocalStorage, clearStorage } from '../utils/tokenManager';
import { googleOAuthService } from '../services/googleOAuthService.ts';
import { toastHelper } from '../utils/toastHelper';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkToken = async () => {
            try {
                const token = await getToken();
                setIsAuthenticated(!!token);
                if (!token) {
                    toastHelper.newMessage('info', 'Session Expired', 'Please log in again.');
                }
            } catch (error) {
                console.error('Token check error:', error);
                setIsAuthenticated(false);
                toastHelper.newMessage('error', 'Session Error', 'Please log in again.');
            } finally {
                setIsLoading(false);
            }
        };

        checkToken();
    }, []);

    const login = async (credentialResponse) => {
        const token = credentialResponse.credential;
        setIsLoading(true);

        try {
            const data = await googleOAuthService.login(token);
            if (data.redirect) {
                const oauthUrl = `${data.oauth_url}&state=${encodeURIComponent(data.user_id)}`;
                window.open(oauthUrl, '_self');
            } else if (data.jwt) {
                setLocalStorage(data.jwt, data.expires_in, data.user_id);
                setIsAuthenticated(true);
                toastHelper.newMessage('success', 'Login Successful', 'You are now authenticated.');
            } else {
                throw new Error('Unexpected backend response');
            }
        } catch (err) {
            console.error(err);
            toastHelper.newMessage('error', 'Login Failed', 'Try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        clearStorage();
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
