# the address is structured like this
# 1871 ถนนอังรีดูนังต์, แขวงปทุมวัน, เขตปทุมวัน, จังหวัดกรุงเทพมหานคร, 10330 //for Bangkok
# 138/1 ถนนพระองค์ดำ, ตำบลในเมือง, อำเภอเมือง, จังหวัดพิษณุโลก, 65000 //for other provinces

from django.core.management.base import BaseCommand
from webapp.models import DonationLocation, SubDistrict, District, Province, Region
from webapp.management.commands.region_list import region_list

class Command(BaseCommand):
    # Parse addresses from DonationLocation and populate Province, District, SubDistrict tables

    def handle(self, *args, **kwargs):
        # Loop through all DonationLocation records
        for location in DonationLocation.objects.all():
            try:
                address_parts = location.address.split(',')
                
                if len(address_parts) >= 5:  # Ensure there are at least 5 components (number or street, subdistrict, district, province, address code)
                    province_name = address_parts[3].strip().replace('จังหวัด', '')
                    if province_name == "กรุงเทพมหานคร":
                        subdistrict_name = address_parts[1].strip().replace('แขวง', '')
                        district_name = address_parts[2].strip().replace('เขต', '')
                    else:
                        subdistrict_name = address_parts[1].strip().replace('ตำบล', '')
                        district_name = address_parts[2].strip().replace('อำเภอ', '')

                        if subdistrict_name == 'ในเมือง':
                            subdistrict_name = subdistrict_name + province_name
                        if district_name == 'เมือง':
                            district_name = district_name + province_name
                
                    print(subdistrict_name)
                    print(district_name)
                    print(province_name)

                    # Get or create Province
                    province, _ = Province.objects.get_or_create(name=province_name)

                    # Set the region based on the province name
                    province_region = self.get_region_for_province(province_name)
                    print(province_region)
                    if province_region:
                        # Get or create the Region object
                        region_obj, _ = Region.objects.get_or_create(name=province_region)
                        # Assign the Region object to the Province
                        province.region = region_obj
                        province.save()

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
                
                else:
                    self.stdout.write(self.style.WARNING(f'Address format not recognized for location: {location.name}'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing location {location.name}: {str(e)}'))

    def get_region_for_province(self, province_name):
        for region, provinces in region_list.items():
            if province_name in provinces:
                return region
        return None
