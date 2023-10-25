from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from books.models import Book
from borrowings.models import Borrowing
from borrowings.paginations import BorrowingPagination
from borrowings.permissions import IsAdminOrIsOwnerGetPost
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIsOwnerGetPost,)
    pagination_class = BorrowingPagination

    def get_queryset(self):
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if is_active:
            if is_active == "True":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active == "False":
                queryset = queryset.exclude(actual_return_date__isnull=True)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        queryset = queryset.distinct()

        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingListSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "return_view":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @transaction.atomic()
    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAdminOrIsOwnerGetPost],
    )
    def return_view(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing)
        book = Book.objects.get(pk=borrowing.book.id)

        serializer.perform_return(borrowing, book)

        return Response(serializer.data, status=status.HTTP_200_OK)
