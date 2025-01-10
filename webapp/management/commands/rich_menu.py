import requests
from django.core.management.base import BaseCommand
from linemessagingapi.models import LineChannel

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        line_bot = LineChannel.objects.get(id=1)
        channel_access_token = line_bot.channel_access_token

        # 1
        # url = "https://api.line.me/v2/bot/richmenu"
        # headers = {
        #     "Authorization": f"Bearer {channel_access_token}",
        #     "Content-Type": "application/json"
        # }
        # data = {
        #     "size": {
        #         "width": 1200,
        #         "height": 809
        #     },
        #     "selected": False,
        #     "name": "Test the default rich menu",
        #     "chatBarText": "Tap to open",
        #     "areas": [
        #         {
        #             "bounds": {
        #                 "x": 0,
        #                 "y": 0,
        #                 "width": 599,
        #                 "height": 404
        #             },
        #             "action": {
        #                 "type": "uri",
        #                 "label": "Tap area A",
        #                 "uri": "https://developers.line.biz/en/news/"
        #             }
        #         },
        #         {
        #             "bounds": {
        #                 "x": 600,
        #                 "y": 0,
        #                 "width": 600,
        #                 "height": 404
        #             },
        #             "action": {
        #                 "type": "uri",
        #                 "label": "Tap area B",
        #                 "uri": "https://lineapiusecase.com/en/top.html"
        #             }
        #         },
        #         {
        #             "bounds": {
        #                 "x": 0,
        #                 "y": 405,
        #                 "width": 599,
        #                 "height": 404
        #             },
        #             "action": {
        #                 "type": "uri",
        #                 "label": "Tap area C",
        #                 "uri": "https://techblog.lycorp.co.jp/en/"
        #             }
        #         },
        #         {
        #             "bounds": {
        #                 "x": 600,
        #                 "y": 405,
        #                 "width": 600,
        #                 "height": 404
        #             },
        #             "action": {
        #                 "type": "uri",
        #                 "label": "Tap area D",
        #                 "uri": "https://developers.line.biz/en/news/"
        #             }
        #         }
        #     ]
        # }

        # response = requests.post(url, headers=headers, json=data)

        # print(f"Status Code: {response.status_code}")
        # print(f"Response: {response.text}")


        # 2
        # rich_menu_id = "richmenu-3939d46831981741ffcd9e7262bde7c5"  # Replace with your richMenuId
        # image_path = "D:/Y4/BloodLink2/blooddonation-backend/LINE rich menu.png"  # Replace with your image file path

        # url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
        # headers = {
        #     "Authorization": f"Bearer {channel_access_token}",
        #     "Content-Type": "image/png"
        # }

        # with open(image_path, 'rb') as image_file:
        #     response = requests.post(url, headers=headers, data=image_file)

        # print(f"Status Code: {response.status_code}")
        # print(f"Response: {response.text}")


        # 3
        rich_menu_id = "richmenu-3939d46831981741ffcd9e7262bde7c5"  # Replace with your richMenuId
        url = f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}"
        headers = {
            "Authorization": f"Bearer {channel_access_token}"
        }

        response = requests.post(url, headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
