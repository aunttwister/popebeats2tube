import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import GoogleCallbackHandler from './components/auth/GoogleCallbackHandler';
import LoginPage from './components/auth/LoginPage';
import AppRoutes from './routes/AppRoutes.js';
import './App.css';
import { useAuth } from './context/AuthContext';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

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
                    <Route
                        path="/auth/google/callback"
                        element={<GoogleCallbackHandler />} // You can inject set auth state here if needed
                    />
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
                </Routes>
            </Router>
        </>
    );
}

export default App;
