from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import (
    CreateUserView,
    UserUpdateView,
)


urlpatterns = [
    path("", CreateUserView.as_view(), name="user-create"),
    path("me", UserUpdateView.as_view(), name="user-detail"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

app_name = "users"
