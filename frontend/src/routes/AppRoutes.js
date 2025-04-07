// src/routes/AppRoutes.js

import React from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Navbar from '../components/core/Navbar';
import PrivateRoute from '../PrivateRoute';
import InstantUpload from '../components/upload/InstantUpload';
import ScheduledUpload from '../components/upload/ScheduledUpload';
import UploadManagement from '../components/UploadManagement/UploadManagement';
import './AppRoutes.css';

import { useAuth } from '../context/AuthContext';

const AppRoutes = ({ selectedTab, setSelectedTab }) => {
    const navigate = useNavigate();
    const { isAuthenticated, logout } = useAuth();

    const handleLogout = () => {
        logout();         // clears storage and updates state
        navigate('/');    // redirect to login or home
    };

    return (
        <Routes>
            <Route
                path="/"
                element={
                    <PrivateRoute isAuthenticated={isAuthenticated}>
                        <div>
                            <Navbar
                                selectedTab={selectedTab}
                                setSelectedTab={setSelectedTab}
                                onLogout={handleLogout}
                            />
                            <div className="authenticated-content-container">
                                {selectedTab === 0 && <InstantUpload />}
                                {selectedTab === 1 && <ScheduledUpload />}
                                {selectedTab === 2 && <UploadManagement />}
                            </div>
                        </div>
                    </PrivateRoute>
                }
            />
        </Routes>
    );
};

export default AppRoutes;
