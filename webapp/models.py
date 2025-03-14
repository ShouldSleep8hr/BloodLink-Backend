import os
import uuid
from django.db import models
from accounts.models import Users
from django.utils import timezone

from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings

class GCSMediaStorage(GoogleCloudStorage):
    bucket_name = settings.GS_BUCKET_NAME
    location = ''  # To avoid creating folders

def unique_upload_path(instance, filename, folder):
    """Generate a unique file path inside a given folder."""
    ext = os.path.splitext(filename)[1]  # Extract file extension
    unique_filename = f"{uuid.uuid4()}{ext}"  # Generate unique filename
    return f"{folder}/{unique_filename}"

# Named functions to use in models (Django can serialize them)
def donor_card_upload_path(instance, filename):
    return unique_upload_path(instance, filename, "donor-card")

def donation_image_upload_path(instance, filename):
    return unique_upload_path(instance, filename, "donation")

def announcement_image_upload_path(instance, filename):
    return unique_upload_path(instance, filename, "announcement")

def achievement_image_upload_path(instance, filename):
    return unique_upload_path(instance, filename, "achievement")

def event_image_upload_path(instance, filename):
    return unique_upload_path(instance, filename, "event")

facility_type_choice = (
    ('1','โรงพยาบาล'),
    ('2','ศูนย์กาชาด'),
    ('3','หน่วยรับบริจาคเคลื่อนที่'),
)

donation_type_choice = [
    ("ทั่วไป", "บริจาคโลหิตทั่วไป"),
    ("ฉุกเฉิน", "บริจาคโลหิตฉุกเฉิน"),
]

donation_history_status_choice = [
    ("pending", "รอการตรวจสอบ"),
    ("verified", "ได้รับการยืนยัน"),
]

class Region(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)

    def __str__(self):
        return self.name
    
class Province(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)
    region = models.ForeignKey(Region, related_name='provinces', on_delete=models.CASCADE, null=True, blank=False)

    def __str__(self):
        return self.name
    
class District(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)
    province = models.ForeignKey(Province, related_name='districts', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class SubDistrict(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)
    district = models.ForeignKey(District, related_name='subdistricts', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class DonationLocation(models.Model):
    name = models.CharField(max_length=200, null=True, blank=False)
    address = models.CharField(max_length=200, null=True, blank=True)
    keyword = models.CharField(max_length=200, null=True, blank=True)

    subdistrict = models.ForeignKey(SubDistrict, related_name='donation_locations', on_delete=models.CASCADE, null=True, blank=True)
    
    latitude = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    contact = models.CharField(max_length=200, null=True, blank=True) #still thinking number or email
    # facility_type = models.CharField(max_length=50, null=True, blank=True) #โรงพยาบาล, ศูนย์กาชาด, หน่วยรับบริจาคเคลื่อนที่
    facility_type = models.CharField(max_length=50, null=True, blank=True, choices=facility_type_choice, default='1') #โรงพยาบาล, ศูนย์กาชาด, หน่วยรับบริจาคเคลื่อนที่
    
    started_date = models.DateField(null=True, blank=True) #สำหรับหน่วยรับบริจาคเคลื่อนที่
    due_date = models.DateField(null=True, blank=True) #สำหรับหน่วยรับบริจาคเคลื่อนที่
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    googlemap = models.CharField(max_length=200, null=True, blank=True) #googlemap link
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    recipient_name = models.CharField(max_length=50, null=True, blank=False)
    recipient_blood_type = models.CharField(max_length=10, null=True, blank=True) #example: AB|Rh+
    
    user = models.ForeignKey(Users, related_name='post', on_delete=models.CASCADE, null=True, blank=False)
    location = models.ForeignKey(DonationLocation, related_name='post', on_delete=models.SET_NULL, null=True, blank=True)
    new_address = models.CharField(max_length=255, null=True, blank=True)

    due_date = models.DateTimeField("due date", null=True, blank=True)
    detail = models.TextField(max_length=200, null=True, blank=True)
    contact = models.CharField(max_length=200, null=True, blank=True) #might add User.contact, still thinking number or email
    number_interest = models.IntegerField(default=0)
    number_donor = models.IntegerField(default=0)
    show = models.BooleanField(default=True)
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.recipient_name
    
class UserPostInterest(models.Model):
    user = models.ForeignKey(Users, related_name='interested_posts', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='interested_users', on_delete=models.CASCADE)
    created_on = models.DateTimeField("date created", default=timezone.now)
    
    def __str__(self):
        return f'{self.user} is interested in {self.post}'

class DonationHistory(models.Model):
    user = models.ForeignKey(Users, related_name='donation_histories', on_delete=models.CASCADE)

    donation_date = models.DateTimeField("donation date", null=True, blank=True)
    location = models.ForeignKey(DonationLocation, on_delete=models.SET_NULL, null=True, blank=True)
    share_status = models.BooleanField(default=False)
    number_like = models.IntegerField(default=0)
    
    donor_card_image = models.FileField(
        upload_to=donor_card_upload_path,
        storage=GCSMediaStorage(),
        blank=True,
        null=True
    )
    donation_image = models.FileField(
        upload_to=donation_image_upload_path,
        storage=GCSMediaStorage(),  # Use the GCS storage backend for this field only
        blank=True,
        null=True
    )
    image_description = models.TextField(blank=True, null=True)
    donation_point = models.PositiveIntegerField(default=0)
    donation_type = models.CharField(max_length=10, choices=donation_type_choice, default="ทั่วไป")
    # Link to emergency post (nullable for general donations)
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, null=True, blank=True, related_name="emergency_donation_histories"
    )
    
    verify_status = models.CharField(max_length=10, choices=donation_history_status_choice, default="pending")
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)
    
