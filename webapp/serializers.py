from rest_framework import serializers
from webapp.models import Post, DonationLocation, SubDistrict, District, Province, Region, Announcement, DonationHistory, PreferredArea, Achievement, UserAchievement, Event, EventParticipant, UserPostInterest
from django.conf import settings
from django.core.files.base import File

class UserPostInterestSerializer(serializers.ModelSerializer):
    post_name = serializers.CharField(source='post.recipient_name', read_only=True)
    class Meta:
        model = UserPostInterest
        fields = ['id', 'post', 'post_name', 'created_on']
        read_only_fields = ['id', 'created_on']

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
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_profile_picture = serializers.CharField(source='user.profile_picture', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'recipient_name', 'recipient_blood_type', 'detail', 'user', 'location', 
            'new_address', 'due_date', 'contact', 'number_interest', 'number_donor', 
            'show', 'created_on', 'updated_on', 'user_full_name', 'user_profile_picture'
        ]
        read_only_fields = ['user', 'number_interest', 'number_donor', 'created_on', 'updated_on', 'user_full_name', 'user_profile_picture']

    def validate(self, data):
        """Ensure required fields are present and validate location/new_address."""
        request_data = self.context['request'].data

        # Required fields check (for create only)
        if self.instance is None:
            required_fields = ['recipient_name', 'recipient_blood_type', 'due_date', 'contact']
            missing_fields = [field for field in required_fields if not request_data.get(field)]
            if missing_fields:
                raise serializers.ValidationError({field: "This field is required." for field in missing_fields})

            # Validate 'location' or 'new_address' only when creating a post
            location_id = request_data.get('location')
            new_address = request_data.get('new_address')

            if not location_id and not new_address:
                raise serializers.ValidationError({
                    "location": "Either 'location' or 'new_address' must be provided."
                })

            if location_id and new_address:
                raise serializers.ValidationError({
                    "non_field_errors": ["You cannot provide both 'location' and 'new_address' at the same time."]
                })

        return data

    def create(self, validated_data):
        """Create a post with the validated data."""

        request_data = self.context['request'].data
        location_id = request_data.get('location')
        new_address = request_data.get('new_address')

        if location_id:
            try:
                validated_data['location'] = DonationLocation.objects.get(id=location_id)
            except DonationLocation.DoesNotExist:
                raise serializers.ValidationError({
                    "location": "Location with this ID does not exist."
                })

        if new_address:
            validated_data['new_address'] = new_address

        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Allow only PATCH requests and remove disallowed fields without raising errors."""
        request = self.context.get('request')
        
        if request and request.method == "PUT":
            raise serializers.ValidationError({
                "detail": "PUT method is not allowed. Use PATCH instead."
            })
        
        # Prevent updating certain fields
        disallowed_fields = ['recipient_blood_type', 'location', 'new_address']
        for field in disallowed_fields:
            validated_data.pop(field, None)  # Remove it if present

        # Apply updates
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    
    
class DonationHistorySerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True) 
    donor_card_image_url = serializers.SerializerMethodField()
    donation_image_url = serializers.SerializerMethodField()
    user_full_name = serializers.CharField(source='user.full_name', read_only=True) 
    
    class Meta:
        model = DonationHistory
        fields = [
            'id', 'user', 'user_full_name', 'donation_date', 'location', 'location_name', 'share_status',
            'donor_card_image', 'donor_card_image_url', 'donation_image', 'donation_image_url',
            'image_description', 'donation_point', 'donation_type', 'verify_status', 'created_on', 'updated_on'
        ]
        read_only_fields = ['user_full_name', 'location_name','donor_card_image_ur', 'donation_image_url', 'donation_point', 'donation_type', 'created_on', 'updated_on']
    
    def validate(self, data):
        # Check donor_card_image file validity
        donor_card_image = data.get('donor_card_image', None)
        if donor_card_image and not isinstance(donor_card_image, File):
            data['donor_card_image'] = None  # Invalid file, set to None

        # Check donation_image file validity
        donation_image = data.get('donation_image', None)
        if donation_image and not isinstance(donation_image, File):
            data['donation_image'] = None  # Invalid file, set to None

        print(data)
        return data

    def update(self, instance, validated_data):
        """
        When a donation is verified handle user's achievement.
        """
        user = instance.user
        prev_verify_status = instance.verify_status
        new_verify_status = validated_data.get("verify_status", prev_verify_status)

        instance = super().update(instance, validated_data)  # Perform the update

        # Check if the status changed from anything to "verified"
        if prev_verify_status != "verified" and new_verify_status == "verified":
            # Count the user's verified donations (including this one)
            verified_count = DonationHistory.objects.filter(user=user, verify_status="verified").count()

            # Check and assign achievements based on the count
            achievements_map = {
                1: "ผู้บริจาคโลหิตครั้งแรก",
                5: "ระดับปลาคราฟสีเงิน",
                10: "ระดับปลาคราฟสีทอง",
                20: "ระดับปลาคราฟแพทตินัม",
            }

            if verified_count in achievements_map:
                achievement_name = achievements_map[verified_count]
                achievement = Achievement.objects.get(name=achievement_name)
                UserAchievement.objects.create(user=user, achievement=achievement)

        return instance

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

class SharedDonationHistorySerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True) 
    donor_card_image_url = serializers.SerializerMethodField()
    donation_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationHistory
        fields = [
            'id', 'user', 'donation_date', 'location_name', 'share_status',
            'donor_card_image_url', 'donation_image_url',
            'image_description', 'donation_type', 'verify', 'created_on', 'number_like'
        ]

    def get_donor_card_image_url(self, obj):
        return self.build_public_url(obj.donor_card_image) if obj.donor_card_image else None

    def get_donation_image_url(self, obj):
        return self.build_public_url(obj.donation_image) if obj.donation_image else None

    def build_public_url(self, image_field):
        """Construct the public URL by removing query parameters."""
        base_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/"
        return f"{base_url}{image_field}"
    
# class PreferredAreaSerializer(serializers.ModelSerializer):
#     district_name = serializers.CharField(source='district.name', read_only=True)
#     province_name = serializers.CharField(source='province.name', read_only=True)

#     class Meta:
#         model = PreferredArea
#         fields = ['id', 'district', 'district_name', 'province', 'province_name']
#         # fields = ['id', 'districts', 'provinces']

#     def validate(self, data):
#         user = data.get('user')
#         district = data.get('district', None)
#         province = data.get('province')

#         # Ensure district belongs to the given province before saving
#         if district:
#             if district.province != province:
#                 raise serializers.ValidationError({
#                     "district": "The selected district does not belong to the specified province."
#                 })
            
#         # Check for duplicate district (if district is not None)
#         if district and PreferredArea.objects.filter(user=user, district=district).exists():
#             raise serializers.ValidationError({
#                 "district": "You have already added this district to your preferred areas."
#             })

#         return data
    
#     def update_preferred_areas(self, user, preferred_areas_data):
#         """
#         Update the user's preferred areas based on the new data.
#         - Update existing ones in order.
#         - Delete extra ones if the new list is shorter.
#         - Create new ones if the new list is longer.
#         """
#         existing_areas = list(user.preferred_areas.all())
#         num_existing = len(existing_areas)
#         num_new = len(preferred_areas_data)

