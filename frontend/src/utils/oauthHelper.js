export const handleGoogleLoginResponse = async (token) => {
    const data = await googleOAuthService.login(token);
  
    if (data.redirect && data.oauth_url) {
      redirectToOAuth(data.oauth_url);
      return { redirected: true };
    }
  
    if (data.jwt && data.user_id && data.user_email) {
      setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
      return {
        authenticated: true,
        user: { id: data.user_id, email: data.user_email }
      };
    }
  
    throw new Error("Unexpected backend response");
  };
  
  export const handleGoogleCallbackFlow = async ({ code, user_id, user_email }) => {
    const data = await googleOAuthService.callback({ code, user_id, user_email });
  
    if (!data.jwt) throw new Error("Authentication failed: No JWT.");
  
    setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
  
    return {
      authenticated: true,
      user: { id: data.user_id, email: data.user_email }
    };
  };
  
  export const handleGoogleRefreshFlow = async () => {
    const data = await googleOAuthService.refreshToken();
  
    if (!data.jwt) throw new Error("Failed to refresh token: No JWT in response.");
  
    setLocalStorage(data.jwt, data.expires_in, data.user_id, data.user_email);
  
    return {
      authenticated: true,
      user: { id: data.user_id, email: data.user_email }
    };
  };
  