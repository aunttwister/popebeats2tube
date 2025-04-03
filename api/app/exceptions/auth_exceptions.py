class AuthException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class InvalidGoogleToken(AuthException):
    def __init__(self, detail="Invalid Google Token"):
        super().__init__(401, detail)

class MissingEmail(AuthException):
    def __init__(self):
        super().__init__(401, "Google token is missing email.")

class UnauthorizedUser(AuthException):
    def __init__(self, email: str):
        super().__init__(401, f"User with email '{email}' is not authorized.")

class RefreshTokenRevoked(AuthException):
    def __init__(self):
        super().__init__(401, "Refresh token has been revoked. Please re-authenticate.")
