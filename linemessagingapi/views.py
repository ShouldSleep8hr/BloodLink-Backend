from rest_framework.views import APIView
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework import status
from linebot import LineBotApi
from linebot.models import TextSendMessage, ButtonsTemplate, TemplateSendMessage, URITemplateAction, FlexSendMessage
from linemessagingapi.models import LineChannelContact, LineChannel, WebhookRequest, NonceMapping
from accounts.models import Users
from accounts.serializers import UserSerializer
from webapp.models import DonationLocation, Post, DonationHistory
from django.db.models import Q
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import quote_plus

from django.db.models.signals import post_save
from django.dispatch import receiver
from webapp.views import post_interested, donation_verified
from webapp.serializers import post_donated

from linemessagingapi.services.nearest_location import calculate_haversine_distance

from jwt import decode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime
import os
# from rest_framework_simplejwt.tokens import RefreshToken
# from urllib.parse import urlencode

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
    
    # def get(self, request, *args, **kwargs):
    #     code = request.query_params.get('code')
    #     state = request.query_params.get('state')

    #     if not code or not state:
    #         return Response({'error': 'Authorization code or state is missing'}, status=status.HTTP_400_BAD_REQUEST)

    #     # Validate state to prevent CSRF attacks
    #     saved_state = request.session.pop('line_login_state', None)  # Retrieve and remove state from session
    #     if saved_state != state:
    #         return Response({'error': 'Invalid state parameter'}, status=status.HTTP_400_BAD_REQUEST)

    #     # Exchange the authorization code for an access token
    #     token_url = "https://api.line.me/oauth2/v2.1/token"
        
    #     data = {
    #         "grant_type": "authorization_code",
    #         "code": code,
    #         "redirect_uri": "https://bloodlink.up.railway.app/line",
    #         "client_id": os.getenv('CLIENT_ID'),
    #         "client_secret": os.getenv('CLIENT_SECRET'),
    #     }
    #     if not data["client_id"] or not data["client_secret"]:
    #         raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in the environment.")
        
    #     headers = {"Content-Type": "application/x-www-form-urlencoded"}

    #     try:
    #         token_response = requests.post(token_url, data=data, headers=headers)
    #         token_response.raise_for_status()
    #         token_data = token_response.json()
    #     except requests.RequestException as e:
    #         return Response({'error': 'Failed to exchange code for token', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #     # Decode the ID token to get LINE user info
    #     id_token = token_data.get('id_token')
    #     access_token = token_data.get('access_token')

    #     if not id_token or not access_token:
    #         return Response({'error': 'Missing tokens in response'}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         decoded_token = decode(id_token, options={"verify_signature": False})  # Add verification in production
    #         line_user_id = decoded_token.get('sub')
    #         email = decoded_token.get("email")
    #     except (ExpiredSignatureError, InvalidTokenError) as e:
    #         return Response({'error': 'Invalid or expired ID token'}, status=status.HTTP_400_BAD_REQUEST)

    #     if not line_user_id:
    #         return Response({'error': 'LINE user ID not found in token'}, status=status.HTTP_400_BAD_REQUEST)

    #     profile_url = "https://api.line.me/v2/profile"
    #     profile_headers = {"Authorization": f"Bearer {access_token}"}

    #     try:
    #         profile_response = requests.get(profile_url, headers=profile_headers)
    #         profile_response.raise_for_status()
    #         profile_data = profile_response.json()

    #         picture_url = profile_data.get("pictureUrl")
    #         display_name = profile_data.get("displayName")
    #     except requests.RequestException as e:
    #         display_name = None
    #         picture_url = None

    #     try:
    #         # Check if user exists, update profile picture if needed
    #         user, created = Users.objects.update_or_create(
    #             line_user_id=line_user_id,
    #             defaults={
    #                 'email': email,
    #                 'line_username': display_name,
    #                 'profile_picture': picture_url,  # Refresh profile picture every login
    #             }
    #         )

    #         # Generate JWT tokens
    #         refresh = RefreshToken.for_user(user)
    #         tokens = { 'refresh': str(refresh), 'access': str(refresh.access_token), }

    #         return Response({
    #             'message': 'User logged in' if not created else 'User registered successfully',
    #             'user_id': user.id,
    #             'user_email': user.email,
    #             'line_username': user.line_username,
    #             'profile_picture': user.profile_picture,
    #             'tokens': tokens,
    #         }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
    #     except Exception as e:
    #         return Response({'error': 'Failed to update or create user', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def handle_message_event(self, event):
        user_id = event['source']['userId']
        reply_token = event['replyToken']
        message_type = event['message']['type']

        if message_type == 'text':
            message_text = event['message']['text']
            if message_text == 'บริจาคโลหิตใกล้ฉัน':
                self.send_location_request(reply_token)
            # elif message_text == 'บันทึกการบริจาคโลหิต':
            #     self.send_saving_donation_with_auth(reply_token, user_id)

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
                        # Check and construct the valid URL
                        if location.name:
                            googlemap = f"https://maps.google.com/?q={quote_plus(location.name)}"
                        else:
                            googlemap = "https://kmitldev-blood-link.netlify.app"
                        bubble_template = self.create_location_bubble(location.name, distance, location.address, googlemap)
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

        try:
            # Check if the user exists in your Users model
            user = Users.objects.get(line_user_id=user_id)
            display_name = user.line_username
        except ObjectDoesNotExist:
            # If user does not exist, set user and display_name to None
            user = None
            display_name = None
        except Exception as e:
            # Log unexpected errors
            print(f"Unexpected error: {e}")
            return HttpResponse(status=500)  # Internal Server Error

        channel = self.line_bot

        # Update or create LineChannelContact
        LineChannelContact.objects.update_or_create(
            channel=channel,
            contact_id=user_id,
            user = user, # This can now be None
            defaults={'display_name': display_name}
        )

        return HttpResponse(status=200)

    #     # 1. Get the link token for this user
    #     link_token = self.get_link_token(user_id)

    #     # 2. Send the linking URL to the user
    #     if link_token:
    #         linking_url = f"http://localhost:5173/link?linkToken={link_token}"
    #         buttons_template = ButtonsTemplate(
    #             title='ลิ้งแอคเคาท์',
    #             text='กดเพื่อลิ้งแอคเคาท์',
    #             actions=[
    #                 URITemplateAction(
    #                     label='ลิ้งแอคเคาท์',
    #                     uri=linking_url
    #                 )
    #             ]
    #         )
    #         template_message = TemplateSendMessage(
    #             alt_text='ลิ้งแอคเคาท์',
    #             template=buttons_template
    #         )
    #         self.line_bot_api.push_message(user_id, template_message)

    # def get_link_token(self, user_id):
    #     # Request the link token from the LINE platform
    #     response = requests.post(
    #         f"https://api.line.me/v2/bot/user/{user_id}/linkToken",
    #         headers={'Authorization': f'Bearer {self.line_bot.channel_access_token}'}
    #     )
    #     if response.status_code == 200:
    #         return response.json().get('linkToken')
    #     return None
    
    # def handle_account_link_event(self, event):
    #     # Extract the necessary details from the event
    #     line_user_id = event['source']['userId']
    #     nonce = event['link']['nonce']
        
    #     # Find the user in your system based on the nonce
    #     try:
    #         # Assuming you have a model that stores the nonce and user ID
    #         nonce_mapping = NonceMapping.objects.get(nonce=nonce)
    #         user = nonce_mapping.user  # Get the associated user

    #         # Save the LINE user ID to the user's profile
    #         user.line_user_id = line_user_id
    #         user.save()

    #         line_channel_contact = LineChannelContact.objects.get(contact_id=line_user_id)
    #         line_channel_contact.user = user
    #         line_channel_contact.save()
            
    #         # Clean up the nonce mapping (optional)
    #         nonce_mapping.delete()

    #         print(f"Linked LINE account {line_user_id} with user {user.email}")

    #     except NonceMapping.DoesNotExist:
    #         print(f"Nonce {nonce} not found, unable to link account.")

    # def get_line_display_name(self, user_id):
    #     """
    #     Call LINE API to get the display name of the user.
    #     """
    #     url = f"https://api.line.me/v2/bot/profile/{user_id}"
    #     headers = {
    #         "Authorization": f"Bearer {self.line_bot.channel_access_token}"
    #     }
    #     try:
    #         response = requests.get(url, headers=headers)
    #         if response.status_code == 200:
    #             data = response.json()
    #             return data.get("displayName", "Unknown User")  # Return the display name or a default
    #         else:
    #             print(f"Error fetching display name: {response.status_code} {response.text}")
    #             return "Unknown User"
    #     except Exception as e:
    #         print(f"Exception occurred: {e}")
    #         return "Unknown User"
        
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
    
    # def send_saving_donation_with_auth(self, reply_token, user_id):
    #     try:
    #         user = Users.objects.get(line_user_id=user_id)
    #     except Users.DoesNotExist:
    #         print(f"User with line_user_id {user_id} not found.")
    #         return

    #     refresh = RefreshToken.for_user(user)
    #     access_token = str(refresh.access_token)

    #     frontend_url = "https://kmitldev-blood-link.netlify.app/line/donation-submission"
    #     query_params = {"access": access_token, "refresh": str(refresh)}

    #     redirect_url = f"{frontend_url}?{urlencode(query_params)}"

    #     buttons_template = ButtonsTemplate(
    #         title='บันทึกการบริจาคโลหิต',
    #         text='กดเพื่อไปหน้าบันทึกการบริจาคโลหิตของคุณ',
    #         actions=[
    #             URITemplateAction(
    #                 label='บันทึกการบริจาคโลหิต',
    #                 uri=redirect_url
    #             )
    #         ]
    #     )
    #     template_message = TemplateSendMessage(
    #         alt_text='บันทึกการบริจาคโลหิต',
    #         template=buttons_template
    #     )
    #     self.line_bot_api.reply_message(reply_token, template_message)
    
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
    if created and instance.show and instance.location:  # Check if it's a new post and it's meant to be shown
        post_subdistrict = instance.location.subdistrict
        post_district = post_subdistrict.district
        post_province = post_district.province

        # Find users whose preferred areas match the post location
        # users_to_notify = Users.objects.filter(
        #     Q(preferred_areas__district=post_district) |
        #     Q(preferred_areas__province=post_province)
        # ).distinct()
        users_to_notify = Users.objects.filter(
            Q(preferred_areas__district__id=post_district.id) |
            Q(preferred_areas__province__id=post_province.id)
        ).exclude(id=instance.user.id).distinct()

        # Initialize Webhook once to reuse it in the loop
        webhook = Webhook()

        # Notify each user via LINE
        for user in users_to_notify:
            if user.line_user_id:  # Ensure the user has linked their LINE account
                thai_year = instance.due_date.year + 543
                # Format the date as "day/month/year" with the full Thai year
                date_only = instance.due_date.strftime(f'%d/%m/{thai_year}')
                flex_message = {
                    "type": "bubble",
                    "size": "mega",
                    "direction": "ltr",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "🆘ด่วน!ขอรับบริจาคโลหิตฉุกเฉิน🆘", "weight": "bold", 'wrap': True},
                            {"type": "text", "text": f"{instance.recipient_name}", "margin": "xl", 'wrap': True},
                            {"type": "text", "text": f"หมู่เลือดที่ต้องการ: {instance.recipient_blood_type}", 'wrap': True},
                            {"type": "text", "text": f"สถานที่: {instance.location.name if instance.location else instance.new_address}", 'wrap': True},
                            {"type": "text", "text": f"บริจาคได้ถึง: {date_only}", 'wrap': True},
                            {"type": "text", "text": f"ขอบคุณที่ร่วมช่วยเหลือ!", "margin": "xxl", 'wrap': True},
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
                                    "label": "ดูรายละเอียดโพสต์",
                                    "uri": f"https://kmitldev-blood-link.netlify.app/post/{instance.id}"
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
            thai_year = instance.due_date.year + 543
            # Format the date as "day/month/year" with the full Thai year
            date_only = instance.due_date.strftime(f'%d/%m/{thai_year}')
            flex_message = {
                "type": "bubble",
                "size": "mega",
                "direction": "ltr",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "สร้างโพสต์สำเร็จ", "weight": "bold", "wrap": True},
                        {"type": "text", "text": f"{instance.recipient_name}", "margin": "xl", "wrap": True},
                        {"type": "text", "text": f"หมู่เลือดที่ต้องการ: {instance.recipient_blood_type}", "wrap": True},
                        {"type": "text", "text": f"สถานที่: {instance.location.name if instance.location else instance.new_address}", "wrap": True},
                        {"type": "text", "text": f"บริจาคได้ถึง: {date_only}", "margin": "xxl", "wrap": True},
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
                                "label": "ดูโพสต์ทั้งหมดของคุณ",
                                "uri": f"https://kmitldev-blood-link.netlify.app/profile"
                            },
                            "color": "#DC0404",
                            "style": "primary"
                        }
                    ]
                }
            }

            # message = TextSendMessage(text=message_text)
            message = FlexSendMessage(alt_text="สร้างโพสต์ขอรับบริจาคโลหิตสำเร็จ", contents=flex_message)
            webhook.line_bot_api.push_message(instance.user.line_user_id, message)

