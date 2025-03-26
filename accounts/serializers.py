from rest_framework import serializers
from accounts.models import Users
from webapp.models import PreferredArea
from webapp.serializers import PreferredAreaSerializer

class UserSerializer(serializers.ModelSerializer):
    preferred_areas = PreferredAreaSerializer(many=True)
    rank = serializers.SerializerMethodField()
    total_users = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ['id', 'full_name', 'line_user_id', 'line_username', 'profile_picture', 'email', 'rank', 'total_users', 'birthdate', 'phone_number', 'blood_type', 'latest_donation_date', 'preferred_areas', 'score', 'created_on', 'is_staff']
        # extra_kwargs = {
        #     'email': {'required': True},  # Ensure email is required
        #     'line_user_id': {'required': True},  # LINE ID is required
        # }

    def create(self, validated_data):
        # Create a user with line_user_id and email
        user = Users.objects.create(**validated_data)
        return user

    # def update(self, instance, validated_data):
    #     # Update only line_user_id and email
    #     for field, value in validated_data.items():
    #         setattr(instance, field, value)
    #     instance.save()
    #     return instance
    
    def update(self, instance, validated_data):
        restricted_fields = {'id', 'line_user_id', 'email', 'rank', 'total_users', 'score', 'created_on'}
        for field in restricted_fields:
            validated_data.pop(field, None)
            
        # Extract preferred areas if provided
        preferred_areas_data = validated_data.pop('preferred_areas', None)

        # Update preferred areas only if provided
        if preferred_areas_data is not None:
            if instance.preferred_areas.exists() and preferred_areas_data == []:
                # Delete all if user sent an empty list
                instance.preferred_areas.all().delete()
            else:
                # Update preferred areas
                preferred_area_serializer = PreferredAreaSerializer()
                preferred_area_serializer.update_preferred_areas(instance, preferred_areas_data)

        # Remove any fields that are explicitly set to None (null)
        validated_data = {k: v for k, v in validated_data.items() if v is not None}

        # Update user fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance
    
    def get_rank(self, obj):
        """Assign rank based on ordering"""
        sorted_users = Users.objects.order_by('-score', 'id')
        rank_dict = {user.id: rank + 1 for rank, user in enumerate(sorted_users)}
        return rank_dict.get(obj.id, None)  # Return the rank
    
    def get_total_users(self, obj):
        """Return the total number of users"""
        return Users.objects.count()  # Count all users in the database
    
class UserRankingSerializer(serializers.ModelSerializer):
    # rank = serializers.SerializerMethodField()
    # total_users = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ['full_name', 'score', 'profile_picture']

    # def get_rank(self, obj):
    #     """Assign rank based on ordering"""
    #     sorted_users = Users.objects.order_by('-score')[:5]  # Get top 5
    #     rank_dict = {user.id: rank + 1 for rank, user in enumerate(sorted_users)}
    #     return rank_dict.get(obj.id, None)  # Return the rank

    # def get_total_users(self, obj):
    #     """Return the total number of users"""
    #     return Users.objects.count()  # Count all users in the database

