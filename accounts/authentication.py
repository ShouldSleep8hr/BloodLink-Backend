from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")  # Read from cookie

        if not access_token:
            print("No access token found in cookies")
            return None  # No token found

        try:
            validated_token = AccessToken(access_token)  # Validate token
            print(access_token)
            print(validated_token)
            print(self.get_user(validated_token))
        except Exception as e:
            print("Token validation failed:", str(e))
            raise AuthenticationFailed("Invalid token")  # Reject invalid tokens

        return self.get_user(validated_token), validated_token
