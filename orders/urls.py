from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path("", views.index, name="index"),
    path("product/", views.menu, name="menu"),
    path("product/<int:item_id>", views.product, name="product"),
    path("cart/", views.cart, name="cart"),
    path("remove/<int:cart_id>", views.remove, name="remove"),
    path("order/", views.orders, name="orders"),
    path("order/<int:order_id>", views.order, name="order"),
    path("cancel/", views.cancel, name="cancel"),
]
