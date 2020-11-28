from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, reverse
from .models import Product, Option, AddOn, Cart, Cart_Option, Cart_AddOn, Order, Order_Item
from accounts.models import Company
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from fooddelivery.context_processor import cart_item_number

# Create your views here.

def index(request):
    company = Company.objects.all()
    context = {
        "company": company,
    }
    return render(request, "orders/index.html", context)

def menu(request):
    menu = Product.objects.filter(published=True)
    context = {
        "menu": menu,
    }
    return render(request, "orders/menu.html", context)

def product(request, item_id):
    if request.method == "POST":
        # create a dictionary for JsonResponse
        data = {
            "status": False,
        }

        if request.user.is_authenticated:
            option = request.POST.getlist("option")
            addon = request.POST.getlist("addon")
            quantity = int(request.POST["quantity"])

            if quantity < 1 or quantity > 999:
                return HttpResponseBadRequest()

            selection = "Selection: "
            item_price = Product.objects.get(pk=item_id).price
            
            total_price = item_price

            for x in option:
                total_price += Option.objects.get(pk=int(x)).additional_price
                selection += Option.objects.get(pk=int(x)).selection + ", "

            for x in addon:
                total_price += AddOn.objects.get(pk=int(x)).additional_price
                selection += AddOn.objects.get(pk=int(x)).addon_item + ", "

            data["status"] = True
            data["total_price"] = total_price

            if selection != "Selection: ":
                data["selection"] = selection[:-2]

            # check if same item in the cart
            cart_items = request.user.cart_set.filter(product_id=item_id)

            if cart_items:
                # if item in cart, check if option and addon are same
                option_set = set(map(int, option))
                addon_set = set(map(int, addon))

                for x in cart_items:
                    # eliminate those with different addon number
                    if len(x.cart_addon_set.all()) != len(addon):
                        continue

                    else:
                        cart_option = []
                        cart_addon = []

                        for y in x.cart_option_set.all():
                            cart_option.append(y.option_id)
                        for y in x.cart_addon_set.all():
                            cart_addon.append(y.addon_id)

                        cart_option_set = set(cart_option)
                        cart_addon_set = set(cart_addon)
                        
                        # item with same option and addon found in cart, increase the quantity
                        if option_set.issubset(cart_option_set) and addon_set.issubset(cart_addon_set):
                            x.quantity += quantity
                            x.save()
                            # update the cart item number via JS
                            cart = cart_item_number(request)
                            data.update(cart)
                            return JsonResponse(data)

            # item with same option and addon not found in cart, create new item in cart
            new_item = request.user.cart_set.create(product_id=item_id, quantity=quantity)
            if option:
                for x in option:
                    new_item.cart_option_set.create(option_id=x)
            if addon:
                for x in addon:
                    new_item.cart_addon_set.create(addon_id=x)

            # update the cart item number via JS
            cart = cart_item_number(request)
            data.update(cart)

            return JsonResponse(data)

        else: # user is not authenticated
            return JsonResponse(data)

    else: # request.method == GET
        item = get_object_or_404(Product, published=True, pk=item_id)
        
        option = item.option_set.all()
        option_queryset = []

        if option:
            categories = []

            for x in option:
                if x.category not in categories:
                    categories.append(x.category)
            
            for x in categories:
                option_queryset.append(item.option_set.filter(category=x))
        
        addon = item.addon_set.all()
        
        context = {
            "item": item,
            "option": option_queryset,
            "addon": addon,
        }

        return render(request, "orders/product-single.html", context)

