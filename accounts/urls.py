from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('profile/', views.profile, name="profile"),
    path('change_password/', views.change_password, name="change_password"),
    path('wallet/', views.wallet, name="wallet"),
    path('cancel/', views.cancel, name="cancel"),
    path('topup-manage/', views.topup_manage, name="topup-manage")
]
