import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toastHelper } from '../../utils/toastHelper';
import { setLocalStorage } from '../../utils/tokenManager';
import { googleOAuthService } from '../../services/googleOAuthService.ts';

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
            googleOAuthService.callback({ code: authCode, user_id })
                .then((data) => {
                    if (data.jwt) {
                        setLocalStorage(data.jwt, data.expires_in, data.user_id)
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
