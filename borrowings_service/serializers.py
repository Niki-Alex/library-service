from rest_framework import serializers

from borrowings_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")


# class BorrowingListSerializer(BorrowingSerializer):
#     book =
#
#     class Meta:
#         model = Borrowing
#         fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user")
