from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

class Users(AbstractUser):
    # You can add any custom fields here
    first_name = models.CharField(max_length=50, null=True, blank=False)
    last_name = models.CharField(max_length=50, null=True, blank=False)
    # email = models.CharField(max_length=50, blank=False)
    birthdate = models.DateField(null=True, blank=False)
    phone_number = models.CharField(max_length=10, null=True, blank=False)
    
    line_user_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    
    personal_info_consent = models.BooleanField(default=False)
    blood_type = models.CharField(max_length=10, null=True, blank=True) #example: AB|Rh+
    latest_donation_date = models.DateField(null=True, blank=True)

    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)
    
    def __str__(self):
        return self.email