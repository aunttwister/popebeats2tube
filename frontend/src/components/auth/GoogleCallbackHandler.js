import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toastHelper } from '../../utils/toastHelper';
import { setToken } from '../../utils/tokenManager';

const GoogleCallbackHandler = ({ setIsAuthenticated }) => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {
        const authCode = searchParams.get('code');
        const user_id = searchParams.get('state');
        const error = searchParams.get('error');

        if (error) {
            toastHelper.newMessage('error', 'Login Failed', 'Google OAuth failed. Please try again.');
            navigate('/');
            return;
        }

        if (authCode) {
            fetch('http://localhost:8000/auth/google/callback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: authCode, user_id }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.jwt) {
                        setToken(data.jwt, data.expires_in)
                        localStorage.setItem('userEmail', data.user_email);
                        setIsAuthenticated(true);
                        navigate('/');
                        toastHelper.newMessage('success', 'Login Successful', 'You are now authenticated.');
                    } else {
                        throw new Error('Authentication failed.');
                    }
                })
                .catch(() => {
                    toastHelper.newMessage('error', 'Login Failed', 'Could not authenticate user. Please try again.');
                    navigate('/');
                });
        } else {
            toastHelper.newMessage('error', 'Login Failed', 'No authorization code found.');
            navigate('/');
        }
    }, [searchParams, navigate, setIsAuthenticated]);

    return (
        <div style={{ textAlign: 'center', marginTop: '20%' }}>
            <h2>Processing Google Authentication...</h2>
        </div>
    );
};

export default GoogleCallbackHandler;
