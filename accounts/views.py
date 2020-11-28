from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, reverse
from .models import Profile, Wallet, Topup
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods, require_POST

# Create your views here.

@require_POST
def register(request):
    name = request.POST["name"]
    email = request.POST["email"].lower()
    mobile = request.POST["mobile"]
    company_name = request.POST["company_name"]
    password = request.POST["password"]

    data = {
        "status": False
    }

    # Check if the email address valid
    try:
        validate_email(email)
    except ValidationError:
        data["message"] = "Enter a valid email address."
        return JsonResponse(data)

    if len(mobile) < 11 or len(mobile) > 13 or not mobile[1:].isnumeric():
        data["message"] = "Enter a valid mobile number."
        return JsonResponse(data)

    # Malaysia contact number country code is +60
    if mobile[0:3] != "+60":
        data["message"] = "Please include +60 for your mobile number."
        return JsonResponse(data)

    # Check if the email registered
    try:
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
    except:
        data["message"] = "Email provided has been registered."
        return JsonResponse(data)
    else:
        user.save()
    
    # Update mobile and company name into Profile table
    profile = Profile(user=user, mobile=mobile, company_name=company_name)
    profile.save()

    # Login the user once the account is registered successfully and redirect to homepage
    login(request, authenticate(request, username=email, password=password))
    
    data["status"] = True

    return JsonResponse(data)

@require_POST
def login_view(request):
    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        data = {
            "status": True,
        }
        return JsonResponse(data)
    else:
        data = {
            "status": False,
            "message": "Either your Email or password seems to be incorrect."
        }
        return JsonResponse(data)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("orders:index"))

@login_required
def profile(request):
    if request.method == "POST":
        # to ensure no blank input
        for i in request.POST.values():
            if len(i) == 0:
                return HttpResponseBadRequest()

        name = request.POST["name"]
        email = request.POST["email"].lower()
        mobile = request.POST["mobile"]
        company_name = request.POST["company_name"]

        current_user = request.user
        
        data = {
            "status": False,
            "email": request.user.email,
        }

        try:
            data["mobile"] = current_user.profile.mobile
        except:
            data["mobile"] = ""

        # Check if the email address valid
        try:
            validate_email(email)
        except ValidationError:
            data["message"] = "Enter a valid email address."
            return JsonResponse(data)

        if len(mobile) < 11 or len(mobile) > 13 or not mobile[1:].isnumeric():
            data["message"] = "Enter a valid mobile number."
            return JsonResponse(data)

        # Malaysia contact number country code is +60
        if mobile[0:3] != "+60":
            data["message"] = "Please include +60 for your mobile number."
            return JsonResponse(data)

        try:
            other_user = User.objects.get(username=email)
        except:
            current_user.first_name = name
            current_user.username = email
            current_user.email = email
            current_user.save()
            try:
                current_user.profile.mobile = mobile
                current_user.profile.company_name = company_name
                current_user.profile.save()
            except:
                Profile(user=current_user, mobile=mobile, company_name=company_name).save()

            data["status"] = True
            data["message"] = "Profile has been updated."
            data["name"] = current_user.first_name
            return JsonResponse(data)
        else:
            if other_user == current_user:
                current_user.first_name = name
                current_user.username = email
                current_user.email = email
                current_user.save()
                try:
                    current_user.profile.mobile = mobile
                    current_user.profile.company_name = company_name
                    current_user.profile.save()
                except:
                    Profile(user=current_user, mobile=mobile, company_name=company_name).save()

                data["status"] = True
                data["message"] = "Profile has been updated."
                data["name"] = current_user.first_name
                return JsonResponse(data)

            else:
                data["message"] = "Email provided has been registered."
                return JsonResponse(data)
    
    else:   # request.method == "GET"
        return render(request, 'registration/profile.html')

@require_POST
def change_password(request):
    # to ensure no blank input
    for i in request.POST.values():
        if len(i) == 0:
            return HttpResponseBadRequest()

    user = request.user
    current_password = request.POST["current_password"]
    new_password = request.POST["new_password"]

    data = {
        "status": False
    }

    if check_password(current_password, user.password):
        user.password = make_password(new_password)
        user.save()

        login(request, authenticate(request, username=user.username, password=new_password))
        data["status"] = True
        data["message"] = "Password has been changed."
        return JsonResponse(data)

    else:
        data["message"] = "Current password incorrect."
        return JsonResponse(data)

@login_required
def wallet(request):
    if request.method == "POST":
        value = int(request.POST["value"])

        request.user.topup_set.create(value=value)

        return HttpResponseRedirect(reverse("accounts:wallet"))

    else:
        topup = request.user.topup_set.filter(status="pending")
        wallet = request.user.wallet_set.all()
                
        wallet_balance = 0

        last_transaction = request.user.wallet_set.order_by('date').last()

        if last_transaction:
            wallet_balance = last_transaction.balance

        context = {
            "topup": topup,
            "wallet": wallet,
            "balance": wallet_balance
        }

        return render(request, "registration/wallet.html", context)


@require_POST
def cancel(request):        # cancel top up request
    topup_id = int(request.POST["topup_id"])
    topup = request.user.topup_set.get(pk=topup_id)

    topup.status = "canceled"
    topup.save()

    return JsonResponse({})

# staff view for manage top up request
def topup_manage(request):
    if request.user.is_superuser or request.user.is_staff:
        if request.method == "POST":
            topup_id = int(request.POST["topup_id"])

            topup = Topup.objects.get(pk=topup_id)

            last_transaction = topup.user.wallet_set.order_by('date').last()

            # if wallet has no transaction, balance = topup value
            if last_transaction:
                Wallet(user=topup.user, description="Top up", value=topup.value, balance=last_transaction.balance + topup.value).save()
            else:
                Wallet(user=topup.user, description="Top up", value=topup.value, balance=topup.value).save()

            topup.status = "topped up"
            topup.save()

            return JsonResponse({})

        else:
            topup_request = Topup.objects.filter(status="pending")

            context = {
                "topup_request": topup_request,
            }

            return render(request, "registration/topup-manage.html", context)
    else:
        return HttpResponseForbidden()

