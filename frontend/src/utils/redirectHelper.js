export const redirectToOAuth = (oauthUrl) => {
    if (!oauthUrl) return;
    window.open(oauthUrl, '_self');
  };