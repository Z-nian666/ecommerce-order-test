from rest_framework import serializers
from .models import Goods


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ["id", "name", "price", "stock"]
        extra_kwargs = {
            "name": {"required": True, "error_messages": {"required": "商品名称不能为空"}},
            "price": {"required": True, "min_value": 0.01, "error_messages": {
                "required": "商品价格不能为空",
                "min_value": "商品价格必须大于0"
            }},
            "stock": {"required": True, "min_value": 0, "error_messages": {
                "required": "库存不能为空",
                "min_value": "库存不能为负数"
            }}
        }
