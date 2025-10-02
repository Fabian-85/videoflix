from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):

    """
    Authenticate via JWT with a cookie fallback.
    
    Try Authorization header first. If absent, fall back to the access_token cookie.
    """
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        raw = request.COOKIES.get("access_token")
        if not raw:
            return None
        validated = self.get_validated_token(raw)
        return (self.get_user(validated), validated)
