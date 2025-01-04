import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from '../core/Navbar';
import PrivateRoute from '../../PrivateRoute';
import InstantUpload from '../core/InstantUpload';
import ScheduledUpload from '../ScheduledUpload/ScheduledUpload';
import UploadManagement from '../UploadManagement/UploadManagement';
import './AuthenticatedRoutes.css'; // Add CSS file for styles

const AuthenticatedRoutes = ({ isAuthenticated, selectedTab, setSelectedTab }) => (
    <Routes>
        <Route
            path="/"
            element={
                <PrivateRoute isAuthenticated={isAuthenticated}>
                    <div>
                        {/* Navbar remains full-width */}
                        <Navbar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
                        
                        {/* Containerized main content */}
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

export default AuthenticatedRoutes;
