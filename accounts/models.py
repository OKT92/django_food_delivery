from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256, blank=True)
    # image = models.ImageField(upload_to='company-photos', null=True)
    cloud_image = CloudinaryField('cloud_image', blank=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    mobile = models.CharField(max_length=13)
    office = models.CharField(max_length=13, blank=True)
    company_name = models.CharField(max_length=100)
    cumulative_order_number = models.PositiveSmallIntegerField(default=0)
    cumulative_order_value = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.user.first_name

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=64)
    value = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    balance = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user

class Topup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    status_choice = (
        ('pending', 'pending'),
        ('topped up', 'topped up'),
        ('canceled', 'canceled')
    )

    status = models.CharField(max_length=9, choices=status_choice, default='pending')


