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
# from django.contrib import admin
# from django.urls import path

# from accounts import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('/', admin.site.urls),
# ]

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from accounts.views import UserViewSet
from webapp.views import DonationLocationViewSet, SubDistrictViewSet, DistrictViewSet, ProvinceViewSet, RegionViewSet, announcement_viewset

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'webapp/announcement',announcement_viewset)
router.register(r'webapp/donation-location', DonationLocationViewSet)
router.register(r'webapp/subdistrict', SubDistrictViewSet)
router.register(r'webapp/district', DistrictViewSet)
router.register(r'webapp/province', ProvinceViewSet)
router.register(r'webapp/region', RegionViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]