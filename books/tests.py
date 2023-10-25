from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from books.models import Book, Author
from books.serializers import BookListSerializer

BOOK_URL = reverse("books:books-list")


def sample_author(**params):
    defaults = {
        "first_name": "Testname",
        "last_name": "Testsername",
    }
    defaults.update(params)

    return Author.objects.create(**defaults)


def sample_book(**params):
    author = Author.objects.create(first_name="first", last_name="last")
    defaults = {
        "title": "Title",
        "cover": "hard",
        "inventory": 2,
        "daily_fee": 0.50,
    }
    defaults.update(params)

    book = Book.objects.create(**defaults)
    book.author.add(author)

    return book


def book_detail_url(book_id):
    return reverse("books:books-detail", args=[book_id])


class UnauthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_books_by_title(self):
        book1 = sample_book(title="Book")
        book2 = sample_book(title="Another Book")
        book3 = sample_book(title="No match")

        res = self.client.get(BOOK_URL, {"title": "book"})

        serializer1 = BookListSerializer(book1)
        serializer2 = BookListSerializer(book2)
        serializer3 = BookListSerializer(book3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_books_detail(self):
        book = sample_book()
        url = book_detail_url(book.id)
        res = self.client.get(url)

        serializer = BookListSerializer(book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_unauthorized(self):
        author = sample_author()

        payload = {
            "title": "Title",
            "cover": "hard",
            "authors": author.id,
            "inventory": 2,
            "daily_fee": 0.50,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="teStpass123",
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self):
        author = sample_author()

        payload = {
            "title": "Title",
            "cover": "hard",
            "authors": author.id,
            "inventory": 2,
            "daily_fee": 0.50,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        author = sample_author()
        payload = {
            "title": "Title",
            "author": author.id,
            "cover": "soft",
            "inventory": 5,
            "daily_fee": 1.50,
        }

        res = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res.data["id"])
        authors = book.author.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(authors.count(), 1)
        self.assertIn(author, authors)

    def test_put_book(self):
        author = sample_author()
        payload = {
            "title": "TitleUpdate",
            "author": author.id,
            "cover": "soft",
            "inventory": 5,
            "daily_fee": 1.50,
        }

        book = sample_book()
        url = book_detail_url(book.id)

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()

        self.assertEqual(book.title, "TitleUpdate")
        self.assertEqual(book.cover, "soft")
        self.assertEqual(book.inventory, 5)
        self.assertEqual(book.daily_fee, 1.50)
        self.assertEqual(list(book.author.all()), [author])

    def test_delete_book(self):
        book = sample_book()
        url = book_detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
