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
    
class SubDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny] 

    queryset = SubDistrict.objects.all() 
    serializer_class = SubDistrictSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        district = self.request.query_params.get('district', None)
        if district:
            queryset = queryset.filter(district=district)
        return queryset

class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        province = self.request.query_params.get('province', None)
        if province:
            queryset = queryset.filter(province=province)
        return queryset

class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]

    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    pagination_class = CustomPagination

class RegionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view
    
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    queryset = Post.objects.filter(show=True).order_by('-created_on')
    serializer_class = PostSerializer
    pagination_class = CustomPagination  # Set the custom pagination
    
    def get_queryset(self):
        now = timezone.now()
        
        # Use `update()` only if there are posts to update (avoids unnecessary DB queries)
        expired_posts = Post.objects.filter(due_date__lt=now, show=True)
        if expired_posts.exists():
            expired_posts.update(show=False)

        # Filter posts that are still `show=True`
        queryset = super().get_queryset()  # Uses the `queryset` defined above

        # Apply the `limit` parameter if present
        limit = self.request.query_params.get('limit')
        if limit and limit.isdigit():
            return queryset[:int(limit)]

        return queryset
    
class UserPostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        """Return only posts created by the logged-in user."""
        return Post.objects.filter(user=self.request.user).order_by('-created_on')

    def perform_create(self, serializer):
        """Set the user automatically when creating a post."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure only the post owner can update their post."""
        post = self.get_object()
        if post.user != self.request.user:
            return Response({"error": "You do not have permission to edit this post."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure only the post owner can delete their post."""
        if instance.user != self.request.user:
            return Response({"error": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()

    @action(detail=True, methods=["post"])
    def interest(self, request, pk=None):
        """Allow users to press interest a post."""
        post = self.get_object()
        post.number_interest += 1
        post.save()
        return Response({"message": "Post interest successfully!"}, status=200)

class DonationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny] 
    serializer_class = DonationHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return DonationHistory.objects.filter(verify=True, share_status=True).order_by('-created_on')
    
class UserDonationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for users to view and create their donation history."""
    serializer_class = DonationHistorySerializer

    def get_queryset(self):
        return DonationHistory.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Allow users to create a new donation history."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Assign the user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
