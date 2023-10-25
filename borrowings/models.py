import datetime

from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        to=Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    def __str__(self):
        active = (
            f"Expected return date: {self.expected_return_date}"
            if self.is_active
            else f"Actual return date: {self.actual_return_date}"
        )
        return (
            f"Book: {self.book.title}, borrow date: {self.borrow_date}\n"
            f"User: {self.user.email}, {self.is_active}\n" + active
        )

    @property
    def is_active(self):
        return not bool(self.actual_return_date)

    @staticmethod
    def validate_book_inventory(book_inventory, error_to_raise):
        if book_inventory == 0:
            raise error_to_raise(
                {"book_inventory": "Borrowing cannot be created, "
                                   "because the inventory this book is 0"}
            )

    @staticmethod
    def validate_date(error_to_raise, actual_return_date=None):
        today = datetime.date.today()
        if actual_return_date and actual_return_date != today:
            raise error_to_raise(
                {"actual_return_date": f"{actual_return_date} "
                                       f"cannot be earlier or later than {today}"}
            )

    def clean(self):
        Borrowing.validate_date(ValidationError, self.actual_return_date)
        Borrowing.validate_book_inventory(self.book.inventory, ValidationError)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )
