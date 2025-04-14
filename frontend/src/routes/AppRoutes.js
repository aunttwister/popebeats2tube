import React from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Navbar from '../components/core/Navbar';
import PrivateRoute from '../PrivateRoute';
import InstantUpload from '../components/upload/InstantUpload';
import ScheduledUpload from '../components/upload/ScheduledUpload';
import UploadManagement from '../components/UploadManagement/UploadManagement';
import NotFoundPage from '../components/common/NotFoundPage';
import './AppRoutes.css';

import { useAuth } from '../context/AuthContext';

const AppRoutes = ({ selectedTab, setSelectedTab }) => {
    const navigate = useNavigate();
    const { isAuthenticated, logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate('/');
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
            <Route path="*" element={<NotFoundPage />} />
        </Routes>
    );
};

export default AppRoutes;
