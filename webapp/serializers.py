from rest_framework import serializers
from webapp.models import Post, DonationLocation, SubDistrict, District, Province, Region, Announcement, DonationHistory, PreferredArea, Achievement, UserAchievement, Event, EventParticipant

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description']

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer()
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement', 'earned_at']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'start_date', 'end_date']

class EventParticipantSerializer(serializers.ModelSerializer):
    event = EventSerializer()
    class Meta:
        model = EventParticipant
        fields = ['id', 'user', 'event', 'joined_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title','content','reference', 'image', 'created_on', 'updated_on']

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
    # user = serializers.CharField(source='user.email', read_only=True)
    # location = serializers.CharField(source='location.name')
    # location = DonationLocationSerializer()
    # latitude = serializers.DecimalField(max_digits=20, decimal_places=15, source='location.latitude', read_only=True)
    # longitude = serializers.DecimalField(max_digits=20, decimal_places=15, source='location.longitude', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'recipient_name', 'recipient_blood_type', 'detail', 'user', 'location', 'new_address', 'due_date','contact', 'number_interest', 'number_donor', 'show', 'created_on']

    def create(self, validated_data):
        request_data = self.context['request'].data
        location_id = request_data.get('location')
        new_address = request_data.get('new_address')

        if not location_id and not new_address:
            raise serializers.ValidationError({
                "location": "Either 'location' or 'new_address' must be provided."
            })
        
        # Raise error if both fields are provided
        if location_id and new_address:
            raise serializers.ValidationError({
                "non_field_errors": ["You cannot provide both 'location' and 'new_address' at the same time."]
            })

        if location_id:
            try:
                location_instance = DonationLocation.objects.get(id=location_id)
                validated_data['location'] = location_instance
            except DonationLocation.DoesNotExist:
                raise serializers.ValidationError({
                    "location": "Location with this ID does not exist."
                })
        
        # Assign new_address if provided
        if new_address:
            validated_data['new_address'] = new_address

        # print("Validated Data:", validated_data)
        
        # Create the post
        post = Post.objects.create(**validated_data)
        return post
    
    
class DonationHistorySerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True) 
    donation_image = serializers.ImageField(required=False, allow_null=True)  # Optional image field
    
    class Meta:
        model = DonationHistory
        fields = ['id', 'user', 'donation_date', 'location', 'location_name', 'share_status', 'donor_card_image', 'donation_image', 'image_description', 'donation_point', 'donation_type', 'verify', 'created_on', 'updated_on']
        read_only_fields = ['verify', 'created_on', 'updated_on']  # These fields are managed automatically

    def validate(self, data):
        # Validate location name
        location_id = self.context['request'].data.get('location')
        if not location_id:
            raise serializers.ValidationError({"location": "This field is required."})

        # Ensure the location exists
        try:
            data['location'] = DonationLocation.objects.get(id=location_id)
        except DonationLocation.DoesNotExist:
            raise serializers.ValidationError({"location": "Location with this name does not exist."})

        return data

    def create(self, validated_data):
        # Directly create the donation history record
        return DonationHistory.objects.create(**validated_data)
    
class PreferredAreaSerializer(serializers.ModelSerializer):
    # subdistricts = SubDistrictSerializer(many=True, read_only=True)
    # districts = DistrictSerializer(many=True, read_only=True)
    # provinces = ProvinceSerializer(many=True, read_only=True)

    # district_id = serializers.PrimaryKeyRelatedField(
    #     queryset=District.objects.all(),
    #     source='district',  # Maps to the ForeignKey field
    #     write_only=True
    # )

    district_name = serializers.CharField(source='district.name', read_only=True)
    province_name = serializers.CharField(source='province.name', read_only=True)

    # district = DistrictSerializer()
    # province = ProvinceSerializer()
    class Meta:
        model = PreferredArea
        fields = ['id', 'user', 'district', 'district_name', 'province', 'province_name']
        # fields = ['id', 'districts', 'provinces']