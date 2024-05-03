import requests

from django.db import models
from django.db.models import Q
from django.conf import settings
from django_extensions.db.fields import AutoSlugField
from django.core.validators import URLValidator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from heidegger_index.constants import LemmaType, RefType, MetadataType
from heidegger_index.passage import get_perseus_passage
from heidegger_index.utils import (
    gen_sort_key,
    slugify,
    contains_page_range,
)
from heidegger_index.validators import validate_gnd, validate_zeno


class Work(models.Model):
    key = models.CharField(max_length=8, unique=True)
    csl_json = models.JSONField()
    reference = models.CharField(max_length=200, null=True)
    slug = AutoSlugField(populate_from="key")
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="children"
    )
    description = models.TextField(null=True)

    def __str__(self):
        return self.key

    def gen_reference(self):
        if not self.reference and self.csl_json:
            r = requests.post(
                settings.CITEPROC_ENDPOINT,
                json={"items": [self.csl_json]},
                params={"style": settings.CITEPROC_STYLE, "responseformat": "html"},
            )
            r.raise_for_status()
            self.reference = r.content.decode()

    @property
    def title(self):
        return self.csl_json.get("title-short") or self.csl_json.get("title") or ""

    @property
    def icon(self):
        return "icon-book-open" if self.parent else "icon-book"

    @property
    def display(self):
        return mark_safe(f'<span class="work">{self.title}</span>')

    @property
    def display_full(self):
        title = self.csl_json.get("title")
        return mark_safe(f'<span class="work">{title}</span>') if title else ""

    def save(self, *args, **kwargs):
        self.gen_reference()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["key"]


class LemmaManager(models.Manager):
    # Get a custom ordering where lemma's that start with a number appear after those that start with letters
    def alpha_numeric_ordering(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        return sorted(qs, key=lambda l: (1 if l.first_letter == "#" else 0, l.sort_key))


class Lemma(models.Model):
    value = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="children"
    )
    related = models.ManyToManyField("self", symmetrical=True)
    type = models.CharField(max_length=1, null=True, choices=LemmaType.list_choices())
    description = models.TextField(null=True)

    urn = models.URLField(
        MetadataType.URN.label,
        max_length=100,
        null=True,
        validators=[URLValidator(schemes=["urn"])],
        unique=True,
    )
    perseus_content = models.TextField(null=True)

    gnd = models.CharField(
        MetadataType.GND.label,
        null=True,
        unique=True,
        max_length=11,
        validators=[validate_gnd],
    )

    dk = models.IntegerField(MetadataType.DIELS_KRANZ.label, null=True)

    zeno = models.CharField(
        MetadataType.ZENO.label,
        null=True,
        unique=True,
        max_length=50,
        validators=[validate_zeno],
    )

    sort_key = models.CharField(max_length=100, null=True, unique=True)
    first_letter = models.CharField(max_length=1, null=True)
    slug = AutoSlugField(populate_from="value", slugify_function=slugify)

    # Only applicable to lemmas with type='w'
    author = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="works"
    )

    # Use if lemma is associated with a work
    work = models.OneToOneField(Work, null=True, on_delete=models.SET_NULL)

    objects = LemmaManager()

    def __str__(self):
        return self.value

    def create_sort_key(self):
        self.sort_key = gen_sort_key(self.value)
        first_letter = self.sort_key[0].upper() if self.sort_key else ""
        if ord("0") <= ord(first_letter) <= ord("9"):
            first_letter = "#"
        self.first_letter = first_letter

    def save(self, *args, **kwargs):
        if not self.sort_key:
            self.create_sort_key()

        super().save(*args, **kwargs)

    def load_work_text(self):
        if self.perseus_content or not self.urn or self.type != "w":
            return

        self.perseus_content = get_perseus_passage(self.urn)

    @property
    def display(self):
        if self.type:
            lemma_type = LemmaType.get_label(self.type)
            class_name = f"lemma lemma--{lemma_type}"
        else:
            class_name = "lemma"

        return mark_safe(f'<span class="{class_name}">{self}</span>')

    @property
    def icon(self):
        match self.type:
            case "w":
                return "icon-book"
            case "p":
                return "icon-user"
            case "g":
                return "icon-map-pin-line"
            case _:
                return ""

    class Meta:
        ordering = ["sort_key"]


class PageReference(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)
    type = models.CharField(max_length=1, choices=RefType.list_choices(), null=True)

    # Datafied page reference
    whole = models.BooleanField(default=False)
    start = models.IntegerField(null=True)
    end = models.IntegerField(null=True)
    suffix = models.CharField(
        max_length=2,
        null=True,
        choices=[("f", "And next page"), ("ff", "And next pages")],
    )

    def __str__(self):
        if self.whole:
            return _("Heel het werk")
        elif self.end:
            return f"{self.start}–{self.end}"
        elif self.suffix:
            return f"{self.start}{self.suffix}"
        else:
            return f"{self.start}"

    def refers_to_page_range(self, page_range: dict) -> bool:
        if contains_page_range(self.__dict__, page_range):
            return True

        return False

    class Meta:
        ordering = ["whole", "lemma", "work", "start", "end", "suffix"]
        constraints = [
            models.CheckConstraint(
                check=Q(whole=False, start__isnull=False) | Q(whole=True),
                name="Start must be defined when lemma doesn't refer to the whole work",
            )
        ]


# Stored aggregates

ALPHABET = []


def get_alphabet():
    global ALPHABET

    if not ALPHABET:
        print("Generating alphabet...")
        ALPHABET = list(
            Lemma.objects.order_by("first_letter")
            .values_list("first_letter", flat=True)
            .distinct()
        )

        # If we have numbers, put the group on the end of the list
        try:
            ALPHABET.remove("#")
        except ValueError:
            pass
        else:
            ALPHABET.append("#")

    return ALPHABET
