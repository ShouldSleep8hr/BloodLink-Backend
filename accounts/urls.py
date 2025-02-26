from django.urls import path
# from auth.views import RegisterView, ChangePasswordView, UpdateProfileView
from accounts.views import RefreshTokenView, LogoutView, LogoutAllView #, UserRegistrationView, CustomLoginView
from accounts.views import LineLoginView, LineLoginCallbackView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('login/', LineLoginView.as_view(), name='line_login'),
    path('callback/', LineLoginCallbackView.as_view(), name='line_callback'),
    # path('jwt/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    # path('login/<str:linkToken>/', CustomLoginView.as_view(), name='link_token_login'),
    # path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('register/', UserRegistrationView.as_view(), name='auth_register'),
    # path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    # path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name='auth_update_profile'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    # path('logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
]