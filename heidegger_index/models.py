from django.db import models

from heidegger_index.constants import LEMMA_TYPES


class Work(models.Model):
    id = models.CharField(max_length=8, primary_key=True)
    csl_json = models.JSONField()

    def __str__(self):
        return self.id


class Lemma(models.Model):
    lemma_types = LEMMA_TYPES
    value = models.CharField(max_length=100, unique=True)
    type = models.CharField(
        max_length=1, null=True, choices=lemma_types.items()
    )

    def __str__(self):
        return self.value


class PageReference(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)
    value = models.CharField(max_length=20)

    def __str__(self):
        return self.value
