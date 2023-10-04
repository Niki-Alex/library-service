from django.urls import path

from users_service.views import (
    CreateUserView,
    UserUpdateView,
)


urlpatterns = [
    path("", CreateUserView.as_view(), name="user-create"),
    path("me", UserUpdateView.as_view(), name="user-detail"),
]

app_name = "users_service"
