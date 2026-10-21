from django.db import IntegrityError, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from goods.models import Goods


class OrderCreateView(APIView):
    """创建订单：带幂等控制 + 行锁超卖防护"""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        goods_id = request.data.get("goods_id")
        request_id = request.data.get("request_id")

        # 1. 前置幂等校验
        exist_order = Order.objects.filter(request_id=request_id).first()
        if exist_order:
            return Response({
                "code": 0,
                "msg": "下单成功",
                "data": {
                    "id": exist_order.id,
                    "order_no": exist_order.order_no,
                    "status": exist_order.status
                }
            })

        try:
            # 2. 行锁扣库存，防超卖
            goods = Goods.objects.select_for_update().get(id=goods_id)
            if goods.stock <= 0:
                return Response({"code": 1, "msg": "库存不足"})

            goods.stock -= 1
            goods.save()

            # 3. 创建订单，存入幂等键
            order = Order.objects.create(
                user=request.user,
                goods=goods,
                total_price=goods.price,
                request_id=request_id,
                status=Order.STATUS_PENDING
            )

            return Response({
                "code": 0,
                "msg": "下单成功",
                "data": {
                    "id": order.id,
                    "order_no": order.order_no,
                    "status": order.status
                }
            })

        except IntegrityError:
            # 4. 并发兜底：唯一约束冲突，直接返回已有订单
            transaction.set_rollback(True)
            order = Order.objects.get(request_id=request_id)
            return Response({
                "code": 0,
                "msg": "下单成功",
                "data": {
                    "id": order.id,
                    "order_no": order.order_no,
                    "status": order.status
                }
            })


class OrderDetailView(APIView):
    """订单详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
            return Response({
                "code": 0,
                "msg": "查询成功",
                "data": {
                    "id": order.id,
                    "order_no": order.order_no,
                    "total_price": str(order.total_price),
                    "status": order.status,
                    "create_time": order.create_time
                }
            })
        except Order.DoesNotExist:
            return Response({"code": 1, "msg": "订单不存在"})


class OrderPayView(APIView):
    """订单支付"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
            if order.status != Order.STATUS_PENDING:
                return Response({"code": 1, "msg": "订单状态异常，无法支付"})
            order.status = Order.STATUS_PAID
            order.save()
            return Response({"code": 0, "msg": "支付成功"})
        except Order.DoesNotExist:
            return Response({"code": 1, "msg": "订单不存在"})


class OrderCancelView(APIView):
    """取消订单"""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
            if order.status != Order.STATUS_PENDING:
                return Response({"code": 1, "msg": "订单状态异常，无法取消"})

            # 归还库存
            goods = Goods.objects.select_for_update().get(id=order.goods_id)
            goods.stock += 1
            goods.save()

            order.status = Order.STATUS_CANCELLED
            order.save()
            return Response({"code": 0, "msg": "取消成功"})
        except Order.DoesNotExist:
            return Response({"code": 1, "msg": "订单不存在"})


class OrderRefundView(APIView):
    """订单退款"""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
            if order.status != Order.STATUS_PAID:
                return Response({"code": 1, "msg": "订单状态异常，无法退款"})

            # 归还库存
            goods = Goods.objects.select_for_update().get(id=order.goods_id)
            goods.stock += 1
            goods.save()

            order.status = Order.STATUS_REFUNDED
            order.save()
            return Response({"code": 0, "msg": "退款成功"})
        except Order.DoesNotExist:
            return Response({"code": 1, "msg": "订单不存在"})
