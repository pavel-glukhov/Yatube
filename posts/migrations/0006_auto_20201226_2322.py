# Generated by Django 2.2.9 on 2020-12-26 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20201226_2300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='здесь можно писать свою историю', verbose_name='Текст'),
        ),
    ]