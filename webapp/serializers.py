from rest_framework import serializers
from webapp.models import Post, DonationLocation, SubDistrict, District, Province, Region, Announcement, DonationHistory, PreferredArea, Achievement, UserAchievement, Event, EventParticipant
from django.conf import settings

class AchievementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'image', 'image_url', 'description']

    def get_image_url(self, obj):
        return self.build_public_url(obj.image) if obj.image else None

    def build_public_url(self, image_field):
        """Construct the public URL by removing query parameters."""
        base_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/"
        return f"{base_url}{image_field}"

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='achievement.name', read_only=True)
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement', 'achievement_name', 'earned_at']

class EventSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id', 'name', 'image', 'image_url', 'description', 'start_date', 'end_date']

    def get_image_url(self, obj):
        return self.build_public_url(obj.image) if obj.image else None

    def build_public_url(self, image_field):
        """Construct the public URL by removing query parameters."""
        base_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/"
        return f"{base_url}{image_field}"

class EventParticipantSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    class Meta:
        model = EventParticipant
        fields = ['id', 'user', 'event', 'event_name', 'joined_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title','content','reference', 'image', 'image_url', 'created_on', 'updated_on']
    
    def get_image_url(self, obj):
        return self.build_public_url(obj.image) if obj.image else None

    def build_public_url(self, image_field):
        """Construct the public URL by removing query parameters."""
        base_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/"
        return f"{base_url}{image_field}"

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
    donor_card_image_url = serializers.SerializerMethodField()
    donation_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationHistory
        fields = [
            'id', 'user', 'donation_date', 'location', 'location_name', 'share_status',
            'donor_card_image', 'donor_card_image_url', 'donation_image', 'donation_image_url',
            'image_description', 'donation_point', 'donation_type', 'verify', 'created_on', 'updated_on'
        ]
        read_only_fields = ['verify', 'created_on', 'updated_on']

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
    
    def get_donor_card_image_url(self, obj):
        return self.build_public_url(obj.donor_card_image) if obj.donor_card_image else None

    def get_donation_image_url(self, obj):
        return self.build_public_url(obj.donation_image) if obj.donation_image else None

    def build_public_url(self, image_field):
        """Construct the public URL by removing query parameters."""
        base_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/"
        return f"{base_url}{image_field}"
    
class PreferredAreaSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        model = PreferredArea
        fields = ['id', 'user', 'district', 'district_name', 'province', 'province_name']
        # fields = ['id', 'districts', 'provinces']

    def validate(self, data):
        # user = self.context["request"].user
        district = data.get('district', None)
        province = data.get('province')

        # Ensure district belongs to the given province before saving
        if district:
            if district.province != province:
                raise serializers.ValidationError({
                    "district": "The selected district does not belong to the specified province."
                })
            
        # Check for duplicate district (if district is not None)
        # if district and PreferredArea.objects.filter(user=8, district=district).exists():
        #     raise serializers.ValidationError({
        #         "district": "You have already added this district to your preferred areas."
        #     })

        return data
    
    def update_preferred_areas(self, user, preferred_areas_data):
        """
        Update the user's preferred areas based on the new data.
        - Update existing ones in order.
        - Delete extra ones if the new list is shorter.
        - Create new ones if the new list is longer.
        """
        existing_areas = list(user.preferred_areas.all())
        num_existing = len(existing_areas)
        num_new = len(preferred_areas_data)

        if num_existing == 0:
            # No existing preferred areas, just create new ones
            PreferredArea.objects.bulk_create([
                PreferredArea(user=user, district=area.get('district', None), province=area['province'])
                for area in preferred_areas_data
            ])
            return

        # Step 1: Update existing preferred areas
        for i in range(min(num_existing, num_new)):
            area = existing_areas[i]
            area_data = preferred_areas_data[i]

            area.district = area_data.get('district', None)
            area.province = area_data['province']
            area.save()

        # Step 2: Delete remaining old areas if new data has fewer items
        if num_existing > num_new:
            for i in range(num_new, num_existing):
                existing_areas[i].delete()

        # Step 3: Create new preferred areas if needed
        for i in range(num_existing, num_new):
            area_data = preferred_areas_data[i]
            PreferredArea.objects.create(
                user = user,
                district = area_data.get('district', None),
                province = area_data['province']
            )