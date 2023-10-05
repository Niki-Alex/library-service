from rest_framework import serializers

from books_service.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BookListSerializer(BookSerializer):
    author = serializers.SlugRelatedField(many=True, read_only=True, slug_field="full_name")
