# the address is structured like this
# new
# 1871 ถ.อังรีดูนังต์ แขวงปทุมวัน เขตปทุมวัน จ.กรุงเทพมหานคร 10330 //for Bangkok
# ศาลากลาง ถ.นารายณ์มหาราช ต.ทะเลชุบศร อ.เมือง จ.ลพบุรี 15000 //for other provinces

import requests
from django.core.management.base import BaseCommand
from webapp.models import DonationLocation, SubDistrict, District, Province, Region
from webapp.serializers import DonationLocationSerializer
from webapp.management.commands.region_list import region_list

class Command(BaseCommand):
    # Parse addresses from DonationLocation and populate Province, District, SubDistrict tables
    def handle(self, *args, **kwargs):
        # Loop through all DonationLocation records
        for location in DonationLocation.objects.all():
            try:
                address_parts = location.address.split()
                for address in address_parts:
                    if address.startswith('จ.'):
                        province_name = address.replace('จ.', '')
                    elif address.startswith('อ.'):
                        district_name = address.replace('อ.', '')
                    elif address.startswith('ต.'):
                        subdistrict_name = address.replace('ต.', '')
                    elif address.startswith('เขต'):
                        district_name = address.replace('เขต', '')
                    elif address.startswith('เแขวง'):
                        subdistrict_name = address.replace('เแขวง', '')

                if subdistrict_name == 'ในเมือง':
                    subdistrict_name = subdistrict_name + province_name
                if district_name == 'เมือง':
                    district_name = district_name + province_name
                
                self.stdout.write(self.style.SUCCESS(f'{subdistrict_name}'))
                self.stdout.write(self.style.SUCCESS(f'{district_name}'))
                self.stdout.write(self.style.SUCCESS(f'{province_name}'))

                # Get or create Province
                province, _ = Province.objects.get_or_create(name=province_name)

                # Set the region based on the province name
                province_region = self.get_region_for_province(province_name)
                if province_region:
                    # Get or create the Region object
                    region_obj, _ = Region.objects.get_or_create(name=province_region)
                    # Assign the Region object to the Province
                    province.region = region_obj
                    province.save()
                    self.stdout.write(self.style.SUCCESS(f'set region of {province_name} to ภาค{province_region}'))

                # Get or create District (ensure it references the right Province)
                district, _ = District.objects.get_or_create(name=district_name, province=province)

                # Get or create SubDistrict (ensure it references the right District)
                subdistrict, _ = SubDistrict.objects.get_or_create(name=subdistrict_name, district=district)

                # Ensure that SubDistrict has the correct District and District has the correct Province
                subdistrict.district = district
                district.province = province

                # Save these relationships if they were modified
                subdistrict.save()
                district.save()

                # Update the DonationLocation to reference the correct SubDistrict, District, and Province
                location.subdistrict = subdistrict
                location.save()

                self.stdout.write(self.style.SUCCESS(f'Processed location: {location.name}'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing location {location.name}: {str(e)}'))

            print()

    def get_region_for_province(self, province_name):
        for region, provinces in region_list.items():
            if province_name in provinces:
                return region
        return None
