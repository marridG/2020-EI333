# Generated by Django 3.0.6 on 2020-05-29 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SJTUTTA_manage', '0002_auto_20200529_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
