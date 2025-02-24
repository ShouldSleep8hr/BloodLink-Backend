from django.http import HttpResponseRedirect
import requests
from django.core.cache import cache

from accounts.models import Users
from rest_framework import permissions, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.decorators import action

from accounts.serializers import UserSerializer, UserRankingSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from jwt import decode, ExpiredSignatureError, InvalidTokenError

from django.shortcuts import redirect
import secrets
from linemessagingapi.models import NonceMapping
import os

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserRankingView(APIView):
    """Return top 5 users based on score"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        top_users = Users.objects.order_by('-score')[:5]  # Get top 5 users sorted by score
        serializer = UserRankingSerializer(top_users, many=True)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.ViewSet):
    """Handles user profile viewing and updating."""
    # permission_classes = [permissions.IsAuthenticated]  # Ensure user is logged in

    @action(detail=False, methods=["get", "patch"])
    def profile(self, request):
        """Handles GET (view profile) and PATCH (update profile)"""
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        elif request.method == "PATCH":
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
    
    # @action(detail=False, methods=['get'])
    # @action(detail=False) # detail=False so dont need id in parameter
    # def profile(self, request): # /user/profile
    #     """Returns the logged-in user's profile information"""
    #     serializer = UserSerializer(request.user)  # Serialize the logged-in user
    #     return Response(serializer.data)

class LineLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        state = secrets.token_urlsafe(16)
        nonce = secrets.token_urlsafe(16)

        request.session['line_login_state'] = state  # Store state in session
        
        # Save nonce in the database linked to a session or user
        NonceMapping.objects.create(nonce=nonce)

        line_login_url = (
            f"https://access.line.me/oauth2/v2.1/authorize"
            f"?response_type=code"
            f"&client_id={os.getenv('CLIENT_ID')}"  # LINE Channel ID
            f"&redirect_uri=https://bloodlink.up.railway.app/auth/callback/"  # Callback URL
            f"&state={state}"  # CSRF prevention
            f"&bot_prompt=aggressive" # normal, aggressive	
            f"&scope=profile%20openid%20email"  # Required scopes
            f"&nonce={nonce}"  # To prevent replay attacks
        )
        
        return redirect(line_login_url)

