from django.db.models import Sum

def cart_item_number(request):
    if request.user.is_authenticated:
        cart = request.user.cart_set.all().aggregate(Sum('quantity'))
        if not cart['quantity__sum']:
            cart['quantity__sum'] = 0
    else:
        cart = {'quantity__sum': 0}

    return cart
 