#         if num_existing == 0:
#             # No existing preferred areas, just create new ones
#             PreferredArea.objects.bulk_create([
#                 PreferredArea(user=user, district=area.get('district', None), province=area['province'])
#                 for area in preferred_areas_data
#             ])
#             return

#         # Step 1: Update existing preferred areas
#         for i in range(min(num_existing, num_new)):
#             area = existing_areas[i]
#             area_data = preferred_areas_data[i]

#             area.district = area_data.get('district', None)
#             area.province = area_data['province']
#             area.user = user
#             area.save()

#         # Step 2: Delete remaining old areas if new data has fewer items
#         if num_existing > num_new:
#             for i in range(num_new, num_existing):
#                 existing_areas[i].delete()

#         # Step 3: Create new preferred areas if needed
#         for i in range(num_existing, num_new):
#             area_data = preferred_areas_data[i]
#             PreferredArea.objects.create(
#                 user = user,
#                 district = area_data.get('district', None),
#                 province = area_data['province']
#             )

class PreferredAreaSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        model = PreferredArea
        fields = ['id', 'district', 'district_name', 'province', 'province_name']

    def validate(self, data):
        # user = data.get('user')
        district = data.get('district', None)
        province = data.get('province')

        # Ensure district belongs to the given province before saving
        if district and district.province != province:
            raise serializers.ValidationError({
                "district": "The selected district does not belong to the specified province."
            })

        # Check for duplicate district (if district is not None)
        # if district and PreferredArea.objects.filter(user=user, district=district).exists():
        #     raise serializers.ValidationError({
        #         "district": "You have already added this district to your preferred areas."
        #     })

        return data

    def update_preferred_areas(self, user, preferred_areas_data):
        """
        Update the user's preferred areas based on the new data.
        - Allows swapping of districts.
        - Prevents duplicate districts in the new list.
        - Prevents updating if the new list is exactly the same as the existing one.
        - Prevents selecting a whole province and a district within that province at the same time.
        - Uses bulk_update and bulk_create for efficiency.
        """
        existing_areas = list(user.preferred_areas.all())
        num_existing = len(existing_areas)
        num_new = len(preferred_areas_data)

        # Convert existing areas into a set of (district_id, province_id)
        existing_set = {(area.district.id if area.district else None, area.province.id) for area in existing_areas}
        new_set = {(area.get('district').id if area.get('district') else None, area['province'].id) for area in preferred_areas_data}

        # Step 1: If new list is exactly the same as existing, do nothing
        if existing_set == new_set:
            return  # No changes needed

        # Step 2: Validate for duplicate districts and overlapping province-district selections
        new_districts = set()
        selected_provinces = set()

        for area_data in preferred_areas_data:
            district = area_data.get('district', None)
            province = area_data['province']

            # If province is already selected, no district from that province should be allowed
            if province in selected_provinces and district:
                raise serializers.ValidationError({
                    "district": f"You cannot add district {district.name} because province {province.name} is already selected."
                })

            # If a district is selected, ensure the province isn't already fully selected
            if district:
                if province in selected_provinces:
                    raise serializers.ValidationError({
                        "district": f"You cannot add district {district.name} because the entire province {province.name} is already selected."
                    })
                if district.id in new_districts:
                    raise serializers.ValidationError({
                        "district": f"The district {district.name} appears more than once."
                    })
                new_districts.add(district.id)
            else:
                # If only province is selected, store it
                selected_provinces.add(province)

        # Step 3: Update existing preferred areas
        updated_areas = []
        for i in range(min(num_existing, num_new)):
            area = existing_areas[i]
            area_data = preferred_areas_data[i]

            area.district = area_data.get('district', None)
            area.province = area_data['province']
            updated_areas.append(area)

        # Bulk update existing areas
        PreferredArea.objects.bulk_update(updated_areas, ["district", "province"])

        # Step 4: Delete extra old areas
        if num_existing > num_new:
            PreferredArea.objects.filter(id__in=[area.id for area in existing_areas[num_new:num_existing]]).delete()

        # Step 5: Create new areas
        new_areas = [
            PreferredArea(user=user, district=area_data.get('district', None), province=area_data['province'])
            for area_data in preferred_areas_data[num_existing:num_new]
        ]

        # Bulk create new preferred areas
        PreferredArea.objects.bulk_create(new_areas)
