from .models import Order
from goods.models import Goods
from common.exceptions import BusinessException
from common.error_code import (
    STOCK_NOT_ENOUGH,
    GOODS_NOT_EXIST,
    ORDER_NOT_EXIST,
    ORDER_STATUS_ERROR
)


def create_order(user, goods_id, request_id):
    """创建订单：幂等校验 → 商品校验 → 库存扣减 → 生成订单"""
    order_no = f"ORD{request_id}"

    # 幂等校验
    exist_order = Order.objects.filter(order_no=order_no).first()
    if exist_order:
        return exist_order

    try:
        goods = Goods.objects.select_for_update().get(id=goods_id)
    except Goods.DoesNotExist:
        raise BusinessException(msg="商品不存在", code=GOODS_NOT_EXIST)

    if goods.stock <= 0:
        raise BusinessException(msg="库存不足", code=STOCK_NOT_ENOUGH)

    # 扣减库存
    goods.stock -= 1
    goods.save()

    # 生成订单
    order = Order.objects.create(
        user=user,
        goods=goods,
        order_no=order_no,
        status=Order.STATUS_PENDING,
        total_price=goods.price
    )
    return order


def pay_order(user, order_id):
    """订单支付：仅待支付状态可支付"""
    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        raise BusinessException(msg="订单不存在", code=ORDER_NOT_EXIST)

    if order.status != Order.STATUS_PENDING:
        raise BusinessException(msg="当前订单状态不可支付", code=ORDER_STATUS_ERROR)

    order.status = Order.STATUS_PAID
    order.save()
    return order


def cancel_order(user, order_id):
    """取消订单：仅待支付可取消，取消后库存回补"""
    try:
        order = Order.objects.select_for_update().get(id=order_id, user=user)
    except Order.DoesNotExist:
        raise BusinessException(msg="订单不存在", code=ORDER_NOT_EXIST)

    if order.status != Order.STATUS_PENDING:
        raise BusinessException(msg="仅待支付订单可取消", code=ORDER_STATUS_ERROR)

    # 库存回补
    goods = order.goods
    goods.stock += 1
    goods.save()

    order.status = Order.STATUS_CANCELLED
    order.save()
    return order


def refund_order(user, order_id):
    """申请退款：仅已支付订单可退款，退款后库存回补"""
    try:
        order = Order.objects.select_for_update().get(id=order_id, user=user)
    except Order.DoesNotExist:
        raise BusinessException(msg="订单不存在", code=ORDER_NOT_EXIST)

    if order.status != Order.STATUS_PAID:
        raise BusinessException(msg="仅已支付订单可申请退款", code=ORDER_STATUS_ERROR)

    # 库存回补
    goods = order.goods
    goods.stock += 1
    goods.save()

    order.status = Order.STATUS_REFUNDED
    order.save()
    return order
