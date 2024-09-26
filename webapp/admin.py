from django.contrib import admin

from webapp.models import Region, Province, District, SubDistrict, DonationLocation, DonationHistory, Post, PreferredArea

admin.site.register(Region)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(SubDistrict)
admin.site.register(DonationLocation)
admin.site.register(DonationHistory)
admin.site.register(Post)
admin.site.register(PreferredArea)