class LineLoginCallbackView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        if not code or not state:
            return Response({'error': 'Authorization code or state is missing'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate state to prevent CSRF attacks
        saved_state = request.session.pop('line_login_state', None)  # Retrieve and remove state from session
        if saved_state != state:
            return Response({'error': 'Invalid state parameter'}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange the authorization code for an access token
        token_url = "https://api.line.me/oauth2/v2.1/token"
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://bloodlink.up.railway.app/auth/callback/",
            "client_id": os.getenv('CLIENT_ID'),
            "client_secret": os.getenv('CLIENT_SECRET'),
        }
        if not data["client_id"] or not data["client_secret"]:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in the environment.")
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            token_response = requests.post(token_url, data=data, headers=headers)
            token_response.raise_for_status()
            token_data = token_response.json()
        except requests.RequestException as e:
            return Response({'error': 'Failed to exchange code for token', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Decode the ID token to get LINE user info
        id_token = token_data.get('id_token')
        access_token = token_data.get('access_token')

        if not id_token or not access_token:
            return Response({'error': 'Missing tokens in response'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = decode(id_token, options={"verify_signature": False})  # Add verification in production
            nonce = decoded_token.get("nonce")
            line_user_id = decoded_token.get('sub')
            email = decoded_token.get("email")

            if not NonceMapping.objects.filter(nonce=nonce).exists():
                return Response({"error": "Invalid nonce"}, status=status.HTTP_400_BAD_REQUEST)
            
            # If valid, delete it to prevent reuse
            NonceMapping.objects.filter(nonce=nonce).delete()

        except (ExpiredSignatureError) as e:
            return Response({'error': 'Expired ID token'}, status=status.HTTP_400_BAD_REQUEST)
        except (InvalidTokenError) as e:
            return Response({'error': 'Invalid ID token'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not line_user_id:
            return Response({'error': 'LINE user ID not found in token'}, status=status.HTTP_400_BAD_REQUEST)

        profile_url = "https://api.line.me/v2/profile"
        profile_headers = {"Authorization": f"Bearer {access_token}"}

        try:
            profile_response = requests.get(profile_url, headers=profile_headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()

            picture_url = profile_data.get("pictureUrl")
            display_name = profile_data.get("displayName")
        except requests.RequestException as e:
            display_name = None
            picture_url = None

        try:
            # uploaded_url = self.upload_profile_picture_to_gcs(picture_url)
            # Check if user exists, update profile picture if needed
            user, created = Users.objects.update_or_create(
                email=email,
                defaults={
                    'line_user_id' : line_user_id,
                    'line_username': display_name,
                    'profile_picture': picture_url,  # Refresh profile picture every login
                }
            )

            # Generate JWT tokens
            # refresh = RefreshToken.for_user(user)
            # tokens = { 'refresh': str(refresh), 'access': str(refresh.access_token), }

            # return Response({
            #     'message': 'User logged in' if not created else 'User registered successfully',
            #     'user_id': user.id,
            #     'user_email': user.email,
            #     'line_username': user.line_username,
            #     'profile_picture': user.profile_picture,
            #     'tokens': tokens,
            # }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Redirect response with HttpOnly cookies
            response = HttpResponseRedirect('https://hare-trusty-boa.ngrok-free.app/callback')
            # response.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="Strict", max_age=3600)
            # response.set_cookie("refresh_token", str(refresh), httponly=True, secure=False, samesite="Strict", max_age=86400)
            response.set_cookie("access_token", access_token, httponly=True, secure=True, samesite="None")
            response.set_cookie("refresh_token", str(refresh), httponly=True, secure=True, samesite="None")
            return response
        except Exception as e:
            return Response({'error': 'Failed to update or create user', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def upload_profile_picture_to_gcs(self, temp_url):
    #     """Download image from temp_url and upload it to GCS using Django's storage."""
    #     response = requests.get(temp_url)
        
    #     if response.status_code == 200:
    #         file_extension = temp_url.split('.')[-1].split('?')[0]  # Extract file extension
    #         unique_filename = f"profile_pictures/{uuid.uuid4().hex}.{file_extension}"

    #         # Save file using Django's storage system
    #         file_obj = ContentFile(response.content)
    #         file_path = default_storage.save(unique_filename, file_obj)

    #         return default_storage.url(file_path)  # Return public URL of uploaded image
        
    #     return None

# class CustomLoginView(TokenObtainPairView):
#     permission_classes = [permissions.AllowAny]  # Allow anyone to access this view
#     # authentication_classes = [TokenAuthentication]  # Use token authentication

#     def post(self, request, *args, **kwargs):
#         # print(request.build_absolute_uri())
#         # Call the parent post method to get the token
#         response = super().post(request, *args, **kwargs)

#         if response.status_code == 200:
#             try:
#                 # Get the user based on the email from the request data
#                 user = Users.objects.get(email=request.data.get('email'))
#             except ObjectDoesNotExist:
#                 return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
#             except MultipleObjectsReturned:
#                 return Response({'error': 'Multiple users found with this email'}, status=status.HTTP_400_BAD_REQUEST)

#             # Generate a secure state and nonce
#             state = secrets.token_urlsafe(16)
#             nonce = secrets.token_urlsafe(16)

#             # Store the state and nonce mapping in the database (Optional)
#             NonceMapping.objects.create(user=user, nonce=nonce)

#             # LINE Login URL construction
#             line_login_url = (
#                 f"https://access.line.me/oauth2/v2.1/authorize"
#                 f"?response_type=code"
#                 f"&client_id=2006630011"  # LINE Channel ID
#                 f"&redirect_uri=https://bloodlink.up.railway.app/line"  # Callback URL
#                 f"&state={state}"  # CSRF prevention
#                 f"&bot_prompt=aggressive" # normal, aggressive	
#                 f"&scope=profile%20openid%20email"  # Required scopes
#                 f"&nonce={nonce}"  # To prevent replay attacks
#             )

#             # Return the LINE Login URL to the frontend
#             return Response({
#                 'message': 'Redirect to this URL to log in with LINE.',
#                 'line_login_url': line_login_url
#             }, status=status.HTTP_200_OK)            

#         # If no link token, return the usual login response with JWT token
#         return response

# class UserRegistrationView(APIView):
#     permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

#     # def post(self, request, *args, **kwargs):
#     #     serializer = UserSerializer(data=request.data)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def post(self, request, *args, **kwargs):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()  # Save the user

#             # Prepare the link token from the request (if provided)
#             link_token = request.query_params.get('linkToken')
#             if link_token:
#                 if link_token.endswith('/'):
#                     link_token = link_token.rstrip('/')
#                 nonce = secrets.token_urlsafe(16)
#                 NonceMapping.objects.create(user=user, nonce=nonce)
#                 # Redirect to the LINE account linking URL
#                 linking_url = (
#                     f"https://access.line.me/dialog/bot/accountLink?linkToken={link_token}&nonce={nonce}"
#                 )
#                 # Return the linking URL to the frontend
#                 return Response({
#                     'message': 'Redirect to this URL to link your LINE account.',
#                     'linking_url': linking_url
#                 }, status=status.HTTP_200_OK)

#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class LogoutView(APIView):
#     # permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         try:
#             refresh_token = request.data["refresh_token"]
#             token = RefreshToken(refresh_token)
#             token.blacklist()

#             return Response(status=status.HTTP_205_RESET_CONTENT)
#         except Exception as e:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
        
# class LogoutAllView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     # authentication_classes = [TokenAuthentication]

#     def post(self, request):
#         tokens = OutstandingToken.objects.filter(user_id=request.user.id)
#         for token in tokens:
#             t, _ = BlacklistedToken.objects.get_or_create(token=token)

#         return Response(status=status.HTTP_205_RESET_CONTENT)

class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)

            # Check if the token is blacklisted (user logged out)
            if BlacklistedToken.objects.filter(token__jti=refresh['jti']).exists():
                return Response({"error": "Refresh token is blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
            
            access_token = str(refresh.access_token)

            response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)
            response.set_cookie("access_token", access_token, httponly=True, secure=True, samesite="None")

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class LogoutView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         try:
#             # Get refresh token from HttpOnly Cookie
#             refresh_token = request.COOKIES.get("refresh_token")

#             if not refresh_token:
#                 return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)

#             token = RefreshToken(refresh_token)
#             token.blacklist()

#             # Clear cookies
#             response = Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
#             response.delete_cookie("access_token")
#             response.delete_cookie("refresh_token")

#             return response

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(APIView):

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")  # Get refresh token from cookie

            if not refresh_token:
                return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
            # Correct way to delete cookies (expire immediately)
            response.set_cookie("access_token", "", httponly=True, secure=True, samesite="None", expires=0)
            response.set_cookie("refresh_token", "", httponly=True, secure=True, samesite="None", expires=0)

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAllView(APIView):

    def post(self, request):
        try:
            tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            response = Response({"message": "Logged out from all devices"}, status=status.HTTP_205_RESET_CONTENT)
            # Correct way to delete cookies (expire immediately)
            response.set_cookie("access_token", "", httponly=True, secure=True, samesite="None", expires=0)
            response.set_cookie("refresh_token", "", httponly=True, secure=True, samesite="None", expires=0)

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)