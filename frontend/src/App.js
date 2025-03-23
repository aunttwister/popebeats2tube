import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import GoogleCallbackHandler from './components/auth/GoogleCallbackHandler';
import LoginPage from './components/auth/LoginPage';
import AuthenticatedRoutes from './components/layout/AuthenticatedRoutes';
import { setToken } from './utils/tokenManager';
import './App.css';
import { toastHelper } from './utils/toastHelper';
import { getToken } from './utils/tokenManager'

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

function App() {
    const [selectedTab, setSelectedTab] = useState(0);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const checkToken = async () => {
            try {
                const token = await getToken(); // Get or refresh the token
                if (token) {
                    setIsAuthenticated(true);
                } else {
                    setIsAuthenticated(false);
                }
            } catch (error) {
                console.error('Error checking token:', error);
                setIsAuthenticated(false);
                toastHelper.newMessage('error', 'Session Expired', 'Please log in again.');
            } finally {
                setIsLoading(false); // Stop loading after token check
            }
        };

        checkToken();
    }, []);

    const handleLoginSuccess = (credentialResponse) => {
        const token = credentialResponse.credential;
        setIsLoading(true);
    
        fetch(`${process.env.REACT_APP_API_BASE_URL}/auth/google`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
        })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Failed to authenticate with backend.');
            })
            .then((data) => {
                if (data.redirect) {
                    const oauthUrl = `${data.oauth_url}&state=${encodeURIComponent(data.user_id)}`;
                    window.open(oauthUrl, '_self');
                } else if (data.jwt) {
                    setToken(data.jwt, data.expires_in);
                    localStorage.setItem('userId', data.user_id);
                    setIsAuthenticated(true);
                    toastHelper.newMessage('success', 'Login Successful', 'You are now authenticated.');
                } else {
                    throw new Error('Unexpected response from backend.');
                }
            })
            .catch((error) => {
                console.error('Error during login:', error);
                toastHelper.newMessage('error', 'Login Failed', 'Could not authenticate user. Please try again.');
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    return (
        <>
            <ToastContainer
                position="bottom-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop
                closeOnClick
                pauseOnHover
                draggable
                theme="colored"
            />
            <Router>
                <Routes>
                    <Route
                        path="/auth/google/callback"
                        element={<GoogleCallbackHandler setIsAuthenticated={setIsAuthenticated} />}
                    />
                    {isAuthenticated ? (
                        <Route
                            path="/*"
                            element={
                                <AuthenticatedRoutes
                                    isAuthenticated={isAuthenticated}
                                    selectedTab={selectedTab}
                                    setSelectedTab={setSelectedTab}
                            />
                            }
                        />
                    ) : (
                        <Route
                            path="/*"
                            element={
                                <LoginPage
                                    isLoading={isLoading}
                                    handleLoginSuccess={handleLoginSuccess}
                                    GOOGLE_CLIENT_ID={GOOGLE_CLIENT_ID}
                                />
                            }
                        />
                    )}
                </Routes>
            </Router>
        </>
    );
}

export default App;
