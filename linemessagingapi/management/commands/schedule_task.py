# for post expired LINE noti and remind user to donate blood
from django.core.management.base import BaseCommand
from accounts.models import Users
from webapp.models import Post
from django.db.models import Q
from linemessagingapi.views import Webhook
from linebot.models import TextSendMessage, ButtonsTemplate, TemplateSendMessage, URITemplateAction, FlexSendMessage
from linemessagingapi.models import LineChannel
from linebot import LineBotApi
import os

from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            # def notify_users_on_post_expired():
            # line_bot = LineChannel.objects.get(id=1)
            line_bot_api = LineBotApi(os.getenv('BOT_CHANNEL_ACCESS_TOKEN'))

            now = timezone.now().date()  # Get today's date
            two_days_before = now + timedelta(days=2)
            one_day_before = now + timedelta(days=1)

            posts = Post.objects.filter(
                due_date__date__in=[two_days_before, one_day_before]
            ).select_related("user")

            for post in posts:
                if not post.user or not post.user.line_user_id:  # Ensure user exists & has LINE ID
                    print(f"Skipping post {post.id}: Missing user or LINE ID")
                    continue
                days_left = (post.due_date.date() - now).days
                if days_left not in [1, 2]:  # Double-check valid days
                    continue

                time_notice = str(days_left)
                recipient_name = post.recipient_name or "ไม่ระบุชื่อ"

                thai_year = post.due_date.year + 543
                # Format the date as "day/month/year" with the full Thai year
                date_only = post.due_date.strftime(f'%d/%m/{thai_year}')
                
                flex_message = {
                    "type": "bubble",
                    "size": "mega",
                    "direction": "ltr",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "แจ้งเตือนหมดอายุโพสต์", "weight": "bold"},
                            {"type": "text", "text": f"{recipient_name}", "margin": "xl"},
                            {"type": "text", "text": f"จะหมดภายในวันที่ {date_only}"},
                            {"type": "text", "text": f"เหลือเวลาอีก {time_notice} วัน", "margin": "xxl"},
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
                                    "uri": f"https://bloodlink.up.railway.app/user/post/{post.id}"
                                },
                                "color": "#DC0404",
                                "style": "primary"
                            }
                        ]
                    }
                }
                
                try:
                    message = FlexSendMessage(alt_text="แจ้งเตือนหมดอายุโพสต์", contents=flex_message)
                    # print(f"Sending message to {post.user.line_user_id}: {flex_message}")  # Debugging
                    line_bot_api.push_message(post.user.line_user_id, message)
                except Exception as e:
                    print(f"Error sending message for post {post.id}: {e}")

        except Exception as e:
            print(f"Error in notify_upcoming_due_date(): {e}")

        try:
            line_bot = LineChannel.objects.get(id=1)
            line_bot_api = LineBotApi(line_bot.channel_access_token)

            # now = timezone.now().date()  # Get today's date
            # three_months_ago = now - timedelta(days=90)  # Approximate 3 months

            # users = Users.objects.filter(
            #     latest_donation_date__lte=three_months_ago,  # Users who donated 3+ months ago
            #     line_user_id__isnull=False  # Ensure they have a LINE ID
            # )
            now = timezone.now().date()
            three_months_ago = now - timedelta(days=90)  # Users eligible today
            two_days_before_three_months = now - timedelta(days=88)  # Users eligible 2 days before

            users = Users.objects.filter(
                latest_donation_date__in=[three_months_ago, two_days_before_three_months],  # Match exact dates
                line_user_id__isnull=False  # Ensure they have a LINE ID
            )

            for user in users:
                # last_donation = user.latest_donation_date or "ไม่ระบุวันที่"
                thai_year = user.latest_donation_date.year + 543
                last_donation = user.latest_donation_date.strftime(f'%d/%m/{thai_year}')

                if user.latest_donation_date == three_months_ago:
                    reminder_text = "คุณสามารถบริจาคโลหิตได้อีกครั้ง"
                    highlight_text = "ครบ 3 เดือนแล้ว!"
                else:
                    reminder_text = "คุณสามารถบริจาคโลหิตได้ในอีก 2 วัน"
                    highlight_text = "ใกล้ครบ 3 เดือนแล้ว!"
                
                flex_message = {
                    "type": "bubble",
                    "size": "mega",
                    "direction": "ltr",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "แจ้งเตือนรอบการบริจาคโลหิต", "weight": "bold"},
                            {"type": "text", "text": reminder_text, "margin": "xl"},
                            {"type": "text", "text": f"บริจาคครั้งล่าสุด: {last_donation}"},
                            {"type": "text", "text": highlight_text, "margin": "xxl"},
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    # "type": "uri",
                                    # "label": "ดูจุดรับบริจาคใกล้คุณ",
                                    # "uri": "https://kmitldev-blood-link.netlify.app"
                                    "type": "message",
                                    "label": "ดูจุดรับบริจาคใกล้คุณ",
                                    "text": "บริจาคโลหิตใกล้ฉัน"
                                },
                                "color": "#DC0404",
                                "style": "primary"
                            }
                        ]
                    }
                }

                try:
                    message = FlexSendMessage(alt_text="แจ้งเตือนรอบการบริจาคโลหิต", contents=flex_message)
                    line_bot_api.push_message(user.line_user_id, message)
                except Exception as e:
                    print(f"Error sending message to {user.id}: {e}")

        except Exception as e:
            print(f"Error in notify_users_for_blood_donation(): {e}")