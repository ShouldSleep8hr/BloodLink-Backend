# รพศ โรงเรียนแพทย์

import requests
from django.core.management.base import BaseCommand
from webapp.models import DonationLocation
from webapp.serializers import DonationLocationSerializer

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Send a GET request to the API
        # response = requests.get("https://data.ha.or.th/api/3/action/datastore_search?q=รพศ&resource_id=d9832ac9-a1b3-4ac9-8e7b-eef682d7985a")
        # response = requests.get("https://data.ha.or.th/api/3/action/datastore_search?q=โรงเรียนแพทย์&resource_id=d9832ac9-a1b3-4ac9-8e7b-eef682d7985a")
        response = requests.get("https://data.ha.or.th/api/3/action/datastore_search?q=รพท&resource_id=d9832ac9-a1b3-4ac9-8e7b-eef682d7985a")

        if response.status_code == 200:
            data = response.json()

            # Loop through the records in the API response and save each one
            for record in data.get('result', {}).get('records', []):
                hospital_name = record.get('โรงพยาบาล')  # Extract the "โรงพยาบาล" field
                if hospital_name:  # Ensure the field exists
                    # Check if a location with this name already exists
                    name = 'โรงพยาบาล' + hospital_name
                    existing_location = DonationLocation.objects.filter(name=name).first()

                    if existing_location:
                        print(f"Location '{name}' already exists. Skipping creation.")
                    else:
                        # Create a dictionary with only the required data
                        filtered_record = {
                            'name': name,
                            'facility_type': '1',  # Save '1' for โรงพยาบาล
                        }

                        # Serialize the filtered data
                        serializer = DonationLocationSerializer(data=filtered_record)
                        if serializer.is_valid():
                            serializer.save()
                            print(f"Saved {filtered_record['name']}")  # Notify on successful save
                        else:
                            print(serializer.errors)  # Handle errors
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")