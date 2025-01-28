# from rest_framework import serializers
# from accounts.models import Users

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Users
#         fields = ['id', 'email', 'password', 'first_name', 'last_name', 'birthdate']
#         extra_kwargs = {
#             'password': {'write_only': True},  # Hide password in the serialized output
#             'email': {'required': True}        # Ensure email is required as it's the username field
#         }

#     def create(self, validated_data):
#         # Create user and hash the password
#         password = validated_data.pop('password', None)
#         user = Users(**validated_data)
#         if password:
#             user.set_password(password)

#         user.save()
#         return user

#     def update(self, instance, validated_data):
#         # Handle user update, including password hash
#         password = validated_data.pop('password', None)
#         instance = super().update(instance, validated_data)
#         if password:
#             instance.set_password(password)
#             instance.save()
#         return instance

from rest_framework import serializers
from accounts.models import Users
from webapp.serializers import PreferredAreaSerializer

class UserSerializer(serializers.ModelSerializer):
    preferred_areas = PreferredAreaSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'full_name', 'line_user_id', 'line_username', 'email', 'birthdate', 'phone_number', 'blood_type', 'latest_donation_date', 'preferred_areas']
        extra_kwargs = {
            'email': {'required': True},  # Ensure email is required
            'line_user_id': {'required': True},  # LINE ID is required
        }

    def create(self, validated_data):
        # Create a user with line_user_id and email
        user = Users.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Update only line_user_id and email
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

