# Generated by Django 4.0.4 on 2022-06-06 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heidegger_index', '0004_expand_data_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='lemma',
            name='first_letter',
            field=models.CharField(max_length=1, null=True),
        ),
    ]