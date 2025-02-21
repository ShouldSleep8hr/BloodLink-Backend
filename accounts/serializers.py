from rest_framework import serializers
from accounts.models import Users
from webapp.models import PreferredArea
from webapp.serializers import PreferredAreaSerializer

class UserSerializer(serializers.ModelSerializer):
    preferred_areas = PreferredAreaSerializer(many=True)

    class Meta:
        model = Users
        fields = ['id', 'full_name', 'line_user_id', 'line_username', 'profile_picture', 'email', 'birthdate', 'phone_number', 'blood_type', 'latest_donation_date', 'preferred_areas', 'score', 'created_on']
        extra_kwargs = {
            'email': {'required': True},  # Ensure email is required
            'line_user_id': {'required': True},  # LINE ID is required
        }

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

        # Update user fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance
    
class UserRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['line_username', 'score', 'profile_picture']

