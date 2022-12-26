from api.pagination import SetCustomPagination
from api.serializers import FollowSerializer, UsersSerializer
from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User

from .models import Follow


class UsersViewSet(UserViewSet):
    """Управление пользователями, подписка, отписка, вывод активных подписок"""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = SetCustomPagination
    permission_classes = [IsAuthenticated]

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        serializer = FollowSerializer(
            data={"user": request.user.id, "author": id}
        )

        if request.method == 'POST':
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={"request": request}
                )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Follow,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        queryset.annotate(recipes_count=Count('recipes'))
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
            )
        return self.get_paginated_response(serializer.data)
