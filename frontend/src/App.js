import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import GoogleCallbackHandler from './components/auth/GoogleCallbackHandler';
import LoginPage from './components/auth/LoginPage';
import AppRoutes from './routes/AppRoutes.js';
import './App.css';
import { useAuth } from './context/AuthContext';
import NotFoundPage from './components/common/NotFoundPage';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;
const GOOGLE_OAUTH_CALLBACK_PATH = process.env.REACT_APP_GOOGLE_OAUTH_CALLBACK_PATH || "/google-oauth/login-callback";

function App() {
    const { isAuthenticated, isLoading, login } = useAuth();
    const [selectedTab, setSelectedTab] = useState(0);

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
                    <Route path={GOOGLE_OAUTH_CALLBACK_PATH} element={<GoogleCallbackHandler />} />

                    {isAuthenticated ? (
                        <Route
                            path="/*"
                            element={
                                <AppRoutes
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
                                    handleLoginSuccess={login}
                                    GOOGLE_CLIENT_ID={GOOGLE_CLIENT_ID}
                                />
                            }
                        />
                    )}

                    <Route path="*" element={<NotFoundPage />} />
                </Routes>
            </Router>
        </>
    );
}

export default App;
