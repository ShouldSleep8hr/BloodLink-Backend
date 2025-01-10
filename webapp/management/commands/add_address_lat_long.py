# {
    # "type": "FeatureCollection",
    # "name": "Thailand_Health_Facilities_TH",
    # "crs": {
    #     "type": "name",
    #     "properties": {
    #         "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
    #     }
    # },
    # "features": [
    #     {
    #         "type": "Feature",
    #         "properties": {
    #             "ID": 111000000000.0,
    #             "Ministry": "กระทรวงกลาโหม",
    #             "Department": "กองทัพบก",
    #             "Agency": "กองทัพบก โรงพยาบาลพระมงกุฎเกล้า",
    #             "Address": "แขวงทุ่งพญาไท เขตราชเทวี กรุงเทพมหานคร 10400",
    #             "Lat": 13.76733,
    #             "Long": 100.5342
    #         },
    #         "geometry": {
    #             "type": "Point",
    #             "coordinates": [
    #                 100.5342,
    #                 13.76733
    #             ]
    #         }
    #     },
    #     {
    #         "type": "Feature",
    #         "properties": {
    #             "ID": 111000000000.0,
    #             "Ministry": "กระทรวงยุติธรรม",
    #             "Department": "กรมราชทัณฑ์",
    #             "Agency": "กรมราชทัณฑ์ ทัณฑสถานโรงพยาบาลราชทัณฑ์",
    #             "Address": "แขวงลาดยาว เขตจตุจักร กรุงเทพมหานคร 10900",
    #             "Lat": 13.85018,
    #             "Long": 100.5531
    #         },
    #         "geometry": {
    #             "type": "Point",
    #             "coordinates": [
    #                 100.5531,
    #                 13.85018
    #             ]
    #         }
    #     },...


import requests
from django.core.management.base import BaseCommand
from webapp.models import DonationLocation, SubDistrict, District, Province, Region
from webapp.serializers import DonationLocationSerializer
from webapp.management.commands.region_list import region_list

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Load the GeoJSON data (you can change this to get it from a URL or file)
        response = requests.get("https://data.opendevelopmentmekong.net/dataset/ab20b509-2b7f-442e-8448-05d3a17651ac/resource/76253a1a-b472-4d64-b209-0ea3114f51f4/download/thailand_health_facilities_th.geojson")
        
        if response.status_code == 200:
            geojson_data = response.json()
            existing_locations = DonationLocation.objects.all()
            existing_dict = {location.name: location for location in existing_locations}

            for feature in geojson_data.get('features', []):
                properties = feature.get('properties', {})

                full_name = properties.get('Agency').split()
                for name in full_name:
                    if name.startswith('โรงพยาบาล'):
                        hospital_name = name

                address = properties.get('Address')
                latitude = properties.get('Lat')
                longitude = properties.get('Long')

                if hospital_name in existing_dict:
                    donation_location = existing_dict[hospital_name]
                    
                    # Create a dictionary for validation
                    data = {
                        'name': hospital_name,
                        'address': address,
                        'latitude': latitude,
                        'longitude': longitude,
                    }

                    # Validate using the serializer
                    serializer = DonationLocationSerializer(donation_location, data=data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        print(f"Updated donation location: {hospital_name}")
                    else:
                        print(serializer.errors)
                # else:
                #     print(f"No existing location found for: {name}")
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
