# Generated by Django 2.2.9 on 2021-01-06 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20210105_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Ваш комментарий'),
        ),
    ]