@login_required
def cart(request):
    if request.method == "POST":            # update cart quantity
        cart_items = request.user.cart_set.all()
        subtotal = 0

        for x, y in request.POST.items():
            if int(y) < 1 or int(y) > 999:
                return HttpResponseBadRequest()

            item = request.user.cart_set.get(pk=int(x))
            item.quantity = int(y)
            item.save()

        for i in cart_items:

            total_unit_price = i.product.price

            for j in i.cart_option_set.all():
                total_unit_price += j.option.additional_price

            for j in i.cart_addon_set.all():
                total_unit_price += j.addon.additional_price

            subtotal += total_unit_price * i.quantity
        
        data = {
            "subtotal": subtotal,
        }

        cart = cart_item_number(request)

        data.update(cart)

        return JsonResponse(data)

    else:           # cart page
        class querydata():
            def __init__(self, item, selection, price):
                self.item = item
                self.selection = selection
                self.price = price

        cart = []
        subtotal = 0

        for x in request.user.cart_set.all():
            selection = ""
            total_unit_price = x.product.price

            for y in x.cart_option_set.all():
                selection += y.option.selection + ", "
                total_unit_price += y.option.additional_price

            for y in x.cart_addon_set.all():
                selection += y.addon.addon_item + ", "
                total_unit_price += y.addon.additional_price

            cart.append(querydata(x, selection[:-2], total_unit_price))

            subtotal += total_unit_price * x.quantity

        context = {
            "cart": cart,
            "subtotal": subtotal
        }

        return render(request, "orders/cart.html", context)

@require_POST
def remove(request, cart_id):           # remove cart item
    request.user.cart_set.get(pk=cart_id).delete()

    cart = cart_item_number(request)

    subtotal = 0

    if request.user.cart_set.all():
        for x in request.user.cart_set.all():
            total_unit_price = x.product.price

            for y in x.cart_option_set.all():
                total_unit_price += y.option.additional_price

            for y in x.cart_addon_set.all():
                total_unit_price += y.addon.additional_price

            subtotal += total_unit_price * x.quantity

    cart["subtotal"] = subtotal

    return JsonResponse(cart)

@login_required
def orders(request):
    if request.method == "POST":        # Place an order from cart

        cart_items = request.user.cart_set.all()

        if cart_items:

            order = Order.objects.create(user=request.user)

            order_total = 0

            for x in cart_items:

                selection = ""
                total_unit_price = x.product.price

                for y in x.cart_option_set.all():
                    total_unit_price += y.option.additional_price
                    selection += y.option.selection + ", "

                for y in x.cart_addon_set.all():
                    total_unit_price += y.addon.additional_price
                    selection += y.addon.addon_item + ", "
                
                order.order_item_set.create(
                    product=x.product,
                    product_name=x.product.name,
                    selection=selection[:-2],
                    quantity=x.quantity,
                    price=total_unit_price,
                    total=x.quantity * total_unit_price
                )

                order_total += x.quantity * total_unit_price

            order.total = order_total
            order.save()

            cart_items.delete()
            
            return JsonResponse({"url": reverse('orders:order', args=[order.id])})

        else:
            return JsonResponse({})

    else:       # request.method == "GET" (show all orders)
        pending_payment = request.user.order_set.filter(status="pending")
        active_orders = request.user.order_set.filter(status="paid")
        past_orders = request.user.order_set.filter(status="completed")

        context = {
            "pending_payment": pending_payment,
            "active_orders": active_orders,
            "past_orders": past_orders,
        }

        return render(request, "orders/orders.html", context)

@login_required
def order(request, order_id):
    if request.method == "POST":
        try:
            order = request.user.order_set.get(pk=order_id, status="pending")
        except:
            return HttpResponseBadRequest()

        last_transaction = request.user.wallet_set.order_by('date').last()

        # ensure server does not process those order with amount larger than wallet balance
        if order.total > last_transaction.balance:
            return HttpResponseBadRequest()

        request.user.wallet_set.create(user=request.user, description=f"Order Number: #{order_id}", value=order.total, balance=last_transaction.balance - order.total)

        order.status = "paid"
        order.save()

        profile = request.user.profile
        profile.cumulative_order_number += 1
        profile.cumulative_order_value += order.total
        profile.save()

        return JsonResponse({})

    else:
        try:
            order = request.user.order_set.get(pk=order_id)
        except:
            raise Http404("Order does not exist")

        wallet_balance = 0

        last_transaction = request.user.wallet_set.order_by('date').last()

        if last_transaction:
            wallet_balance = last_transaction.balance

        context = {
            "order": order,
            "wallet_balance": wallet_balance
        }

        return render(request, "orders/order.html", context)

@login_required
def cancel(request):
    order_id = int(request.POST["order_id"])

    try:
        order = request.user.order_set.get(pk=order_id, status="pending")
    except:
        return HttpResponseBadRequest()
    else:
        order.status = "canceled"
        order.save()

    return JsonResponse({})