@receiver(post_interested, sender=Post)
def notify_user_post_interested(sender, instance, interested_by, **kwargs):
    """Notify the user that press interested in post."""
    
    # Ensure the user has linked their LINE account
    if interested_by.line_user_id:
        webhook = Webhook()  # Initialize webhook

        thai_year = instance.due_date.year + 543
        # Format the date as "day/month/year" with the full Thai year
        date_only = instance.due_date.strftime(f'%d/%m/{thai_year}')

        # Check and construct the valid URL
        if instance.location and instance.location.name:
            googlemap = f"https://maps.google.com/?q={quote_plus(instance.location.name)}"
        elif instance.new_address:
            googlemap = f"https://maps.google.com/?q={quote_plus(instance.new_address)}"
        else:
            googlemap = "https://kmitldev-blood-link.netlify.app"

        flex_message = {
            "type": "bubble",
            "size": "mega",
            "direction": "ltr",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "โพสต์ที่คุณกดสนใจ", "weight": "bold", "wrap": True},
                    {"type": "text", "text": f"{instance.recipient_name}", "margin": "xl", "wrap": True},
                    {"type": "text", "text": f"หมู่เลือดที่ต้องการ: {instance.recipient_blood_type}", "wrap": True},
                    {"type": "text", "text": f"สถานที่: {instance.location.name if instance.location else instance.new_address}", "wrap": True},
                    {"type": "text", "text": f"บริจาคได้ถึง: {date_only}", "wrap": True},
                    {"type": "text", "text": f"ขอบคุณที่สนใจร่วมช่วยเหลือ!", "margin": "xxl", "wrap": True},
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
                            "uri": googlemap
                        },
                        "color": "#DC0404",
                        "style": "primary"
                    }
                ]
            }
        }
        

        message = FlexSendMessage(alt_text="โพสต์บริจาคโลหิตฉุกเฉินที่คุณกดสนใจ", contents=flex_message)
        webhook.line_bot_api.push_message(interested_by.line_user_id, message)


