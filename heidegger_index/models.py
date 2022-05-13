import requests

from django.db import models
from django.conf import settings
from django_extensions.db.fields import AutoSlugField

from heidegger_index.constants import LEMMA_TYPES, REF_TYPES
from heidegger_index.utils import gen_sort_key, slugify


class Work(models.Model):
    id = models.CharField(max_length=8, primary_key=True)
    csl_json = models.JSONField()
    reference = models.CharField(max_length=200, null=True)
    slug = AutoSlugField(populate_from="id")

    def __str__(self):
        return self.id

    def gen_reference(self):
        if not self.reference and self.csl_json:
            r = requests.post(
                settings.CITEPROC_ENDPOINT,
                json={"items": [self.csl_json]},
                params={"style": settings.CITEPROC_STYLE, "responseformat": "html"},
            )
            r.raise_for_status()
            self.reference = r.content.decode()

    def save(self, *args, **kwargs):
        self.gen_reference()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["id"]


class Lemma(models.Model):
    TYPES = LEMMA_TYPES
    value = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="children"
    )
    related = models.ManyToManyField("self", symmetrical=True)
    type = models.CharField(max_length=1, null=True, choices=TYPES.items())
    description = models.TextField(null=True)
    sort_key = models.CharField(max_length=100, null=True, unique=True)
    slug = AutoSlugField(populate_from="value", slugify_function=slugify)

    # Only applicable to lemmas with type='w'
    author = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="works"
    )

    # Use if lemma is associated with a work
    work = models.OneToOneField(Work, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.value

    def create_sort_key(self):
        self.sort_key = gen_sort_key(self.value)

    def save(self, *args, **kwargs):
        if not self.sort_key:
            self.create_sort_key()

        super().save(*args, **kwargs)

    @property
    def first_letter(self):
        return self.sort_key and self.sort_key[0].upper() or ""

    class Meta:
        ordering = ["sort_key"]


class PageReference(models.Model):
    TYPES = REF_TYPES
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)
    type = models.CharField(max_length=1, choices=TYPES.items(), null=True)

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
