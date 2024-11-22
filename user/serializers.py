from user.models import CustomUser
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "password"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                "이메일과 비밀번호를 모두 입력하십니오."
            )

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                "이메일 또는 비밀번호가 올바르지 않습니다."
            )

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                "이메일과 비밀번호를 모두 입력하십시오."
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError(
                ("이메일 또는 비밀번호가 올바르지 않습니다.")
            )

        data = super().validate(attrs)

        refresh = self.get_token(user)

        data["email"] = email
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data
