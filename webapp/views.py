from webapp.models import DonationLocation, SubDistrict, District, Province, Region, Post, Announcement, DonationHistory, Achievement, UserAchievement, Event, EventParticipant, PreferredArea, UserPostInterest
from accounts.models import Users
from rest_framework import permissions, viewsets, generics, views, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from webapp.serializers import DonationLocationSerializer, SubDistrictSerializer, DistrictSerializer, ProvinceSerializer, RegionSerializer, PostSerializer, AnnouncementSerializer, DonationHistorySerializer, AchievementSerializer, UserAchievementSerializer, EventSerializer, EventParticipantSerializer, PreferredAreaSerializer, UserPostInterestSerializer

from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from django.dispatch import receiver, Signal
from django.db.models import Q

import logging
from django.db.models import F

logger = logging.getLogger(__name__)

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'paginator'  # Users can set ?paginator=2 to get 2 results per page
    max_page_size = 100  # Optionally limit the maximum number of results per page

class PreferredAreaViewset(viewsets.ModelViewSet):
    queryset = PreferredArea.objects.all()
    serializer_class = PreferredAreaSerializer
    permission_classes = [permissions.IsAdminUser]

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
    
class UserEventParticipantViewset(mixins.ListModelMixin,  # Allows list
                                  mixins.CreateModelMixin,  # Allows POST
                                  viewsets.GenericViewSet):  # No PUT/DELETE
    serializer_class = EventParticipantSerializer

    def get_queryset(self):
        """Filter queryset to return only the authenticated user's event participation records."""
        queryset = EventParticipant.objects.filter(user=self.request.user)
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Prevent duplicate event participation and assign user."""
        user = request.user
        event_id = request.data.get("event")

        # Prevent duplicate participation
        if EventParticipant.objects.filter(user=user, event_id=event_id).exists():
            return Response({"detail": "You have already joined this event."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)  # Explicitly assign the user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnnouncementViewset(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    pagination_class = CustomPagination
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
        Post.objects.filter(due_date__lt=now, show=True).update(show=False)
        # expired_posts = Post.objects.filter(due_date__lt=now, show=True)
        # if expired_posts.exists():
        #     expired_posts.update(show=False)

        # Filter posts that are still `show=True`
        queryset = super().get_queryset()  # Uses the `queryset` defined above

        # Apply the `limit` parameter if present
        limit = self.request.query_params.get('limit')
        if limit and limit.isdigit():
            return queryset[:int(limit)]

        return queryset

post_interested = Signal()
class UserPostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = CustomPagination
    queryset = Post.objects.filter(show=True).order_by('-created_on')

    def get_queryset(self):
        """Return only posts created by the logged-in user."""
        now = timezone.now()
        # Use `update()` only if there are posts to update (avoids unnecessary DB queries)
        Post.objects.filter(due_date__lt=now, show=True).update(show=False)

        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user automatically when creating a post."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure only the post owner can update their post."""
        post = self.get_object()
        if post.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this post.")
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure only the post owner can delete their post."""
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")
        instance.delete()

    @action(detail=True, methods=["post"])
    def interest(self, request, pk=None):
        """Allow users to press interest on a post."""
        post = self.get_object()
        user = self.request.user  # The user who is showing interest
        
        # Check if the user is trying to show interest in their own post
        if post.user == user:
            return Response({"message": "You cannot show interest in your own post."}, status=400)

        # Check if the user has already shown interest in this post
        if UserPostInterest.objects.filter(user=user, post=post).exists():
            return Response({"message": "You have already shown interest in this post."}, status=400)
        
        # Increment the number of interests on the post
        post.number_interest += 1
        post.save()

        # Create a record in UserPostInterest to track the user's interest
        UserPostInterest.objects.create(user=user, post=post)

        # Send a signal that the post was liked
        post_interested.send(sender=Post, instance=post, interested_by=user)
        return Response({"message": "Post interest successfully!"}, status=200)
    
class UserPostInterestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPostInterestSerializer

    def get_queryset(self):
        return UserPostInterest.objects.filter(user=self.request.user).order_by('-created_on')

class DonationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny] 
    serializer_class = DonationHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return DonationHistory.objects.filter(verify_status='verified', share_status=True).order_by('-created_on')
    
class VerifyDonationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = DonationHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return (
            DonationHistory.objects
            .filter(verify_status='pending')
            .exclude(
                (Q(donor_card_image__isnull=True) | Q(donor_card_image='')) &
                (Q(donation_image__isnull=True) | Q(donation_image=''))
            )
            .order_by('-created_on')
        )
        # return DonationHistory.objects.filter(verify_status='pending').order_by('-created_on')
    
    @action(detail=False, methods=["PATCH"], url_path="approve")
    def bulk_approve(self, request):
        """Approve multiple pending donation records"""
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Select all pending donations along with user data
        donations = DonationHistory.objects.filter(id__in=ids, verify_status="pending").select_related("user")
        if not donations.exists():
            return Response({"message": "No pending donations found"}, status=status.HTTP_404_NOT_FOUND)

        update_donations = []
        user_point_map = {}

        for donation in donations:
            # Calculate donation points
            point_increase = 25 if donation.share_status else 20
            donation.donation_point = point_increase
            update_donations.append(donation)

            # Accumulate user points
            user_point_map[donation.user.id] = user_point_map.get(donation.user.id, 0) + point_increase

        # First, bulk update donation points
        DonationHistory.objects.bulk_update(update_donations, ["donation_point"])

        # Then, bulk update user scores
        for user_id, points in user_point_map.items():
            Users.objects.filter(id=user_id).update(score=F("score") + points)

        # Finally, update verify_status using the serializer
        updated_count = 0
        for donation in donations:
            serializer = DonationHistorySerializer(donation, data={"verify_status": "verified"}, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_count += 1

        return Response({"message": f"Successfully approved {updated_count} donation records"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["DELETE"], url_path="delete")
    def bulk_delete(self, request):
        """Delete multiple pending donation records"""
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = DonationHistory.objects.filter(id__in=ids, verify_status="pending").delete()
        return Response({"message": f"Deleted {deleted_count} records"}, status=status.HTTP_204_NO_CONTENT)
    
class UserDonationHistoryViewSet(mixins.ListModelMixin,  # Allows list
                                  mixins.CreateModelMixin,  # Allows POST
                                  viewsets.GenericViewSet):  # No PUT/DELETE
    """ViewSet for users to view and create their donation history."""
    serializer_class = DonationHistorySerializer

    def get_queryset(self):
        return DonationHistory.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Assign the user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
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