class PreferredArea(models.Model):
    user    = models.ForeignKey(Users, related_name='preferred_areas', on_delete=models.CASCADE, blank=False)

    # Allow multiple subdistricts, districts, and provinces
    # subdistricts = models.ManyToManyField(SubDistrict, related_name='preferred_areas', blank=True)
    # districts = models.ManyToManyField(District, related_name='preferred_areas', blank=True)
    # provinces = models.ManyToManyField(Province, related_name='preferred_areas', blank=True)

    # subdistrict = models.ForeignKey(SubDistrict, related_name='preferred_areas', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, related_name='preferred_areas', on_delete=models.CASCADE, null=True, blank=True)
    province = models.ForeignKey(Province, related_name='preferred_areas', on_delete=models.CASCADE, blank=False)
    
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.user.email

class Announcement(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=200, null=True, blank=True)
    image = models.FileField(
        upload_to=announcement_image_upload_path,
        storage=GCSMediaStorage(),  # Use the GCS storage backend for this field only
        blank=True,
        null=True
    )
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.title

class Achievement(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(
        upload_to=achievement_image_upload_path,
        storage=GCSMediaStorage(),  # Use the GCS storage backend for this field only
        blank=True,
        null=True
    )
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.name
    
class UserAchievement(models.Model):
    achievement = models.ForeignKey(Achievement, related_name='user_achievements', on_delete=models.CASCADE, null=True, blank=False)
    user    = models.ForeignKey(Users, related_name='user_achievements', on_delete=models.CASCADE, null=True, blank=False)
    earned_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} earned {self.achievement} at {self.earned_at}"

class Event(models.Model):
    name = models.CharField(max_length=50, null=True, blank=False)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    image = models.FileField(
        upload_to=event_image_upload_path,
        storage=GCSMediaStorage(),  # Use the GCS storage backend for this field only
        blank=True,
        null=True
    )

    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.name
    
class EventParticipant(models.Model):
    event = models.ForeignKey(Event, related_name='event_participants', on_delete=models.CASCADE, null=True, blank=False)
    user    = models.ForeignKey(Users, related_name='event_participants', on_delete=models.CASCADE, null=True, blank=False)
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} joined {self.event} at {self.joined_at}"
