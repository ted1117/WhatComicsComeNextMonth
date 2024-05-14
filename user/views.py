from django.shortcuts import render
from rest_framework import generics

from user.models import CustomUser
from user.serializers import UserSerializer


# Create your views here.
class UserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


def index(request):
    return render(request, "register.html", context={})
