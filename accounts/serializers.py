from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AuditLog

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'profile_picture', 'badge')

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'action', 'details', 'timestamp')
