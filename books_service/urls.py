from rest_framework import routers

from books_service.views import BookViewSet


router = routers.DefaultRouter()
router.register("", BookViewSet)


urlpatterns = router.urls

app_name = "books_service"
