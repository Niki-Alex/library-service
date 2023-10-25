from rest_framework import routers

from books.views import BookViewSet, AuthorViewSet

router = routers.DefaultRouter()
router.register("", BookViewSet, basename="books")
router.register("authors", AuthorViewSet)


urlpatterns = router.urls

app_name = "books"
