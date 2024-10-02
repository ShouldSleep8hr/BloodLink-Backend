from webapp.models import DonationLocation, SubDistrict, District, Province, Region, Post, announcements
from rest_framework import permissions, viewsets

from webapp.serializers import DonationLocationSerializer, SubDistrictSerializer, DistrictSerializer, ProvinceSerializer, RegionSerializer, PostSerializer, announcements_serializer

from rest_framework.pagination import PageNumberPagination

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import render
from .fb_scraper import scrape_blood_donation_posts

def scrape_blood_donation_posts_view(request):
    scrape_blood_donation_posts()  # เรียกฟังก์ชัน scraping
    return JsonResponse({"message": "Scraping completed, check terminal for results"}, status=200)

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'paginator'  # Users can set ?paginator=2 to get 2 results per page
    max_page_size = 100  # Optionally limit the maximum number of results per page

class announcement_viewset(viewsets.ModelViewSet):
    queryset = announcements.objects.all()
    serializer_class = announcements_serializer

class DonationLocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = DonationLocation.objects.all()
    serializer_class = DonationLocationSerializer
    pagination_class = CustomPagination  # Set the custom pagination
    # permission_classes = [permissions.IsAuthenticated]

class SubDistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = SubDistrict.objects.all()
    serializer_class = SubDistrictSerializer
    # permission_classes = [permissions.IsAuthenticated]

class DistrictViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    # permission_classes = [permissions.IsAuthenticated]

class ProvinceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    # permission_classes = [permissions.IsAuthenticated]

class RegionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    # permission_classes = [permissions.IsAuthenticated]

class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticated]
