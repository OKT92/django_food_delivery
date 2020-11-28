from django.contrib import admin
from .models import Profile, Wallet, Company

# Register your models here.

admin.site.register(Profile)
admin.site.register(Wallet)
admin.site.register(Company)