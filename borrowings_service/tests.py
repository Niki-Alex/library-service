import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from books_service.models import Book, Author
from borrowings_service.models import Borrowing
from borrowings_service.serializers import BorrowingListSerializer

BORROWINGS_URL = reverse("borrowings_service:borrowings-list")
EXPECTED_RETURN_DATE = datetime.date.today() + datetime.timedelta(days=3)


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


def sample_borrowing(user, **params):
    book = sample_book()

    defaults = {
        "expected_return_date": EXPECTED_RETURN_DATE,
        "book": book,
        "user": user,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def borrowing_detail_url(borrowings_id):
    return reverse("borrowings_service:borrowings-detail", args=[borrowings_id])


def borrowing_return_url(borrowings_id):
    return reverse("borrowings_service:borrowings-return-view", args=[borrowings_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.other_user = get_user_model().objects.create_user(
            "other@test.com",
            "otherpass",
        )
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings_only_your_own(self):
        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(user=self.user)
        borrowing3 = sample_borrowing(user=self.other_user)

        res = self.client.get(BORROWINGS_URL)

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_borrowings_by_is_active(self):
        borrowing1 = sample_borrowing(
            user=self.user, actual_return_date=datetime.date.today()
        )
        borrowing2 = sample_borrowing(
            user=self.user, actual_return_date=datetime.date.today()
        )
        borrowing3 = sample_borrowing(
            user=self.user,
        )

        res = self.client.get(BORROWINGS_URL, {"is_active": "False"})

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_borrowings_detail(self):
        borrowing = sample_borrowing(user=self.user)
        url = borrowing_detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingListSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing_with_decrease_in_book_inventory_by_1(self):
        book = sample_book()
        inventory_before = book.inventory

        payload = {
            "expected_return_date": EXPECTED_RETURN_DATE,
            "book": book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWINGS_URL, payload)

        book.refresh_from_db()
        inventory_after = book.inventory

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(inventory_before - 1, inventory_after)
        borrowings = Borrowing.objects.get(id=res.data["id"])
        payload.update({"book": book, "user": self.user})
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(borrowings, key))

    def test_raise_validation_error_when_creating_borrowing_with_book_inventory_equal_0(
        self,
    ):
        book = sample_book(inventory=0)

        payload = {
            "expected_return_date": EXPECTED_RETURN_DATE,
            "book": book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing_and_addition_book_inventory_by_1(self):
        book = sample_book(inventory=1)
        borrowing = sample_borrowing(book=book, user=self.user)

        url = borrowing_return_url(borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data["actual_return_date"], datetime.date.today().strftime("%Y-%m-%d")
        )
        book.refresh_from_db()
        self.assertEqual(book.inventory, 2)

    def test_raise_validation_error_when_twice_return_borrowing(self):
        borrowing = sample_borrowing(user=self.user)
        url = borrowing_return_url(borrowing.id)

        self.client.post(url)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.other_user = get_user_model().objects.create_user(
            "other@test.com",
            "otherpass",
        )
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_all_borrowings(self):
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.other_user)

        res = self.client.get(BORROWINGS_URL)

        borrowings = Borrowing.objects.order_by("id")
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_borrowings_by_user_id(self):
        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(user=self.user)
        borrowing3 = sample_borrowing(user=self.other_user)

        res = self.client.get(BORROWINGS_URL, {"user_id": {self.user.id}})

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])
