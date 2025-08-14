from django.contrib.auth import get_user_model

User = get_user_model()

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
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField(read_only=True)
    other_participant = serializers.SerializerMethodField()

    # 생성할 때 receiver_id를 따로 받기 위한 필드 (write_only)
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='receiver'
    )

    def get_other_participant(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        other = obj.get_other_participant(user)
        return UserSerializer(other).data if other else None

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        return MessageSerializer(last_msg).data if last_msg else None

    class Meta:
        model = ChatRoom
        fields = ['id', 'requester', 'receiver', 'receiver_id', 'other_participant', 'updated_at', 'is_active', 'last_message', 'unread_count']