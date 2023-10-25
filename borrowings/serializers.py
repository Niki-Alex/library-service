import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookListSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(required=False)

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_date(
            ValidationError,
            attrs.get("actual_return_date", None)
        )

        Borrowing.validate_book_inventory(
            attrs["book"].inventory,
            ValidationError
        )
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = BookListSerializer(many=False, read_only=True)
    user = serializers.SlugRelatedField(
        read_only=True, many=False, slug_field="email"
    )


class BorrowingCreateSerializer(BorrowingSerializer):
    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        today = datetime.date.today()
        if attrs["expected_return_date"] < today:
            raise ValidationError(
                {"expected_return_date": f"Expected return date can't "
                                         f"be any sooner than {today}"}
            )

        return data

    def create(self, validated_data):
        with transaction.atomic():
            borrowing = Borrowing.objects.create(**validated_data)
            borrowing.book.inventory -= 1
            borrowing.book.save()
            return borrowing

    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")


class BorrowingReturnSerializer(BorrowingSerializer):
    actual_return_date = serializers.DateField(
        required=False, read_only=True
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )

        read_only_fields = (
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
