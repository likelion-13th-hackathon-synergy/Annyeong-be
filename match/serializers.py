from rest_framework import serializers
from .models import UserMatchPreference, MatchLike, MatchDislike

class UserMatchPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMatchPreference
        fields = ['mode']

class MatchLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchLike
        fields = ['from_user', 'to_user', 'created_at']

class MatchDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchDislike
        fields = ['from_user', 'to_user', 'created_at']