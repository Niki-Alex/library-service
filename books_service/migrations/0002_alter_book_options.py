# Generated by Django 4.2.5 on 2023-10-03 13:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("books_service", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ["title"]},
        ),
    ]
