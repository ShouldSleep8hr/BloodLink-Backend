# from rest_framework import serializers
# from .models import LineMessage

# class LineMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LineMessage
#         fields = ['id', 'user', 'message', 'reply_token', 'message_type', 'timestamp', 'sent_by_user']
#         read_only_fields = ['id', 'timestamp']  # These fields should not be modified
