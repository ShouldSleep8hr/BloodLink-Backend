"""
URL configuration for bloodlink project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from accounts.views import UserViewSet, UserProfileViewSet, UserRankingView
from webapp.views import DonationLocationViewSet, SubDistrictViewSet, DistrictViewSet, ProvinceViewSet, RegionViewSet, PostViewSet, UserPostViewSet, AnnouncementViewset, DonationHistoryViewSet, UserDonationHistoryViewSet, AchievementViewset, UserAchievementViewset, EventViewset, EventParticipantViewset, UserEventParticipantViewset, PreferredAreaViewset
from webapp.views import VerifyDonationHistoryViewSet

from linemessagingapi.views import Webhook

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)
router.register(r'user', UserProfileViewSet, basename='user-profile')

router.register(r'webapp/announcement',AnnouncementViewset)

router.register(r'webapp/donation-history',DonationHistoryViewSet, basename='share-donation-history')
router.register(r'user/donation-history',UserDonationHistoryViewSet, basename='user-donation-history')
router.register(r'webapp/verify-donation-history',VerifyDonationHistoryViewSet, basename='verify-donation-history')

router.register(r'webapp/donation-location', DonationLocationViewSet)
router.register(r'webapp/subdistrict', SubDistrictViewSet)
router.register(r'webapp/district', DistrictViewSet)
router.register(r'webapp/province', ProvinceViewSet)
router.register(r'webapp/region', RegionViewSet)

router.register(r'webapp/post', PostViewSet)
router.register(r'user/post',UserPostViewSet, basename='user-post')

router.register(r'webapp/achievement', AchievementViewset)
router.register(r'user/achievement', UserAchievementViewset, basename="user-achievement")


router.register(r'webapp/event', EventViewset)
router.register(r'webapp/event-participant', EventParticipantViewset)
router.register(r'user/event-participant', UserEventParticipantViewset, basename='user-event-participant')

router.register(r'webapp/preferred-area', PreferredAreaViewset)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),

    path('auth/', include('accounts.urls')),

    # path('', include('djoser.urls')), # Djoser handles login/logout
    # path('', include('djoser.urls.authtoken')), # Token-based auth
    # path('', include('djoser.urls.jwt')), # Token-based auth
    # path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Obtain JWT
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh JWT

    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('register/', UserRegistrationView.as_view(), name='register'),
    path('line/', Webhook.as_view(), name='line_webhook'),
    # path('line/<str:token>/', Webhook.as_view(), name='line_token'),
    path('ranking/', UserRankingView.as_view(), name='user-ranking'),
]