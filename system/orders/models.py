from django.db import models
from django.contrib.auth.models import User
from goods.models import Goods


class Order(models.Model):
    # 订单状态枚举
    STATUS_PENDING = 1    # 待支付
    STATUS_PAID = 2       # 已支付
    STATUS_SHIPPED = 3    # 已发货
    STATUS_COMPLETED = 4  # 已完成
    STATUS_CANCELLED = 5  # 已取消
    STATUS_REFUNDED = 6   # 已退款

    STATUS_CHOICES = [
        (STATUS_PENDING, "待支付"),
        (STATUS_PAID, "已支付"),
        (STATUS_SHIPPED, "已发货"),
        (STATUS_COMPLETED, "已完成"),
        (STATUS_CANCELLED, "已取消"),
        (STATUS_REFUNDED, "已退款"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="下单用户")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")
    order_no = models.CharField(max_length=64, unique=True, verbose_name="订单号")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单总价")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="订单状态")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # 新增：幂等请求ID，数据库唯一索引兜底幂等
    request_id = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="幂等请求ID",
        null=True,
        default=None
    )

    class Meta:
        db_table = "order"
        verbose_name = "订单表"
        ordering = ["-create_time"]