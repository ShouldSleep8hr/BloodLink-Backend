from django.urls import path
# from auth.views import RegisterView, ChangePasswordView, UpdateProfileView
from accounts.views import LogoutView, LogoutAllView, UserRegistrationView, CustomLoginView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    # path('login/<str:linkToken>/', CustomLoginView.as_view(), name='link_token_login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='auth_register'),
    # path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    # path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name='auth_update_profile'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
]