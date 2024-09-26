from webapp.models import DonationLocation, SubDistrict, District, Province, Region, Post
from rest_framework import permissions, viewsets

from webapp.serializers import DonationLocationSerializer, SubDistrictSerializer, DistrictSerializer, ProvinceSerializer, RegionSerializer, PostSerializer

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'paginator'  # Users can set ?paginator=2 to get 2 results per page
    max_page_size = 100  # Optionally limit the maximum number of results per page

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
