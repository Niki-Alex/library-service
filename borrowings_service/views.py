from rest_framework import viewsets

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        borrow_date = self.request.query_params.get("borrow_date")

        if borrow_date:
            queryset = queryset.filter(borrow_date=borrow_date)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingListSerializer

        return BorrowingSerializer
