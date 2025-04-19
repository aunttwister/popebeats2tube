import React from 'react';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import ClipLoader from 'react-spinners/ClipLoader';

const LoginPage = ({ isLoading, handleLoginSuccess, GOOGLE_CLIENT_ID }) => (
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

export default LoginPage;