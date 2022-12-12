from api.pagination import SetCustomPagination
from api.serializers import UsersSerializer

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Follow

from users.models import User


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = SetCustomPagination
    permission_classes=[IsAuthenticated]

 #   @action(
 #       detail=True,
 #       methods=['post', 'delete'],
 #       permission_classes=[IsAuthenticated]
 #   )
