from rest_framework import serializers
from .models import Order


class OrderCreateSerializer(serializers.Serializer):
    goods_id = serializers.IntegerField(min_value=1, error_messages={"min_value": "商品ID必须为正整数"})
    request_id = serializers.CharField(max_length=64, error_messages={"max_length": "请求ID长度不能超过64位"})


class OrderSerializer(serializers.ModelSerializer):
    # 从关联的商品表取名称和价格，不是订单表的数据库字段
    goods_name = serializers.CharField(source='goods.name', read_only=True)
    goods_price = serializers.DecimalField(source='goods.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        # 只保留模型里真实存在的字段，去掉不存在的 amount
        fields = ["id", "order_no", "goods_name", "goods_price", "status", "create_time"]

from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """订单信息返回序列化器"""
    class Meta:
        model = Order
        fields = ["id", "order_no", "total_price", "status", "create_time"]


class OrderCreateSerializer(serializers.Serializer):
    """创建订单入参校验序列化器"""
    goods_id = serializers.IntegerField(required=True, min_value=1, error_messages={
        "required": "商品ID不能为空",
        "min_value": "商品ID必须大于0"
    })
    request_id = serializers.CharField(required=True, max_length=64, error_messages={
        "required": "请求ID不能为空",
        "max_length": "请求ID长度不能超过64位"
    })
