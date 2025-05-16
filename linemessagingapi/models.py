from django.db import models
from accounts.models import Users
from django.utils import timezone
import secrets

class WebhookRequest(models.Model):
    method = models.CharField(max_length=10)  # Stores the request method (e.g., POST, GET)
    path = models.CharField(max_length=255)  # Stores the request path (e.g., /line/)
    headers = models.JSONField()  # Stores the request headers in JSON format
    body = models.TextField()  # Stores the raw request body
    received_at = models.DateTimeField(auto_now_add=True)  # Stores the timestamp when the webhook was received

    def __str__(self):
        return f"Webhook {self.method} {self.path} at {self.received_at}"
    
class LineChannel(models.Model): #เก็บ channel access เพราะมี LINE bot หลายตัว
    nickname             = models.CharField(blank=True, max_length=50) #BloodLink1, BloodLink2...
    bot_id               = models.CharField(blank=True, max_length=50) # @210opltx
    channel_id           = models.CharField(max_length=50, db_index=True)
    channel_access_token = models.TextField(blank=True, max_length=200)
    channel_secret       = models.CharField(max_length=50)

    created_on           = models.DateTimeField(auto_now_add=True)
    updated_on           = models.DateTimeField(auto_now=True)
    active               = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nickname} {self.bot_id}"
        
class LineChannelContact(models.Model):
    channel = models.ForeignKey(LineChannel, related_name='line_channel_contacts', on_delete=models.CASCADE)
    contact_id = models.CharField(max_length=50, db_index=True, unique=True)
    user = models.ForeignKey(Users, related_name='line_channel_contacts', on_delete=models.SET_NULL, null=True, blank=True)
    display_name = models.CharField(blank=True, max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name} {self.contact_id}"
    
# class LineUserTokenMapping(models.Model):
#     token = models.CharField(max_length=64, unique=True)
#     line_user_id = models.CharField(max_length=255, blank=True, null=True)  # Populated after follow event
#     created_on = models.DateTimeField(default=timezone.now)

def generate_nonce():
    return secrets.token_urlsafe(16)  # 16-byte random string
def generate_state():
    return secrets.token_urlsafe(16)

class NonceMapping(models.Model):
    nonce = models.CharField(max_length=255, unique=True, default=generate_nonce)
    state = models.CharField(max_length=255, unique=True, default=generate_state)
    redirect_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nonce} {self.state} {self.redirect_path}"
        # return self.nonce
