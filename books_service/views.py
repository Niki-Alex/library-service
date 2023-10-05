from rest_framework import viewsets

from books_service.models import Book, Author
from books_service.serializers import (
    BookSerializer,
    BookListSerializer,
    AuthorSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related("author")
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = self.queryset
        title = self.request.query_params.get("title")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BookListSerializer

        return BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        queryset = self.queryset
        first_name = self.request.query_params.get("first_name")

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        return queryset.distinct()
