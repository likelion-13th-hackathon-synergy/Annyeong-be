from django.contrib.auth.models import User

from rest_framework import serializers

from .models import ChatRoom, Message

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='profile.image', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chatroom', 'sender', 'content', 'translated_content', 'image', 'created_at', 'is_read']

class ChatRoomSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    other_participant = serializers.SerializerMethodField()

    def get_other_participant(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        other = obj.get_other_participant(user)
        return UserSerializer(other).data if other else None

    class Meta:
        model = ChatRoom
        fields = ['id', 'requester', 'receiver', 'other_participant', 'updated_at', 'is_active', 'messages', 'unread_count']