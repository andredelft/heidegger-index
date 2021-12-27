import requests
from unidecode import unidecode

from django.db import models
from django.conf import settings
from django.utils.safestring import SafeString
from django_extensions.db.fields import AutoSlugField

from heidegger_index.constants import LEMMA_TYPES


class Work(models.Model):
    id = models.CharField(max_length=8, primary_key=True)
    csl_json = models.JSONField()
    reference = models.CharField(max_length=200, null=True)
    slug = AutoSlugField(populate_from="id")

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.reference and self.csl_json:
            r = requests.post(
                settings.CITEPROC_ENDPOINT,
                json={"items": [self.csl_json]},
                params={"style": settings.CITEPROC_STYLE, "responseformat": "html"},
            )
            r.raise_for_status()
            self.reference = r.content.decode()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["id"]


class Lemma(models.Model):
    TYPES = LEMMA_TYPES
    value = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=1, null=True, choices=TYPES.items())
    sort_key = models.CharField(max_length=100, null=True)
    slug = AutoSlugField(populate_from="value")

    def __str__(self):
        return self.value

    def format(self):
        format_string = f"<i>{self.value}</i>"
        if self.type:
            return SafeString(f"{format_string} ({self.get_type_display()})")
        else:
            return SafeString(format_string)

    def create_sort_key(self):
        self.sort_key = unidecode(self.value).lower()

    def save(self, *args, **kwargs):
        if not self.sort_key:
            self.create_sort_key()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["sort_key"]


class PageReference(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)

    # Datafied page reference
    start = models.IntegerField()
    end = models.IntegerField(null=True)
    suffix = models.CharField(
        max_length=2,
        null=True,
        choices=[("f", "And next page"), ("ff", "And next pages")],
    )

    def __str__(self):
        if self.end:
            return f"{self.start}–{self.end}"
        elif self.suffix:
            return f"{self.start}{self.suffix}."
        else:
            return f"{self.start}"

    class Meta:
        ordering = ["lemma", "work", "start", "end", "suffix"]
