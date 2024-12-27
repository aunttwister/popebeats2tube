import React from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";

const GOOGLE_CLIENT_ID = "243581675304-aa4fm5o67j8m9mbq6pjq5fpu2f90n3d6.apps.googleusercontent.com"; // Replace with your Client ID

const Login = ({ onLoginSuccess }) => {
    const handleSuccess = (credentialResponse) => {
        const token = credentialResponse.credential;
        // Send token to the backend for authentication
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
                onLoginSuccess(data.jwt); // Pass the JWT back to the parent component
            })
            .catch((error) => {
                console.error(error.message);
            });
    };

    const handleError = () => {
        console.error("Google Login Failed");
    };

    return (
        <GoogleLogin
            onSuccess={handleSuccess}
            onError={handleError}
        />
    );
};

export default GoogleLogin;