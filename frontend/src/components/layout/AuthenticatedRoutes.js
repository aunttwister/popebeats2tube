import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from '../core/Navbar';
import PrivateRoute from '../../PrivateRoute';
import InstantUpload from '../core/InstantUpload';
import ScheduledUpload from '../core/ScheduledUpload';
import UploadManagement from '../core/UploadManagement';

const AuthenticatedRoutes = ({ isAuthenticated, selectedTab, setSelectedTab }) => (
    <Routes>
        <Route
            path="/"
            element={
                <PrivateRoute isAuthenticated={isAuthenticated}>
                    <div>
                        <Navbar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
                        {selectedTab === 0 && <InstantUpload />}
                        {selectedTab === 1 && <ScheduledUpload />}
                        {selectedTab === 2 && <UploadManagement />}
                    </div>
                </PrivateRoute>
            }
        />
    </Routes>
);

export default AuthenticatedRoutes;
