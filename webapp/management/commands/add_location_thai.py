import requests
from django.core.management.base import BaseCommand
from webapp.models import Province, District, SubDistrict, Region
from webapp.management.commands.region_list import region_list


class Command(BaseCommand):
    help = 'Fetch provinces, districts, and subdistricts from API and populate the database'

    def handle(self, *args, **kwargs):
        # Fetch data from APIs with error handling
        try:
            province_response = requests.get("https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_province.json")
            district_response = requests.get("https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_amphure.json")
            subdistrict_response = requests.get("https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_tambon.json")
            
            province_response.raise_for_status()
            district_response.raise_for_status()
            subdistrict_response.raise_for_status()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"API Request Failed: {e}"))
            return

        provinces = province_response.json()
        districts = district_response.json()
        subdistricts = subdistrict_response.json()

        # Step 1: Save Provinces
        province_dict = {}  # To map province_id for later use
        for province in provinces:
            province_obj, created = Province.objects.get_or_create(name=province['name_th'])
            province_dict[province['id']] = province_obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added Province: {province_obj.name}"))
            else:
                self.stdout.write(f"Province already exists: {province_obj.name}")

            # Set Region
            if province_obj.region is None:
                province_region = self.get_region_for_province(province_obj.name)
                if province_region:
                    region_obj, _ = Region.objects.get_or_create(name=province_region)
                    province_obj.region = region_obj
                    province_obj.save()
                    self.stdout.write(self.style.SUCCESS(f'Set region of {province_obj.name} to ภาค{province_region}'))

        # Step 2: Save Districts
        district_dict = {}
        for district in districts:
            province_id = district['province_id']
            province_obj = province_dict.get(province_id)

            if not province_obj:
                self.stdout.write(self.style.ERROR(f"Province ID {province_id} not found for District {district['name_th']}"))
                continue

            district_obj, created = District.objects.get_or_create(name=district['name_th'], province=province_obj)
            district_dict[district['id']] = district_obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added District: {district_obj.name} in {province_obj.name}"))
            else:
                self.stdout.write(f"District already exists: {district_obj.name} in {province_obj.name}")

        # Step 3: Save SubDistricts
        for subdistrict in subdistricts:
            district_id = subdistrict['amphure_id']
            district_obj = district_dict.get(district_id)

            if not district_obj:
                self.stdout.write(self.style.ERROR(f"District ID {district_id} not found for SubDistrict {subdistrict['name_th']}"))
                continue

            subdistrict_obj, created = SubDistrict.objects.get_or_create(name=subdistrict['name_th'], district=district_obj)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added SubDistrict: {subdistrict_obj.name} in {district_obj.name}"))
            else:
                self.stdout.write(f"SubDistrict already exists: {subdistrict_obj.name} in {district_obj.name}")

    def get_region_for_province(self, province_name):
        """Map provinces to regions."""
        for region, provinces in region_list.items():
            if province_name in provinces:
                return region
        return None





# add from tambon.json file
# [408,4,180101,"ต. ในเมือง","Nai Mueang",1801,"อ. เมืองชัยนาท","Mueang Chai Nat",18,"จ. ชัยนาท","Chai Nat",15.181,100.127],
# [200,4,100106,"แขวง เสาชิงช้า","Sao Chingcha",1001,"เขต พระนคร","Phra Nakhon",10,"กรุงเทพมหานคร","Bangkok",13.753,100.5],
# [848,4,110101,"ต. เทศบาลนครสมุทรปราการ","",1101,"อ. เมืองสมุทรปราการ","Mueang Samut Prakan",11,"จ. สมุทรปราการ","Samut Prakarn",13.593,100.597],
# i add กรุงเทพมหานคร in province manually
# i remove all the name เทศบาล
# ต. ในเมือง    อ. เมืองนครราชสีมา   จ. นครราชสีมา doesnt have in this file
# ต. เมืองใต้	อ. เมืองศรีสะเกษ	จ. ศรีสะเกษ doesnt have in this file
# ต. โพนเขวา   อ. เมืองศรีสะเกษ	จ. ศรีสะเกษ doesnt have in this file
# this file has 2 ต. นครนายก  อ. เมืองนครนายก	จ. นครนายก
# i edit "ต. เวียงเหนือ สวนดอก สบตุ๋ย อยู่นอก1 ตำบล คือหัวเ*" อ. เมืองลำปาง จ. ลำปาง to ต. เวียงเหนือ
# ต. หัวเวียง อ. เมืองลำปาง จ. ลำปาง doesnt have in this file
# ต. สบตุ๋ย   อ. เมืองลำปาง จ. ลำปาง doesnt have in this file
# ต. สวนดอก อ. เมืองลำปาง จ. ลำปาง doesnt have in this file
# ต. สาม change to ต. สามตำบล อ. จุฬาภรณ์   จ. นครศรีธรรมราช
# this file has 10 ต. เกาะพยาม  อ. เมืองระนอง	จ. ระนอง
# this file has 8 ต. ปากน้ำ  อ. เมืองระนอง	จ. ระนอง

# import json
# from django.core.management.base import BaseCommand
# from django.conf import settings
# from webapp.models import SubDistrict, District, Province, Region
# from webapp.management.commands.region_list import region_list

# # Load the JSON file
# with open(settings.BASE_DIR / 'tambon.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)

# class Command(BaseCommand):
#     # Parse addresses from DonationLocation and populate Province, District, SubDistrict tables
#     def handle(self, *args, **kwargs):
#         for record in data['records']:
#             subdistrict_name = record[3].strip()  # TAMBON_T
#             district_name = record[6].strip()     # AMPHOE_T
#             province_name = record[9].strip()     # CHANGWAT_T

#             if province_name.startswith('จ.'):
#                 province_name = province_name.replace('จ.', '')

#             if district_name.startswith('อ.'):
#                 district_name = district_name.replace('อ.', '')
#             elif district_name.startswith('เขต'):
#                 district_name = district_name.replace('เขต', '')

#             if subdistrict_name.startswith('ต.'):
#                 subdistrict_name = subdistrict_name.replace('ต.', '')
#             elif subdistrict_name.startswith('แขวง'):
#                 subdistrict_name = subdistrict_name.replace('แขวง', '')

#             # if subdistrict_name == 'ในเมือง':
#             #     subdistrict_name = subdistrict_name + province_name

#             # Create or get Province
#             province, created = Province.objects.get_or_create(name=province_name)

#             # Set the region based on the province name
#             province_region = self.get_region_for_province(province_name)
#             if province_region:
#                 # Get or create the Region object
#                 region_obj, _ = Region.objects.get_or_create(name=province_region)
#                 # Assign the Region object to the Province
#                 province.region = region_obj
#                 province.save()
#                 self.stdout.write(self.style.SUCCESS(f'set region of {province_name} to ภาค{province_region}'))

#             # Create or get District linked to Province
#             district, created = District.objects.get_or_create(name=district_name, province=province)

#             # Create or get SubDistrict linked to District
#             subdistrict, created = SubDistrict.objects.get_or_create(name=subdistrict_name, district=district)

#             if created:
#                 print(f"Added: {subdistrict_name} in {district_name}, {province_name}")
#             else:
#                 print(f"Already exists: {subdistrict_name} in {district_name}, {province_name}")
                
#     def get_region_for_province(self, province_name):
#         for region, provinces in region_list.items():
#             if province_name in provinces:
#                 return region
#         return None