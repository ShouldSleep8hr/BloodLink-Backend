from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")  # Read from cookie

        if not access_token:
            return None  # No token found

        try:
            validated_token = AccessToken(access_token)  # Validate token
        except Exception:
            raise AuthenticationFailed("Invalid token")  # Reject invalid tokens
        
        print(access_token)
        print(validated_token)
        print(self.get_user(validated_token))

        return self.get_user(validated_token), validated_token
