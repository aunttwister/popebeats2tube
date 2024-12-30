import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-toastify';

const GoogleCallbackHandler = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {
        const authCode = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
            toast.error('Google OAuth failed. Please try again.');
            console.error('Error during Google OAuth:', error);
            navigate('/'); // Redirect to login page or show an error message
            return;
        }

        if (authCode) {
            // Send the authorization code to the backend
            fetch('http://localhost:8000/auth/google/callback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: authCode }),
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
                        navigate('/'); // Redirect to login page
                    } else {
                        console.log('OAuth successful:', data);
                        toast.success('Authentication successful!');
                        navigate('/'); // Redirect to the main app or dashboard
                    }
                })
                .catch((err) => {
                    console.error('Error during backend communication:', err);
                    toast.error('An error occurred during authentication. Please try again.');
                    navigate('/'); // Redirect to login page
                });
        } else {
            toast.error('No authorization code found.');
            navigate('/'); // Redirect to login page
        }
    }, [searchParams, navigate]);

    return (
        <div style={{ textAlign: 'center', marginTop: '20%' }}>
            <h2>Processing Google Authentication...</h2>
        </div>
    );
};

export default GoogleCallbackHandler;
