from django.conf import settings
from django.db import models

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        to=Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    def __str__(self):
        active = (
            f"Expected return date: {self.expected_return_date}"
            if self.is_active
            else f"Actual return date: {self.actual_return_date}"
        )
        return (
            f"Book: {self.book.title}, borrow date: {self.borrow_date}\n"
            f"User: {self.user.email}, {self.is_active}\n"
            + active
        )

    @property
    def is_active(self):
        return not bool(self.actual_return_date)
