import requests
from django.core.management.base import BaseCommand
from linemessagingapi.models import LineChannel
import os
from django.conf import settings

from accounts.models import Users
from webapp.models import Post
from django.db.models import Q
from linemessagingapi.views import Webhook
from linebot.models import TextSendMessage, ButtonsTemplate, TemplateSendMessage, URITemplateAction, FlexSendMessage
from linebot import LineBotApi

from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        line_bot = LineChannel.objects.get(id=1)
        channel_access_token = line_bot.channel_access_token

        # # 1
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
        #                 "uri": "https://kmitldev-blood-link.netlify.app/line/donation-submission"
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
        #                 "type": "message",
        #                 "label": "Tap area B",
        #                 "text": "บริจาคโลหิตใกล้ฉัน"
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
        #                 "uri": "https://kmitldev-blood-link.netlify.app/profile/1"
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
        #                 "uri": "https://kmitldev-blood-link.netlify.app"
        #             }
        #         }
        #     ]
        # }

        # response = requests.post(url, headers=headers, json=data)

        # rich_menu_id = response.json().get("richMenuId")
        # print(f"Status Code: {response.status_code}")
        # print(f"Response: {rich_menu_id}")


        # 2
        # image_path = os.path.join(settings.BASE_DIR, "static", "LINE rich menu.png")

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
        # url = f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}"
        # headers = {
        #     "Authorization": f"Bearer {channel_access_token}"
        # }

        # response = requests.post(url, headers=headers)

        # print(f"Status Code: {response.status_code}")
        # print(f"Response: {response.text}")
