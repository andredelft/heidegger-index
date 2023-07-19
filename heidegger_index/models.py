import requests
from bs4 import BeautifulSoup
from pyCTS import CTS_URN

from django.db import models
from django.conf import settings
from django_extensions.db.fields import AutoSlugField
from django.core.validators import URLValidator

from heidegger_index.constants import LemmaType, RefType, MetadataType
from heidegger_index.utils import (
    gen_sort_key,
    slugify,
    contains_page_range,
)
from heidegger_index.validators import validate_gnd


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

    def save(self, *args, **kwargs):
        self.gen_reference()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["key"]


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

    sort_key = models.CharField(max_length=100, null=True, unique=True)
    first_letter = models.CharField(max_length=1, null=True)
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
        first_letter = self.sort_key[0].upper() if self.sort_key else ""
        if ord("0") <= ord(first_letter) <= ord("9"):
            first_letter = "#"
        self.first_letter = first_letter

    def save(self, *args, **kwargs):
        if not self.sort_key:
            self.create_sort_key()

        super().save(*args, **kwargs)

    def load_work_text(self):
        if not self.perseus_content and self.urn and self.type == "w":
            lemma_urn = CTS_URN(self.urn)
            if not lemma_urn.passage_component:
                self.perseus_content = None
            else:
                p_link = (
                    "https://scaife-cts.perseus.org/api/cts?request=GetPassage&urn="
                    + self.urn
                )
                p_response = requests.get(p_link)
                parsed_xml = BeautifulSoup(p_response.text, 'lxml')
                while parsed_xml.p.bibl:
                    parsed_xml.p.bibl.decompose()
                while parsed_xml.p.label:
                    parsed_xml.p.label.decompose()
                self.perseus_content = str(parsed_xml.p.get_text())

    class Meta:
        ordering = ["sort_key"]


class PageReference(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)
    type = models.CharField(max_length=1, choices=RefType.list_choices(), null=True)

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
            return f"{self.start}{self.suffix}"
        else:
            return f"{self.start}"

    def refers_to_page_range(self, page_range: dict) -> bool:
        if contains_page_range(self.__dict__, page_range):
            return True

        return False

    class Meta:
        ordering = ["lemma", "work", "start", "end", "suffix"]


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

    return ALPHABET
