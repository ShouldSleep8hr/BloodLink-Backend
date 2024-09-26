from django.db import models
from accounts.models import Users
from django.utils import timezone

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
    name = models.CharField(max_length=50, null=True, blank=False)
    address = models.CharField(max_length=200, null=True, blank=True)
    keyword = models.CharField(max_length=200, null=True, blank=True)

    subdistrict = models.ForeignKey(SubDistrict, related_name='donation_locations', on_delete=models.CASCADE, null=True, blank=True)
    
    latitude = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longtitude = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    contact = models.CharField(max_length=200, null=True, blank=True) #still thinking number or email
    facility_type = models.CharField(max_length=50, null=True, blank=True) #โรงพยาบาล, ศูนย์กาชาด, หน่วยรับบริจาคเคลื่อนที่
    available_date = models.DateTimeField(null=True, blank=True) #สำหรับหน่วยรับบริจาคเคลื่อนที่
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    googlemap = models.CharField(max_length=200, null=True, blank=True) #googlemap link
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.name
    
class DonationHistory(models.Model):
    user = models.ForeignKey(Users, related_name='donation_histories', on_delete=models.CASCADE)

    donation_date = models.DateTimeField("donation date", null=True, blank=True)
    location = models.ForeignKey(DonationLocation, on_delete=models.CASCADE)
    donation_image = models.FilePathField #just store image path of user's donation image from LINE
    verify = models.BooleanField(default=False)
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

class Post(models.Model):
    recipient_name = models.CharField(max_length=50, null=True, blank=False)
    recipient_blood_type = models.CharField(max_length=10, null=True, blank=True) #example: AB|Rh+
    
    user = models.ForeignKey(Users, related_name='post', on_delete=models.CASCADE, null=True, blank=False)
    location = models.ForeignKey(DonationLocation, related_name='post', on_delete=models.SET_NULL, null=True, blank=False)

    due_date = models.DateTimeField("due date", null=True, blank=True)
    detail = models.TextField(max_length=200, null=True, blank=True)
    contact = models.CharField(max_length=200, null=True, blank=True) #might add User.contact, still thinking number or email
    number_interest = models.IntegerField(null=True, blank=True)
    number_donor = models.IntegerField(null=True, blank=True)
    show = models.BooleanField(default=False)
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.recipient_name
    
class PreferredArea(models.Model):
    user    = models.ForeignKey(Users, related_name='preferred_areas', on_delete=models.CASCADE, null=True, blank=False)

    # Allow multiple subdistricts, districts, and provinces
    subdistricts = models.ManyToManyField(SubDistrict, related_name='preferred_areas', blank=True)
    districts = models.ManyToManyField(District, related_name='preferred_areas', blank=True)
    provinces = models.ManyToManyField(Province, related_name='preferred_areas', blank=True)
    # subdistrict = models.ForeignKey(SubDistrict, related_name='preferred_areas', on_delete=models.SET_NULL, null=True, blank=True)
    # district = models.ForeignKey(District, related_name='preferred_areas', on_delete=models.SET_NULL, null=True, blank=True)
    # province = models.ForeignKey(Province, related_name='preferred_areas', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_on = models.DateTimeField("date created", default=timezone.now)
    updated_on = models.DateTimeField("date updated", auto_now=True)

    def __str__(self):
        return self.user.email
