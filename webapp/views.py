from webapp.models import DonationLocation, SubDistrict, District, Province, Region, Post, Announcement, DonationHistory, Achievement, UserAchievement, Event, EventParticipant, PreferredArea
from rest_framework import permissions, viewsets, generics, views
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from webapp.serializers import DonationLocationSerializer, SubDistrictSerializer, DistrictSerializer, ProvinceSerializer, RegionSerializer, PostSerializer, AnnouncementSerializer, DonationHistorySerializer, AchievementSerializer, UserAchievementSerializer, EventSerializer, EventParticipantSerializer, PreferredAreaSerializer

from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'paginator'  # Users can set ?paginator=2 to get 2 results per page
    max_page_size = 100  # Optionally limit the maximum number of results per page

class PreferredAreaViewset(viewsets.ModelViewSet):
    queryset = PreferredArea.objects.all()
    serializer_class = PreferredAreaSerializer

    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]

class AchievementViewset(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    permission_classes = [permissions.AllowAny]

# class UserAchievementViewset(viewsets.ModelViewSet):
#     queryset = UserAchievement.objects.all()
#     serializer_class = UserAchievementSerializer

#     permission_classes = [permissions.AllowAny]

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         user_id = self.request.query_params.get('user')
#         achievement_id = self.request.query_params.get('achievement')
#         if user_id:
#             queryset = queryset.filter(user_id=user_id)
#         if achievement_id:
#             queryset = queryset.filter(achievement_id=achievement_id)
#         return queryset
    
class UserAchievementViewset(viewsets.ReadOnlyModelViewSet):
    """Handles user achievement retrieval."""
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        """Returns only the logged-in user's achievements."""
        return UserAchievement.objects.filter(user=self.request.user)

class EventViewset(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]

class EventParticipantViewset(viewsets.ModelViewSet):
    queryset = EventParticipant.objects.all()
    serializer_class = EventParticipantSerializer

    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user')
        event_id = self.request.query_params.get('event')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset
    
class UserEventParticipantViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventParticipantSerializer

    def get_queryset(self):
        return EventParticipant.objects.filter(user=self.request.user)

class AnnouncementViewset(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]

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
    
    def get_queryset(self):
        now = timezone.now()

        # Automatically update `show=False` for expired posts
        Post.objects.filter(due_date__lt=now, show=True).update(show=False)

        # Get posts that are still `show=True`
        queryset = Post.objects.filter(show=True).order_by('-created_on')

        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter posts by the authenticated user if logged in
        # user = self.request.user
        # if user.is_authenticated:
        #     queryset = queryset.filter(user=user)

        # Apply the `limit` parameter if present
        limit = self.request.query_params.get('limit', None)
        if limit is not None:
            return queryset[:int(limit)]

        return queryset

# class PostCreateView(generics.CreateAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer

#     def perform_create(self, serializer):
#         serializer.save()  # This will call the create method in the serializer

class DonationHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser] 
    queryset = DonationHistory.objects.all()
    serializer_class = DonationHistorySerializer
    pagination_class = CustomPagination  # Set the custom pagination

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
    
class UserDonationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonationHistorySerializer

    def get_queryset(self):
        return DonationHistory.objects.filter(user=self.request.user)

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
