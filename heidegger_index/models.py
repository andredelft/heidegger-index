from django.db import models


class Work(models.Model):
    id = models.CharField(max_length=8, primary_key=True)
    reference = models.JSONField()


class Lemma(models.Model):
    PERSON = 'p'
    LEMMA_TYPES = {
        PERSON: 'Person'
    }
    term = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=1, null=True, choices=LEMMA_TYPES.items())


class PageReference(models.Model):
    work = models.ForeignKey(Work, on_delete=models.PROTECT)
    lemma = models.ForeignKey(Lemma, on_delete=models.PROTECT)
    reference = models.CharField(max_length=20)
