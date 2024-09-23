from rest_framework import serializers
from webapp.models import Post, DonationLocation, SubDistrict, Province, Region, announcements

class announcements_serializer(serializers.ModelSerializer):
    class Meta:
        model = announcements
        fields = ['title','content','reference']

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']

class ProvinceSerializer(serializers.ModelSerializer):
    region = serializers.CharField(source='region.name', read_only=True)
    class Meta:
        model = Province
        fields = ['id', 'name', 'region']

class DistrictSerializer(serializers.ModelSerializer):
    province = serializers.CharField(source='province.name', read_only=True)
    class Meta:
        model = SubDistrict
        fields = ['id', 'name', 'province']

class SubDistrictSerializer(serializers.ModelSerializer):
    district = serializers.CharField(source='district.name', read_only=True)
    province = serializers.CharField(source='district.province.name', read_only=True)
    class Meta:
        model = SubDistrict
        fields = ['id', 'name', 'district', 'province']

class DonationLocationSerializer(serializers.ModelSerializer):
    subdistrict = serializers.CharField(source='subdistrict.name', read_only=True)
    district = serializers.CharField(source='subdistrict.district.name', read_only=True)
    province = serializers.CharField(source='subdistrict.district.province.name', read_only=True)
    class Meta:
        model = DonationLocation
        fields = ['id', 'name', 'address', 'contact', 'subdistrict', 'district', 'province', 'latitude', 'longtitude', 'googlemap']

class PostSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    location = serializers.CharField(source='location.name', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'recipient_name', 'detail', 'user', 'location', 'due_date','contact', 'number_interest', 'number_donor', 'show']
        read_only_fields = ['user']  # Exclude 'user' from being required during creation