# Generated by Django 3.0.8 on 2020-10-27 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20201004_0612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='product-photos'),
        ),
    ]
