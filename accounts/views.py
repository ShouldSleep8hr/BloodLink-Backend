import requests
from accounts.models import Users
from rest_framework import permissions, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from accounts.serializers import UserSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from django.shortcuts import redirect
import secrets
from linemessagingapi.models import NonceMapping

# from django.http import JsonResponse
# from django.middleware.csrf import get_token

# def csrf_token_view(request):
#     token = get_token(request)
#     return JsonResponse({'csrfToken': token})

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

class CustomLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view
    # authentication_classes = [TokenAuthentication]  # Use token authentication

    def post(self, request, *args, **kwargs):
        # print(request.build_absolute_uri())
        # Call the parent post method to get the token
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            try:
                # Get the user based on the email from the request data
                user = Users.objects.get(email=request.data.get('email'))
            except ObjectDoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
            except MultipleObjectsReturned:
                return Response({'error': 'Multiple users found with this email'}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare the link token from the request (if provided)
            # link_token = request.query_params.get('linkToken')
            # if link_token:
            #     if link_token.endswith('/'):
            #         link_token = link_token.rstrip('/')

            #     nonce = secrets.token_urlsafe(16)  # Generate a secure nonce
            #     NonceMapping.objects.create(user=user, nonce=nonce)

            #     # Redirect to the LINE account linking URL
            #     linking_url = (
            #         f"https://access.line.me/dialog/bot/accountLink?linkToken={link_token}&nonce={nonce}"
            #     )
            #     # Return the linking URL to the frontend
            #     return Response({
            #         'message': 'Redirect to this URL to link your LINE account.',
            #         'linking_url': linking_url
            #     }, status=status.HTTP_200_OK)

            # Generate a secure state and nonce
            state = secrets.token_urlsafe(16)
            nonce = secrets.token_urlsafe(16)

            # Store the state and nonce mapping in the database (Optional)
            NonceMapping.objects.create(user=user, nonce=nonce)

            # LINE Login URL construction
            line_login_url = (
                f"https://access.line.me/oauth2/v2.1/authorize"
                f"?response_type=code"
                f"&client_id=2006630011"  # LINE Channel ID
                f"&redirect_uri=https://bloodlink.up.railway.app/line"  # Callback URL
                f"&state={state}"  # CSRF prevention
                f"&bot_prompt=aggressive" # normal, aggressive	
                f"&scope=profile%20openid%20email"  # Required scopes
                f"&nonce={nonce}"  # To prevent replay attacks
            )

            # Return the LINE Login URL to the frontend
            return Response({
                'message': 'Redirect to this URL to log in with LINE.',
                'line_login_url': line_login_url
            }, status=status.HTTP_200_OK)            

        # If no link token, return the usual login response with JWT token
        return response

    # def get_user_from_request(self, request):
    #     # Extract user from the request, assuming the user is authenticated
    #     return request.user  # Djoser sets the authenticated user in request.user

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    # def post(self, request, *args, **kwargs):
    #     serializer = UserSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Save the user

            # Prepare the link token from the request (if provided)
            link_token = request.query_params.get('linkToken')
            if link_token:
                if link_token.endswith('/'):
                    link_token = link_token.rstrip('/')
                nonce = secrets.token_urlsafe(16)
                NonceMapping.objects.create(user=user, nonce=nonce)
                # Redirect to the LINE account linking URL
                linking_url = (
                    f"https://access.line.me/dialog/bot/accountLink?linkToken={link_token}&nonce={nonce}"
                )
                # Return the linking URL to the frontend
                return Response({
                    'message': 'Redirect to this URL to link your LINE account.',
                    'linking_url': linking_url
                }, status=status.HTTP_200_OK)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class LogoutAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)