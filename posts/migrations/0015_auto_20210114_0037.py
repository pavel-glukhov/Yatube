# Generated by Django 2.2.6 on 2021-01-13 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20210114_0020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(verbose_name='комментарий'),
        ),
    ]
