from rest_framework.views import APIView
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework import status
from linebot import LineBotApi
from linebot.models import TextSendMessage, ButtonsTemplate, TemplateSendMessage, URITemplateAction, FlexSendMessage
from linemessagingapi.models import LineChannelContact, LineChannel, WebhookRequest, NonceMapping
from accounts.models import Users
from accounts.serializers import UserSerializer
from webapp.models import DonationLocation, Post
from django.db.models import Q
import requests

from django.db.models.signals import post_save
from django.dispatch import receiver

from linemessagingapi.services.nearest_location import calculate_haversine_distance

from jwt import decode, ExpiredSignatureError, InvalidTokenError

# from rest_framework.authentication import TokenAuthentication

# from django.shortcuts import redirect
# from django.http import HttpResponse

class Webhook(APIView):
    # authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [permissions.AllowAny]  # Allow anyone to access this view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize LineBot instance
        self.line_bot = LineChannel.objects.get(id=1) # now have only one bot so declare static
        self.line_bot_api = LineBotApi(self.line_bot.channel_access_token)

    def post(self, request, *args, **kwargs):
        self.store_webhook_data(request)
        # Process incoming webhook events
        events = request.data.get('events')
        if not isinstance(events, list):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Process each event and send messages to LINE
        for event in events:
            if event['type'] == 'message':
                self.handle_message_event(event)
            elif event['type'] == 'follow':
                self.handle_follow_event(event)
            # elif event['type'] == 'accountLink':  # Handle account linking event
            #     self.handle_account_link_event(event)

        return Response(status=status.HTTP_200_OK)
    
    def get(self, request, *args, **kwargs):
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        if not code or not state:
            return Response({'error': 'Authorization code or state is missing'}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange the authorization code for an access token
        token_url = "https://api.line.me/oauth2/v2.1/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://secretly-coherent-lacewing.ngrok-free.app/line",
            "client_id": "2006630011",
            "client_secret": "2b7ad148dcbb206e8a9aeb281d36022b",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            token_response = requests.post(token_url, data=data, headers=headers)
            token_response.raise_for_status()
            token_data = token_response.json()
        except requests.RequestException as e:
            return Response({'error': 'Failed to exchange code for token', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Decode the ID token to get LINE user info
        id_token = token_data.get('id_token')
        try:
            decoded_token = decode(id_token, options={"verify_signature": False})  # Add verification in production
            line_user_id = decoded_token.get('sub')
            email = decoded_token.get("email")
        except (ExpiredSignatureError, InvalidTokenError) as e:
            return Response({'error': 'Invalid or expired ID token'}, status=status.HTTP_400_BAD_REQUEST)

        if not line_user_id:
            return Response({'error': 'LINE user ID not found in token'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the LINE user ID exists in the database
        try:
            user = Users.objects.get(line_user_id=line_user_id)
            # Log the user in (use your authentication mechanism here)
            return Response({'message': 'User logged in', 'user_id': user.id, 'user_email': email}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            # If user does not exist, redirect to registration
            serializer = UserSerializer(data={
                'line_user_id': line_user_id,
                'email': email
            })
            if serializer.is_valid():
                user = serializer.save()
                return Response({'message': 'User registered successfully', 'user_email': user.email}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_message_event(self, event):
        user_id = event['source']['userId']
        reply_token = event['replyToken']
        message_type = event['message']['type']

        if message_type == 'text':
            message_text = event['message']['text']
            if message_text == 'บริจาคโลหิตใกล้ฉัน':
                self.send_location_request(reply_token)

        elif message_type == 'location':
            # Get user's latitude and longitude
            user_lat = event['message']['latitude']
            user_lon = event['message']['longitude']

            # Find donation locations within 10km of the user's location
            nearby_locations = []
            donation_locations = DonationLocation.objects.all()

            for location in donation_locations:
                if location.latitude != None and location.longitude != None:
                    distance = calculate_haversine_distance(user_lat, user_lon, location.latitude, location.longitude)
                    # If the location is within 10km, add it to the nearby locations list
                    if distance <= 10:
                        bubble_template = self.create_location_bubble(location.name, distance, location.address, location.googlemap)
                        nearby_locations.append(bubble_template)

            # If there are nearby locations, send them in a single Flex message
            if nearby_locations:
                flex_message = FlexSendMessage(
                    alt_text="บริจาคโลหิตใกล้ฉัน",
                    contents={
                        "type": "carousel",
                        "contents": nearby_locations  # Send all bubbles as a carousel
                    }
                )
                self.line_bot_api.reply_message(reply_token, flex_message)
            else:
                # If no nearby locations are found, send a text message
                message = TextSendMessage(text="ไม่พบสถานที่บริจาคโลหิตใกล้คุณภายใน 10 กิโลเมตร")
                self.line_bot_api.reply_message(reply_token, message)

    def handle_follow_event(self, event):
        user_id = event['source']['userId']
        
        display_name = self.get_line_display_name(user_id)
        channel = self.line_bot
        
        LineChannelContact.objects.get_or_create(
            channel=channel,
            contact_id=user_id,
            defaults={'display_name': display_name}
        )

        # 1. Get the link token for this user
        link_token = self.get_link_token(user_id)

        # 2. Send the linking URL to the user
        if link_token:
            linking_url = f"http://localhost:5173/link?linkToken={link_token}"
            buttons_template = ButtonsTemplate(
                title='ลิ้งแอคเคาท์',
                text='กดเพื่อลิ้งแอคเคาท์',
                actions=[
                    URITemplateAction(
                        label='ลิ้งแอคเคาท์',
                        uri=linking_url
                    )
                ]
            )
            template_message = TemplateSendMessage(
                alt_text='ลิ้งแอคเคาท์',
                template=buttons_template
            )
            self.line_bot_api.push_message(user_id, template_message)

    def get_link_token(self, user_id):
        # Request the link token from the LINE platform
        response = requests.post(
            f"https://api.line.me/v2/bot/user/{user_id}/linkToken",
            headers={'Authorization': f'Bearer {self.line_bot.channel_access_token}'}
        )
        if response.status_code == 200:
            return response.json().get('linkToken')
        return None
    
    def handle_account_link_event(self, event):
        # Extract the necessary details from the event
        line_user_id = event['source']['userId']
        nonce = event['link']['nonce']
        
        # Find the user in your system based on the nonce
        try:
            # Assuming you have a model that stores the nonce and user ID
            nonce_mapping = NonceMapping.objects.get(nonce=nonce)
            user = nonce_mapping.user  # Get the associated user

            # Save the LINE user ID to the user's profile
            user.line_user_id = line_user_id
            user.save()

            line_channel_contact = LineChannelContact.objects.get(contact_id=line_user_id)
            line_channel_contact.user = user
            line_channel_contact.save()
            
            # Clean up the nonce mapping (optional)
            nonce_mapping.delete()

            print(f"Linked LINE account {line_user_id} with user {user.email}")

        except NonceMapping.DoesNotExist:
            print(f"Nonce {nonce} not found, unable to link account.")



    def get_line_display_name(self, user_id):
        """
        Call LINE API to get the display name of the user.
        """
        url = f"https://api.line.me/v2/bot/profile/{user_id}"
        headers = {
            "Authorization": f"Bearer {self.line_bot.channel_access_token}"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("displayName", "Unknown User")  # Return the display name or a default
            else:
                print(f"Error fetching display name: {response.status_code} {response.text}")
                return "Unknown User"
        except Exception as e:
            print(f"Exception occurred: {e}")
            return "Unknown User"
        
    def send_location_request(self, reply_token):
        buttons_template = ButtonsTemplate(
            title='แชร์ตำแหน่ง',
            text='กรุณาเลือกเพื่อแชร์ตำแหน่งของคุณ',
            actions=[
                URITemplateAction(
                    label='แชร์ตำแหน่ง',
                    uri='line://nv/location'  # Native location sharing
                )
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='แชร์ตำแหน่ง',
            template=buttons_template
        )
        self.line_bot_api.reply_message(reply_token, template_message)

    def create_location_bubble(self, loc_name, loc_distance, loc_address, map_url):
        bubble_template = {
            "type": "bubble",
            "direction": "ltr",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "lg",
                        "margin": "none",
                        "contents": [
                            {
                                "type": "text",
                                "text": loc_name,
                                "weight": "bold",
                                "align": "start",
                                "wrap": True,
                                "contents": []
                            },
                            {
                                "type": "text",
                                "text": f"อยู่ห่างจากคุณ {loc_distance} กม.",
                                "margin": "none",
                                "wrap": True,
                                "contents": []
                            },
                            {
                                "type": "text",
                                "text": f"🚩 {loc_address}",
                                "align": "start",
                                "margin": "none",
                                "wrap": True,
                                "contents": []
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูบนแผนที่",
                            "uri": map_url
                        },
                        "color": "#B6ABA0",
                        "style": "primary"
                    }
                ]
            }
        }
        return bubble_template
    
    def store_webhook_data(self, request):
        # Extract method, path, headers, and body
        method = request.method
        path = request.path
        headers = dict(request.headers)  # Convert headers to a dictionary
        body = request.body.decode('utf-8')  # Get raw body as a string

        # Save the webhook request data to the database
        WebhookRequest.objects.create(
            method=method,
            path=path,
            headers=headers,
            body=body
        )
        


@receiver(post_save, sender=Post)
def notify_users_on_post_creation(sender, instance, created, **kwargs):
    if created and instance.show:  # Check if it's a new post and it's meant to be shown
        post_subdistrict = instance.location.subdistrict
        post_district = post_subdistrict.district
        post_province = post_district.province

        # Find users whose preferred areas match the post location
        users_to_notify = Users.objects.filter(
            Q(preferred_areas__subdistricts=post_subdistrict) |
            Q(preferred_areas__districts=post_district) |
            Q(preferred_areas__provinces=post_province)
        ).distinct()

        # Initialize Webhook once to reuse it in the loop
        webhook = Webhook()

        # Notify each user via LINE
        for user in users_to_notify:
            if user.line_user_id:  # Ensure the user has linked their LINE account
                flex_message = {
                    "type": "bubble",
                    "size": "mega",
                    "direction": "ltr",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "none",
                        "margin": "none",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🆘 ด่วน! ขอรับบริจาคโลหิตฉุกเฉิน 🆘",
                                "weight": "regular",
                                "align": "start",
                                "margin": "none",
                                "contents": []
                            },
                            {
                                "type": "text",
                                "text": f"หมู่เลือดที่ต้องการ: {instance.recipient_blood_type}",
                                "align": "start",
                                "gravity": "center",
                                "margin": "xl",
                                "contents": []
                            },
                            {
                                "type": "text",
                                "text": f"สถานที่: {instance.location.name}",
                                "contents": [],
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": "ขอบคุณที่ร่วมช่วยเหลือ!",
                                "margin": "xxl",
                                "contents": []
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "none",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "ดูรายละเอียดโพสต์",
                                    "uri": f"https://yourwebsite.com/post/{instance.id}"
                                },
                                "color": "#DC0404",
                                "style": "primary"
                            }
                        ]
                    }
                }
                # message = TextSendMessage(text=message_text)
                message = FlexSendMessage(alt_text="ขอรับบริจาคโลหิต", contents=flex_message)
                webhook.line_bot_api.push_message(user.line_user_id, message)


@receiver(post_save, sender=Post)
def notify_user_on_post_creation(sender, instance, created, **kwargs):
    if created :

        # Initialize Webhook once to reuse it in the loop
        webhook = Webhook()

        if instance.user.line_user_id:  # Ensure the user has linked their LINE account
            flex_message = {
                "type": "bubble",
                "size": "mega",
                "direction": "ltr",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "none",
                    "margin": "none",
                    "contents": [
                        {
                            "type": "text",
                            "text": "สร้างโพสต์ขอรับบริจาคโลหิตฉุกเฉินสำเร็จ",
                            "weight": "regular",
                            "align": "start",
                            "margin": "none",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": f"หมู่เลือดที่ต้องการ: {instance.recipient_blood_type}",
                            "align": "start",
                            "gravity": "center",
                            "margin": "xl",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": f"สถานที่: {instance.location.name}",
                            "contents": [],
                            "wrap": True
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "none",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "ดูรายละเอียดโพสต์",
                                "uri": f"https://yourwebsite.com/post/{instance.id}"
                            },
                            "color": "#DC0404",
                            "style": "primary"
                        }
                    ]
                }
            }
            # message = TextSendMessage(text=message_text)
            message = FlexSendMessage(alt_text="ขอรับบริจาคโลหิต", contents=flex_message)
            webhook.line_bot_api.push_message(instance.user.line_user_id, message)