@receiver(post_donated, sender=Post)
def notify_user_on_post_donation(sender, instance, donated_by, **kwargs):
    """Notify the post owner when someone has donated blood in their post."""
    
    # Ensure the user has linked their LINE account
    if instance.user.line_user_id:
        webhook = Webhook()  # Initialize webhook

        thai_year = instance.due_date.year + 543
        # Format the date as "day/month/year" with the full Thai year
        date_only = instance.due_date.strftime(f'%d/%m/{thai_year}')

        flex_message = {
            "type": "bubble",
            "size": "mega",
            "direction": "ltr",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "มีผู้บริจาคโลหิตให้โพสต์ของคุณ!", "weight": "bold", "wrap": True},
                    {"type": "text", "text": f"{donated_by.full_name}", "margin": "xl", "wrap": True},
                    {"type": "text", "text": f"บริจาคให้กับ {instance.recipient_name}", "wrap": True},
                    {"type": "text", "text": f"มีคนบริจาคให้ทั้งหมด {instance.number_donor} คน", "wrap": True},
                    {"type": "text", "text": f"บริจาคได้ถึง: {date_only}", "wrap": True},
                    {"type": "text", "text": f"ยินดีด้วยกับความช่วยเหลือ!", "margin": "xxl", "wrap": True},
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
                            "label": "ดูโพสต์ทั้งหมดของคุณ",
                            "uri": f"https://kmitldev-blood-link.netlify.app/profile"
                        },
                        "color": "#DC0404",
                        "style": "primary"
                    }
                ]
            }
        }
        

        message = FlexSendMessage(alt_text="มีผู้บริจาคโลหิตให้โพสต์ของคุณ", contents=flex_message)
        webhook.line_bot_api.push_message(instance.user.line_user_id, message)


