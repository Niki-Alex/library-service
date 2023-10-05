from rest_framework import routers

from books_service.views import BookViewSet, AuthorViewSet

router = routers.DefaultRouter()
router.register("", BookViewSet)
router.register("authors", AuthorViewSet)


urlpatterns = router.urls

app_name = "books_service"
