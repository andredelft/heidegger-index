# Generated by Django 4.2.9 on 2024-02-09 08:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("heidegger_index", "0012_lemma_zeno"),
    ]

    operations = [
        migrations.AddField(
            model_name="lemma",
            name="lang",
            field=models.CharField(max_length=3, null=True),
        ),
    ]
