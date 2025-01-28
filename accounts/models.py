from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class Users(AbstractUser):
    # You can add any custom fields here
    # Removing the username field
    username = None

    # Use email as the username field for authentication
    email = models.EmailField(unique=True, blank=False)

    # first_name = models.CharField(max_length=50, null=True, blank=False)
    # last_name = models.CharField(max_length=50, null=True, blank=False)
    full_name = models.CharField(max_length=100, null=True, blank=False)
    
    birthdate = models.DateField(null=True, blank=False)
    phone_number = models.CharField(max_length=10, null=True, blank=False)
    
    line_user_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    line_username = models.CharField(max_length=255, unique=False, blank=True, null=True)
    
    personal_info_consent = models.BooleanField(default=False)
    blood_type = models.CharField(max_length=10, null=True, blank=True) #example: AB|Rh+
    latest_donation_date = models.DateField(null=True, blank=True)

    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    # unique_token = models.CharField(max_length=64, unique=True, blank=True, null=True)

    # Set the email field to be used as the unique identifier for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birthdate']

    objects = CustomUserManager()  # Set the custom manager
    
    def __str__(self):
        return self.email