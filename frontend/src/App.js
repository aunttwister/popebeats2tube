import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useSearchParams } from 'react-router-dom';
import Navbar from './components/Navbar';
import InstantUpload from './components/InstantUpload';
import ScheduledUpload from './components/ScheduledUpload';
import UploadManagement from './components/UploadManagement';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PrivateRoute from './PrivateRoute';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import './App.css';
import ClipLoader from 'react-spinners/ClipLoader';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const GoogleCallbackHandler = ({ setIsAuthenticated }) => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const user_id = searchParams.get('state');

    useEffect(() => {
        const authCode = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
            toast.error('Google OAuth failed. Please try again.');
            console.error('Error during Google OAuth:', error);
            navigate('/');
            return;
        }

        if (authCode) {
            fetch('http://localhost:8000/auth/google/callback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: authCode, user_id: user_id }),
            })
                .then((response) => {
                    if (!response.ok) {
                        return response.json().then((errorResponse) => {
                            throw new Error(JSON.stringify(errorResponse));
                        });
                    }
                    return response.json();
                })
                .then((data) => {
                    if (data.error) {
                        console.error('Error from backend:', data.error);
                        toast.error('Authentication failed. Please try again.');
                        navigate('/');
                    } else {
                        console.log('OAuth successful:', data);
                        toast.success('Authentication successful!');
                        setIsAuthenticated(true); // Set authentication to true
                        navigate('/'); // Redirect to the main page
                    }
                })
                .catch((err) => {
                    console.error('Error during backend communication:', err);
                    toast.error('An error occurred during authentication. Please try again.');
                    navigate('/');
                });
        } else {
            toast.error('No authorization code found.');
            navigate('/');
        }
    }, [searchParams, navigate, setIsAuthenticated]);

    return (
        <div style={{ textAlign: 'center', marginTop: '20%' }}>
            <h2>Processing Google Authentication...</h2>
        </div>
    );
};

function App() {
    const [selectedTab, setSelectedTab] = useState(0);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [jwt, setJwt] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

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
        setIsLoading(true);
    
        fetch('http://localhost:8000/auth/google', {
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
                    // Redirect the user to Google OAuth consent screen
                    const oauthUrl = `${data.oauth_url}&state=${encodeURIComponent(data.user_id)}`;
                    window.open(oauthUrl, '_self'); // Open in the same window
                } else if (data.jwt) {
                    // Save JWT and authenticate user
                    setJwt(data.jwt);
                    setIsAuthenticated(true);
                    showToast('success', 'Login Successful', 'You are now authenticated.');
                } else {
                    throw new Error('Unexpected response from backend.');
                }
            })
            .catch((error) => {
                console.error('Error during login:', error);
                showToast('error', 'Login Failed', 'Could not authenticate user.');
            })
            .finally(() => {
                setIsLoading(false);
            });
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
            <Router>
                <Routes>
                <Route path="/auth/google/callback" element={<GoogleCallbackHandler setIsAuthenticated={setIsAuthenticated} />}/>
                    {isAuthenticated ? (
                        <Route path="/*" element={<AuthenticatedRoutes />} />
                    ) : (
                        <Route path="/*" element={<LoginPage />} />
                    )}
                </Routes>
            </Router>
        </>
    );
}

export default App;