@receiver(donation_verified, sender=DonationHistory)
def notify_user_on_donation_verification(sender, instance, **kwargs):
    # Initialize Webhook once to reuse it in the loop
    webhook = Webhook()

    if instance.user.line_user_id:  # Ensure the user has linked their LINE account
        thai_year = instance.donation_date.year + 543
        # Format the date as "day/month/year" with the full Thai year
        date_only = instance.donation_date.strftime(f'%d/%m/{thai_year}')
        user_score = instance.user.score + instance.donation_point
        flex_message = {
            "type": "bubble",
            "size": "mega",
            "direction": "ltr",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "ยินดีด้วย! บันทึกบริจาคโลหิตของคุณผ่านการตรวจสอบ", "weight": "bold", "wrap": True},
                    {"type": "text", "text": f"บริจาคเมื่อวันที่: {date_only}", "margin": "xl", "wrap": True},
                    {"type": "text", "text": f"ได้รับคะแนน: {instance.donation_point} คะแนน", "wrap": True},
                    {"type": "text", "text": f"คุณมีคะแนนรวม {user_score} คะแนน", "margin": "xxl", "wrap": True},
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
                            "label": "ดูประวัติการบริจาคของคุณ",
                            "uri": f"https://kmitldev-blood-link.netlify.app/history"
                        },
                        "color": "#DC0404",
                        "style": "primary"
                    }
                ]
            }
        }
        
        # message = TextSendMessage(text=message_text)
        message = FlexSendMessage(alt_text="บันทึกบริจาคโลหิตของคุณผ่าน", contents=flex_message)
        webhook.line_bot_api.push_message(instance.user.line_user_id, message)
