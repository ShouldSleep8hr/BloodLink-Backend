from webapp.models import DonationLocation, SubDistrict, District, Province, Region
from rest_framework import permissions, viewsets

from webapp.serializers import DonationLocationSerializer, SubDistrictSerializer, DistrictSerializer, ProvinceSerializer, RegionSerializer

class DonationLocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = DonationLocation.objects.all()
    serializer_class = DonationLocationSerializer
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
