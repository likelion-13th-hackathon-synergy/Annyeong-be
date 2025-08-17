from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "real_name", "user_type", "age",
            "profile_image", "nationality", "introduction",
            "city", "service_language", "translation_category",
            "google_verified"
        ]

class SignupSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "real_name", "user_type", "password1", "password2"]

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            real_name=validated_data["real_name"],
            user_type=validated_data["user_type"],
            password=validated_data["password1"]
        )
        return user