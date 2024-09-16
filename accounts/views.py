from accounts.models import Users
from rest_framework import permissions, viewsets

from accounts.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]