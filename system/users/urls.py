from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="user_register"),
    path("login/", views.LoginView.as_view(), name="user_login"),
    path("info/", views.UserInfoView.as_view(), name="user_info"),
]
