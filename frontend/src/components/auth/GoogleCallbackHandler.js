import React, { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toastHelper } from '../../utils/toastHelper';
import { setLocalStorage } from '../../utils/tokenManager';
import { googleOAuthService } from '../../services/googleOAuthService.ts';
import { useAuth } from '../../context/AuthContext';

const GoogleCallbackHandler = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const hasRunRef = useRef(false);
  const { setIsAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading || hasRunRef.current) return;

    const authCode = searchParams.get('code');
    const user_id = searchParams.get('state');
    const user_email = searchParams.get('login_hint')
    const error = searchParams.get('error');

    if (!authCode || !user_id || error) {
      toastHelper.newMessage('error', 'Login Failed', error ? 'Google OAuth failed. Please try again.' : 'Missing OAuth parameters.');
      navigate('/');
      return;
    }

    hasRunRef.current = true;

    googleOAuthService
      .callback({ code: authCode, user_id, user_email})
      .then((data) => {
        if (data.jwt) {
          setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
          setIsAuthenticated(true); // ✅ safe now
          toastHelper.newMessage('success', 'Login Successful', 'You are now authenticated.');
          navigate('/');
        } else {
          throw new Error('Authentication failed: No JWT.');
        }
      })
      .catch((err) => {
        console.error('Google OAuth callback error:', err);
        toastHelper.newMessage('error', 'Login Failed', 'Could not authenticate user. Please try again.');
        navigate('/');
      });
  }, [searchParams, navigate, setIsAuthenticated, isLoading]);

  return (
    <div style={{ textAlign: 'center', marginTop: '20%' }}>
      <h2>Processing Google Authentication...</h2>
    </div>
  );
};

export default GoogleCallbackHandler;
