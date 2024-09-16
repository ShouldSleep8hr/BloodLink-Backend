from rest_framework import serializers
from accounts.models import Users

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name', 'email', 'birthdate']
        extra_kwargs = {
            'password': {'write_only': True}  # Password should not be exposed in serialized output
        }

    def create(self, validated_data):
        # Create user and hash password
        user = Users.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Update user and handle password hashing
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

