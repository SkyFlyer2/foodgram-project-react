from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'users'

router_v1 = DefaultRouter()

#router.register('users', CustomUserViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]