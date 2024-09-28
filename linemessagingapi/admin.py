from django.contrib import admin

from linemessagingapi.models import WebhookRequest, LineChannel, LineChannelContact

admin.site.register(WebhookRequest)
admin.site.register(LineChannel)
admin.site.register(LineChannelContact)