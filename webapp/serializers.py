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
        fields = ['id', 'name', 'keyword', 'address', 'contact', 'subdistrict', 'district', 'province', 'latitude', 'longitude', 'googlemap', 'facility_type']

# class DonationHistorySerializer(serializers.ModelSerializer):
#     subdistrict = serializers.CharField(source='subdistrict.name', read_only=True)
#     district = serializers.CharField(source='subdistrict.district.name', read_only=True)
#     province = serializers.CharField(source='subdistrict.district.province.name', read_only=True)
#     class Meta:
#         model = DonationLocation
#         fields = ['id', 'name', 'keyword', 'address', 'contact', 'subdistrict', 'district', 'province', 'latitude', 'longtitude', 'googlemap']

class PostSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.email', read_only=True)
    # location = serializers.CharField(source='location.name')
    location = DonationLocationSerializer(read_only=True)
    # latitude = serializers.DecimalField(max_digits=20, decimal_places=15, source='location.latitude', read_only=True)
    # longitude = serializers.DecimalField(max_digits=20, decimal_places=15, source='location.longitude', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'recipient_name', 'recipient_blood_type', 'detail', 'user', 'location', 'due_date','contact', 'number_interest', 'number_donor', 'show']

    def create(self, validated_data):
        # Manually retrieve the location ID from the request data
        location_id = self.context['request'].data.get('location')
        
        if not location_id:
            raise serializers.ValidationError({"location": "This field is required."})

        # Fetch the location instance based on the provided ID
        try:
            location_instance = DonationLocation.objects.get(id=location_id)
        except DonationLocation.DoesNotExist:
            raise serializers.ValidationError({"location": "Location with this ID does not exist."})

        # Assign the location instance and the authenticated user
        validated_data['location'] = location_instance
        # validated_data['user'] = self.context['request'].user

        # Create the post
        post = Post.objects.create(**validated_data)
        return post