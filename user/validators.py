import re

from rest_framework.serializers import ValidationError

from user.models import CustomUser


class EmailValidator:
    def __call__(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError("이미 사용 중인 이메일입니다.")
        return value


class PasswordValidator:
    def __call__(self, value):
        if len(value) < 8:
            raise ValidationError("비밀번호는 8자 이상이어야 합니다.")

        if not re.search(r"[A-Z]", value):
            raise ValidationError("비밀번호는 영어 대문자를 하나 이상 포함해야 합니다.")

        if not re.search(r"[a-z]", value):
            raise ValidationError("비밀번호는 영어 소문자를 하나 이상 포함해야 합니다.")

        if not re.search(r"\d", value):
            raise ValidationError("비밀번호는 숫자 하나 이상 포함해야 합니다.")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("비밀번호는 특수문자를 하나 이상 포함해야 합니다.")
