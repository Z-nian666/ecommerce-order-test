from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # 新增这一行！
    path('api/users/', include('users.urls')),
    path('api/goods/', include('goods.urls')),
    path('api/orders/', include('orders.urls')),
]
