# Generated by Django 4.1 on 2022-08-24 16:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heidegger_index', '0006_work_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='lemma',
            name='urn',
            field=models.URLField(max_length=100, null=True, unique=True, validators=[django.core.validators.URLValidator(schemes=['urn'])]),
        ),
    ]
