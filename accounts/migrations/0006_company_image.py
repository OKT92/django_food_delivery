# Generated by Django 3.0.8 on 2020-10-27 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20201023_0551'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='image',
            field=models.ImageField(null=True, upload_to='company-photos'),
        ),
    ]