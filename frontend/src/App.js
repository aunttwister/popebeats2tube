import React, { useState } from 'react';
import Navbar from './components/Navbar';
import InstantUpload from './components/InstantUpload';
import ScheduledUpload from './components/ScheduledUpload';
import UploadManagement from './components/UploadManagement';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PrivateRoute from "./PrivateRoute";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

const GOOGLE_CLIENT_ID = "299795794182-g4po9fe003o5ducp1jkn588tdcsdbmaa.apps.googleusercontent.com"; // Replace with your Client ID

function App() {
  const [selectedTab, setSelectedTab] = useState(0);

  const [isAuthenticated, setIsAuthenticated] = useState(false); // Tracks authentication status
    const [jwt, setJwt] = useState(null); // Stores JWT after login

    const handleLoginSuccess = (credentialResponse) => {
        const token = credentialResponse.credential;

        console.log(token)
        // Send token to the backend for verification
        fetch("http://localhost:8000/auth/google", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
        })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Authentication failed");
                }
            })
            .then((data) => {
                setJwt(data.jwt); // Store JWT
                setIsAuthenticated(true); // Set authentication status to true
            })
            .catch((error) => {
                console.error("Authentication failed:", error.message);
                setIsAuthenticated(false); // Ensure unauthenticated status
            });
    };

  const handleLoginError = () => {
    console.error("Google Login Failed");
    setIsAuthenticated(false); // Ensure unauthenticated status
  };

  if (!isAuthenticated) {
    // Render login only when not authenticated
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <div>
                <h1>Please log in to access the app</h1>
                <GoogleLogin
                    onSuccess={handleLoginSuccess}
                    onError={handleLoginError}
                />
            </div>
        </GoogleOAuthProvider>
    );
}
return (
    <Router>
        <Routes>
            <Route
                path="/login"
                element={<GoogleLogin onLoginSuccess={() => setIsAuthenticated(true)} />}
            />
            <Route
                path=""
                element={
                    <PrivateRoute isAuthenticated={isAuthenticated}>
                        <div>
                          <ToastContainer
                            position="top-right"  // Default position
                            autoClose={3000}      // Default auto-close duration (in milliseconds)
                            hideProgressBar={false} // Show progress bar
                            newestOnTop={true}    // Newest toast appears on top
                            closeOnClick={true}   // Dismiss toast on click
                            pauseOnHover={true}   // Pause auto-close on hover
                            draggable={true}      // Allow dragging the toast
                            theme="colored"       // Theme: 'light', 'dark', or 'colored'
                          />
                          <Navbar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
                          {selectedTab === 0 && <InstantUpload />}
                          {selectedTab === 1 && <ScheduledUpload />}
                          {selectedTab === 2 && <UploadManagement />}
                        </div>
                    </PrivateRoute>
                }
            />
        </Routes>
    </Router>
  );
};

export default App;
