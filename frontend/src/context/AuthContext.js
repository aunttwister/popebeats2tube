// context/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import {
    getToken,
    setLocalStorage,
    clearStorage,
    getUser,
} from '../utils/tokenManager';
import { googleOAuthService } from '../services/googleOAuthService.ts';
import { toastHelper } from '../utils/toastHelper';
import { redirectToOAuth } from '../utils/redirectHelper.js';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState({ id: null, email: null });

    useEffect(() => {
        const checkToken = async () => {
            try {
                const storedToken = localStorage.getItem('jwt'); // ✅ check manually first
                if (!storedToken) {
                    setIsAuthenticated(false);
                    setIsLoading(false);
                    return;
                }
    
                const token = await getToken(); // ⬅️ now safe to call (may refresh if expired)
                const storedUser = getUser();
    
                setIsAuthenticated(!!token);
    
                if (token && storedUser?.id && storedUser?.email) {
                    setUser(storedUser);
                } else {
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
            if (data.redirect && data.oauth_url) {
                redirectToOAuth(data.oauth_url);
            } else if (data.jwt && data.user_id && data.user_email) {
                setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
                setUser({ id: data.user_id, email: data.user_email });
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
        setUser({ id: null, email: null });
    };

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated,
                isLoading,
                setIsAuthenticated,
                login,
                logout,
                user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
