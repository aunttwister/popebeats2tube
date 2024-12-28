import React, { useState } from 'react';
import Navbar from './components/Navbar';
import InstantUpload from './components/InstantUpload';
import ScheduledUpload from './components/ScheduledUpload';
import UploadManagement from './components/UploadManagement';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PrivateRoute from './PrivateRoute';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import './App.css';
import ClipLoader from "react-spinners/ClipLoader";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

function App() {
    const [selectedTab, setSelectedTab] = useState(0);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [jwt, setJwt] = useState(null);
    const [isLoading, setIsLoading] = useState(false); // Loading state
    
    // Toast utility for reusability
    const showToast = (type, title, message) => {
      if (type === 'success') {
          toast.success(message);
      } else if (type === 'error') {
          toast.error(
              <div style={{ textAlign: 'left' }}>
                  <h4 className="toast-title">{title}</h4>
                  <p className="toast-message">{message}</p>
              </div>
          );
      }
  };

    const handleLoginSuccess = (credentialResponse) => {
        const token = credentialResponse.credential;
        setIsLoading(true); // Start loading feedback

        fetch('http://localhost:8000/auth/google', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
        })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                    return response.json().then((errorResponse) => {
                        throw new Error(JSON.stringify(errorResponse));
                    });
                }
            })
            .then((data) => {
                setJwt(data.jwt);
                setIsAuthenticated(true);
            })
            .catch((error) => {
                const errorResponse = JSON.parse(error.message);
                const title = errorResponse.title || 'Error';
                const message = errorResponse.message || 'An unknown error occurred.';
                showToast('error', title, message);
                setIsAuthenticated(false);
            })
            .finally(() => setIsLoading(false)); // Stop loading feedback
    };

    const AuthenticatedRoutes = () => (
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

    const LoginPage = () => (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <div className="google-login-container">
                <h1>Please log in to access the app</h1>
                {isLoading ? (
                    <div className="loader-wrapper">
                        <ClipLoader color="#6a1b9a" loading={isLoading} size={50} />
                        <p>Authenticating...</p>
                    </div>
                ) : (
                    <GoogleLogin
                        onSuccess={handleLoginSuccess}
                        text="signin_with"
                        shape="pill"
                        theme="outline"
                        size="large"
                    />
                )}
            </div>
        </GoogleOAuthProvider>
    );

    return (
        <>
            <ToastContainer
                position="top-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop
                closeOnClick
                pauseOnHover
                draggable
                theme="colored"
            />
            <Router>{isAuthenticated ? <AuthenticatedRoutes /> : <LoginPage />}</Router>
        </>
    );
}

export default App;
