from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField

# Create your models here.

class Product(models.Model):
    category = models.CharField(max_length=24, blank=True)
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField(blank=True)
    # image = models.ImageField(upload_to='product-photos')
    image = CloudinaryField('image', null=True)
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Option(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.CharField(max_length=16)
    selection = models.CharField(max_length=16)
    additional_price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.selection

class AddOn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    addon_item = models.CharField(max_length=64)
    additional_price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.addon_item

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.user.first_name

class Cart_Option(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.option.selection

class Cart_AddOn(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    addon = models.ForeignKey(AddOn, on_delete=models.CASCADE)

    def __str__(self):
        return self.addon

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    status_choice = (
        ('pending', 'pending'),
        ('paid', 'paid'),
        ('completed', 'completed'),
        ('canceled', 'canceled')
    )

    status = models.CharField(max_length=12, choices=status_choice, default='pending')

    def __str__(self):
        return f'{self.id}'

class Order_Item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    product_name = models.CharField(max_length=64)
    selection = models.CharField(max_length=256, blank=True)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=6, decimal_places=2)
    total = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.product_name