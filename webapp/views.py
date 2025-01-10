from webapp.models import DonationLocation, SubDistrict, District, Province, Region, Post, announcements, DonationHistory
from rest_framework import permissions, viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from webapp.serializers import DonationLocationSerializer, SubDistrictSerializer, DistrictSerializer, ProvinceSerializer, RegionSerializer, PostSerializer, announcements_serializer, DonationHistorySerializer

from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication

import logging

logger = logging.getLogger(__name__)

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'paginator'  # Users can set ?paginator=2 to get 2 results per page
    max_page_size = 100  # Optionally limit the maximum number of results per page

class announcement_viewset(viewsets.ModelViewSet):
    queryset = announcements.objects.all()
    serializer_class = announcements_serializer

    authentication_classes = [TokenAuthentication]  # Use token authentication
    # permission_classes = [permissions.IsAuthenticated]

class DonationLocationViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    queryset = DonationLocation.objects.all()
    serializer_class = DonationLocationSerializer
    pagination_class = CustomPagination  # Set the custom pagination

    # Optionally, you can override get_queryset() if you need more custom logic
    def get_queryset(self):
        queryset = super().get_queryset()
        facility_type = self.request.query_params.get('facility_type', None)
        if facility_type:
            queryset = queryset.filter(facility_type=facility_type)
        return queryset

class SubDistrictViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    queryset = SubDistrict.objects.all()
    serializer_class = SubDistrictSerializer

class DistrictViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    queryset = District.objects.all()
    serializer_class = DistrictSerializer

class ProvinceViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer

class RegionViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view
    
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class PostViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPagination  # Set the custom pagination

# class PostCreateView(generics.CreateAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer

#     def perform_create(self, serializer):
#         serializer.save()  # This will call the create method in the serializer

class DonationHistoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Use token authentication
    # permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated
    permission_classes = [permissions.AllowAny] 

    queryset = DonationHistory.objects.all()
    serializer_class = DonationHistorySerializer
    pagination_class = CustomPagination  # Set the custom pagination

    # def get_queryset(self):
    #     # Return only donation histories for the authenticated user
    #     return DonationHistory.objects.filter(user=self.request.user)

    # def perform_create(self, serializer):
    #     # Assign the logged-in user to the donation history record
    #     serializer.save(user=self.request.user)

    # def post(self, request, *args, **kwargs):
    #     user = request.user  # Get the logged-in user
    #     data = request.data.copy()
    #     data['user'] = user.id  # Add the user ID to the data

    #     serializer = DonationHistorySerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({
    #             'message': 'Donation history created successfully',
    #             'donation_history': serializer.data
    #         }, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
