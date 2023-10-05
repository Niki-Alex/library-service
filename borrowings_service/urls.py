from rest_framework import routers

from borrowings_service.views import BorrowingViewSet


router = routers.DefaultRouter()
router.register("", BorrowingViewSet)


urlpatterns = router.urls

app_name = "borrowings_service"
