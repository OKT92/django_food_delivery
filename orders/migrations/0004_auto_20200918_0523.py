# Generated by Django 3.0.8 on 2020-09-17 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20200918_0522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('submitted', 'submitted'), ('paid', 'paid'), ('completed', 'completed'), ('cancelled', 'cancelled')], default='submitted', max_length=12),
        ),
    ]
