# Generated by Django 4.1.7 on 2023-03-19 21:42

import django.core.validators
from django.db import migrations, models
import heidegger_index.validators


class Migration(migrations.Migration):
    dependencies = [
        ("heidegger_index", "0009_lemma_gnd"),
    ]

    operations = [
        migrations.AddField(
            model_name="lemma",
            name="dk",
            field=models.IntegerField(null=True, verbose_name="Diels-Kranz ID"),
        ),
        migrations.AlterField(
            model_name="lemma",
            name="gnd",
            field=models.CharField(
                max_length=11,
                null=True,
                unique=True,
                validators=[heidegger_index.validators.validate_gnd],
                verbose_name="Gemeinsame Normdatei",
            ),
        ),
        migrations.AlterField(
            model_name="lemma",
            name="urn",
            field=models.URLField(
                max_length=100,
                null=True,
                unique=True,
                validators=[django.core.validators.URLValidator(schemes=["urn"])],
                verbose_name="Uniform Resource Name",
            ),
        ),
    ]