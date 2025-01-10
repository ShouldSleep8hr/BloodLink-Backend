from django.contrib import admin

from linemessagingapi.models import WebhookRequest, LineChannel, LineChannelContact, NonceMapping

admin.site.register(WebhookRequest)
admin.site.register(LineChannel)
admin.site.register(LineChannelContact)
admin.site.register(NonceMapping)