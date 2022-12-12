from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow

from users.models import User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
#    serializer_class = CustomUserSerializer
#    pagination_class = CustomPagination
    permission_classes=[IsAuthenticated]

 #   @action(
 #       detail=True,
 #       methods=['post', 'delete'],
 #       permission_classes=[IsAuthenticated]
 #   )
