from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, nickname=None):
        if not email:
            raise ValueError("must have user email.")
        user = self.model(
            email=self.normalize_email(email), nickname=nickname or email.split("@")[0]
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email=self.normalize_email(email), password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="이메일")
    nickname = models.CharField(
        unique=True, max_length=20, null=True, verbose_name="닉네임"
    )
    is_active = models.BooleanField(default=True, verbose_name="활성 상태")
    is_staff = models.BooleanField(default=False, verbose_name="관리자 여부")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="가입일")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    def __str__(self) -> str:
        return self.email
