from django.contrib import admin
from django.utils.html import format_html
from webapp.models import Region, Province, District, SubDistrict, DonationLocation, DonationHistory, Post, PreferredArea, announcements

class DonationLocationAdmin(admin.ModelAdmin):
    # Specify the fields you want to display in the list view
    list_display = ('name', 'address', 'latitude', 'longitude', 'facility_type', 'googlemap_link', 'get_region')

    # Optionally add search functionality
    search_fields = ('name', 'address')

    # Optionally add filters
    list_filter = ('facility_type', 'created_on')

    # Optionally make fields read-only in the admin
    readonly_fields = ('created_on', 'updated_on')

    # Custom method to create a clickable Google Maps link
    def googlemap_link(self, obj):
        if obj.googlemap:  # Ensure the field is not empty
            return format_html('<a href="{}">Google Map</a>', obj.googlemap)
        return "-"
    googlemap_link.short_description = 'Google Map'  # Customize column name

     # Custom method to display province
    def get_region(self, obj):
        return obj.subdistrict.district.province.region.name if obj.subdistrict and obj.subdistrict.district.province.region else '-'
    get_region.short_description = 'Region'

class SubDistrictAdmin(admin.ModelAdmin):
    # Specify the fields you want to display in the list view
    list_display = ('name', 'district', 'get_province', 'get_region')

    # Optionally add search functionality
    search_fields = ('name', 'district', 'district__province', 'district__province__region')

    # Optionally add filters
    list_filter = ('district', 'district__province')  # Filtering by related fields

    # Custom method to display province
    def get_province(self, obj):
        return obj.district.province.name if obj.district and obj.district.province else '-'
    get_province.short_description = 'Province'

    # Custom method to display region
    def get_region(self, obj):
        return obj.district.province.region.name if obj.district and obj.district.province and obj.district.province.region else '-'
    get_region.short_description = 'Region'

admin.site.register(Region)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(SubDistrict, SubDistrictAdmin)
admin.site.register(DonationLocation, DonationLocationAdmin)
admin.site.register(DonationHistory)
admin.site.register(Post)
admin.site.register(PreferredArea)
admin.site.register(announcements)
