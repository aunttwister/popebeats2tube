import React, { createContext, useContext, useEffect, useState } from 'react';
import {
    clearStorage,
    getUser
} from '../../utils/tokenManager.js';

import {
    getToken,
    handleGoogleLoginResponse
} from '../../utils/oauthHelper.js';

import { googleOAuthService } from '../../services/googleOAuthService.ts';
import { toastHelper } from '../../utils/toastHelper.js';
import { redirectToOAuth } from '../../utils/redirectHelper.js';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const initSession = async () => {
            try {
                const token = await getToken(); // handles null, expiry, and refresh
                if (!token) {
                    finalizeSession(false);
                    return;
                }

                const storedUser = getUser();
                if (storedUser?.id && storedUser?.email) {
                    finalizeSession(true);
                } else {
                    toastHelper.newMessage('info', 'Session Expired', 'Please log in again.');
                    clearStorage();
                    finalizeSession(false);
                }
            } catch (err) {
                console.error("Session error:", err);
                toastHelper.newMessage('error', 'Session Error', 'Please log in again.');
                clearStorage();
                finalizeSession(false);
            }
        };

        const finalizeSession = (authenticated) => {
            setIsAuthenticated(authenticated);
            setIsLoading(false);
        };

        initSession();
    }, []);

    const login = async (credentialResponse) => {
        const rawToken = credentialResponse.credential; // plain JWT string
        setIsLoading(true);

        try {
            const data = await googleOAuthService.login(rawToken); // ✅ raw token only

            if (data.redirect && data.oauth_url) {
                redirectToOAuth(data.oauth_url);
            } else {
                handleGoogleLoginResponse(data);
                setIsAuthenticated(true);
                toastHelper.newMessage('success', 'Login Successful', 'You are now authenticated.');
            }
        } catch (err) {
            console.error("Login failed:", err);
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
        <AuthContext.Provider
            value={{
                isAuthenticated,
                isLoading,
                setIsAuthenticated,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
