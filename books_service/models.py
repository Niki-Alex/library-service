from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "hard"
        SOFT = "soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()  # the number of this specific book available for now in the library
    daily_fee = models.DecimalField(max_digits=4, decimal_places=2)  # $USD

    def __str__(self):
        return f"{self.author}, {self.title}"

    class Meta:
        ordering = ["title"]
