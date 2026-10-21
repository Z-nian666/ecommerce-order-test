from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("<int:pk>/pay/", views.OrderPayView.as_view(), name="order_pay"),
    path("<int:pk>/cancel/", views.OrderCancelView.as_view(), name="order_cancel"),
    path("<int:pk>/refund/", views.OrderRefundView.as_view(), name="order_refund"),
]
