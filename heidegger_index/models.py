import requests

from django.db import models
from django.conf import settings

from heidegger_index.constants import LEMMA_TYPES


class Work(models.Model):
    id = models.CharField(max_length=8, primary_key=True)
    csl_json = models.JSONField()
    reference = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.reference and self.csl_json:
            r = requests.post(
                settings.CITEPROC_ENDPOINT,
                json={'items': [self.csl_json]},
                params={
                    'style': settings.CITEPROC_STYLE,
                    'responseformat': 'html'
                }
            )
            r.raise_for_status()
            self.reference = r.content.decode()
        super().save()


class Lemma(models.Model):
    TYPES = LEMMA_TYPES
    value = models.CharField(max_length=100, unique=True)
    type = models.CharField(
        max_length=1, null=True, choices=TYPES.items()
    )

    def __str__(self):
        return self.value


class PageReference(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)

    # Datafied page reference
    begin = models.IntegerField()
    end = models.IntegerField(null=True)
    suffix = models.CharField(
        max_length=2, null=True, choices=[
            ('f', 'And next page'),
            ('ff', 'And next pages')
        ]
    )

    def __str__(self):
        if self.end:
            return f'{self.begin}–{self.end}'
        elif self.suffix:
            return f'{self.begin}{self.suffix}.'
        else:
            return f'{self.begin}'
