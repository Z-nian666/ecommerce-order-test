import uuid
from api_test.common.request_util import http_client
from api_test.common.assert_util import AssertUtil
from api_test.common.error_code import (
    STOCK_NOT_ENOUGH,
    ORDER_NOT_EXIST,
    GOODS_NOT_EXIST,
    PARAM_INVALID,
    NOT_LOGIN,
    SUCCESS,
    ORDER_STATUS_ERROR
)

BASE_URL = "http://127.0.0.1:8000"


def test_create_order_success(api_headers, admin_headers):
    """【正向功能】正常下单-核心业务流程"""
    # 前置：管理员重置商品库存（普通用户无权限修改）
    http_client.send(
        "put",
        "/api/goods/1/",
        headers=admin_headers,
        json={"name": "iPhone 15", "price": 5999, "stock": 100}
    )

    json_data = {
        "goods_id": 1,
        "request_id": str(uuid.uuid4())
    }
    resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=json_data)
    AssertUtil.assert_code(resp, SUCCESS)
    AssertUtil.assert_key_exist(resp, "id")
    AssertUtil.assert_key_exist(resp, "order_no")


def test_create_order_param_missing(api_headers):
    """【参数异常】必填字段缺失，验证参数校验拦截"""
    # 缺失 goods_id
    data1 = {"request_id": str(uuid.uuid4())}
    resp1 = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data1)
    AssertUtil.assert_code(resp1, PARAM_INVALID)

    # 缺失 request_id
    data2 = {"goods_id": 1}
    resp2 = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data2)
    AssertUtil.assert_code(resp2, PARAM_INVALID)


def test_create_order_param_illegal(api_headers):
    """【参数异常】非法参数类型，验证参数校验拦截"""
    data = {"goods_id": -1, "request_id": str(uuid.uuid4())}
    resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data)
    AssertUtil.assert_code(resp, PARAM_INVALID)


def test_create_order_goods_not_exist(api_headers):
    """【业务边界】下单商品不存在，验证业务拦截"""
    data = {"goods_id": 9999, "request_id": str(uuid.uuid4())}
    resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data)
    AssertUtil.assert_code(resp, GOODS_NOT_EXIST)


def test_create_order_stock_zero(api_headers, admin_headers):
    """【业务边界】库存为0下单，验证库存不足拦截"""
    # 前置：管理员将商品库存置为0
    http_client.send(
        "put",
        "/api/goods/1/",
        headers=admin_headers,
        json={"name": "iPhone 15", "price": 5999, "stock": 0}
    )

    data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data)
    AssertUtil.assert_code(resp, STOCK_NOT_ENOUGH)


def test_create_order_overstock(api_headers, admin_headers):
    """【业务场景】连续下单耗尽库存，最后一次触发库存不足"""
    # 前置：管理员重置库存为2
    http_client.send(
        "put",
        "/api/goods/1/",
        headers=admin_headers,
        json={"name": "iPhone 15", "price": 5999, "stock": 2}
    )

    last_resp = None
    # 连续下单3次，必然耗尽库存
    for _ in range(3):
        data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
        last_resp = http_client.send(
            "post",
            "/api/orders/create/",
            headers=api_headers,
            json=data
        )
        resp_data = last_resp.json()
        if resp_data["code"] != SUCCESS:
            break

    AssertUtil.assert_code(last_resp, STOCK_NOT_ENOUGH)
    # 验证最终库存为0（商品已改造统一格式，走data层）
    final_resp = http_client.send("get", "/api/goods/1/", headers=admin_headers)
    final_stock = final_resp.json()["data"]["stock"]
    assert final_stock == 0


def test_order_detail_not_exist(api_headers):
    """【业务边界】查询不存在的订单，返回订单不存在错误码"""
    order_id = 9999
    resp = http_client.send("get", f"/api/orders/{order_id}/", headers=api_headers)
    AssertUtil.assert_code(resp, ORDER_NOT_EXIST)


def test_order_not_login():
    """【权限校验】未登录状态下单，验证鉴权拦截"""
    data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    resp = http_client.send("post", "/api/orders/create/", headers={}, json=data)
    AssertUtil.assert_code(resp, NOT_LOGIN)


def test_order_idempotent(api_headers, admin_headers):
    """【幂等专项】同一request_id多次下单，仅生成1笔订单、扣1次库存"""
    # 前置：管理员重置商品库存
    http_client.send(
        "put",
        "/api/goods/1/",
        headers=admin_headers,
        json={"name": "iPhone 15", "price": 5999, "stock": 10}
    )
    before_stock = http_client.send("get", "/api/goods/1/", headers=admin_headers).json()["data"]["stock"]

    req_id = str(uuid.uuid4())
    order_ids = []
    for _ in range(3):
        data = {"goods_id": 1, "request_id": req_id}
        resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data)
        AssertUtil.assert_code(resp, SUCCESS)
        order_ids.append(resp.json()["data"]["id"])

    # 验证：3次请求返回同一订单
    assert len(set(order_ids)) == 1, "重复请求生成不同订单，幂等机制失效"
    # 验证：库存仅扣减1次
    after_stock = http_client.send("get", "/api/goods/1/", headers=admin_headers).json()["data"]["stock"]
    assert before_stock - after_stock == 1, "库存扣减次数异常，幂等机制失效"


def test_order_overstock_verify(api_headers, admin_headers):
    """【超卖专项】库存耗尽后下单失败，验证不会超卖"""
    stock_num = 1
    http_client.send(
        "put",
        "/api/goods/1/",
        headers=admin_headers,
        json={"name": "iPhone 15", "price": 5999, "stock": stock_num}
    )

    last_resp = None
    for _ in range(stock_num + 1):
        data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
        last_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data)

    AssertUtil.assert_code(last_resp, STOCK_NOT_ENOUGH)
    final_resp = http_client.send("get", "/api/goods/1/", headers=admin_headers)
    final_stock = final_resp.json()["data"]["stock"]
    assert final_stock == 0


def test_order_pay_success(api_headers, admin_headers):
    """【正向流程】待支付订单支付成功，状态变为已支付"""
    # 前置：重置库存+下单
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]

    # 执行支付
    pay_resp = http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers)
    AssertUtil.assert_code(pay_resp, SUCCESS)
    assert pay_resp.json()["data"]["status"] == 2  # 2=已支付


def test_order_pay_status_error(api_headers, admin_headers):
    """【异常场景】已支付订单重复支付，状态拦截生效"""
    # 前置：下单并支付
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]
    http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers)

    # 重复支付，预期报错
    pay_resp = http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers)
    AssertUtil.assert_code(pay_resp, ORDER_STATUS_ERROR)


def test_order_cancel_success(api_headers, admin_headers):
    """【正向流程】待支付订单取消成功，库存回补"""
    # 前置：重置库存+下单
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    before_stock = http_client.send("get", "/api/goods/1/", headers=admin_headers).json()["data"]["stock"]

    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]

    # 取消订单
    cancel_resp = http_client.send("post", f"/api/orders/{order_id}/cancel/", headers=api_headers)
    AssertUtil.assert_code(cancel_resp, SUCCESS)
    assert cancel_resp.json()["data"]["status"] == 5  # 5=已取消

    # 验证库存回补
    after_stock = http_client.send("get", "/api/goods/1/", headers=admin_headers).json()["data"]["stock"]
    assert after_stock == before_stock, "取消订单后库存未正确回补"


def test_order_refund_success(api_headers, admin_headers):
    """【正向流程】已支付订单退款成功，库存回补"""
    # 前置：重置库存+下单+支付
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    before_stock = http_client.send("get", "/api/goods/1/", headers=admin_headers).json()["data"]["stock"]

    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]
    http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers)

    # 申请退款
    refund_resp = http_client.send("post", f"/api/orders/{order_id}/refund/", headers=api_headers)
    AssertUtil.assert_code(refund_resp, SUCCESS)
    assert refund_resp.json()["data"]["status"] == 6  # 6=已退款

    # 验证库存回补
    after_stock = http_client.send("get", "/api/goods/1/", headers=admin_headers).json()["data"]["stock"]
    assert after_stock == before_stock, "退款后库存未正确回补"


def test_order_pay_after_cancel(api_headers, admin_headers):
    """【异常场景】订单取消后重复支付，状态拦截生效"""
    # 1.下单
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    res = http_client.send("post", "/api/orders/create/", headers=api_headers, json=data)
    order_id = res.json()["data"]["id"]
    # 2.取消订单
    http_client.send("post", f"/api/orders/{order_id}/cancel/", headers=api_headers)
    # 3.尝试支付已取消订单
    resp = http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers)
    AssertUtil.assert_code(resp, ORDER_STATUS_ERROR)


def test_order_refund_before_pay(api_headers, admin_headers):
    """【异常场景】待支付订单直接申请退款，状态拦截生效"""
    # 前置：下单（不支付）
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]

    # 待支付直接退款，预期拦截
    refund_resp = http_client.send("post", f"/api/orders/{order_id}/refund/", headers=api_headers)
    AssertUtil.assert_code(refund_resp, ORDER_STATUS_ERROR)


def test_order_refund_repeat(api_headers, admin_headers):
    """【异常场景】已退款订单重复申请退款，状态拦截生效"""
    # 前置：下单→支付→退款
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]
    http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers)
    http_client.send("post", f"/api/orders/{order_id}/refund/", headers=api_headers)

    # 重复退款，预期拦截
    refund_resp = http_client.send("post", f"/api/orders/{order_id}/refund/", headers=api_headers)
    AssertUtil.assert_code(refund_resp, ORDER_STATUS_ERROR)


def test_order_cancel_after_paid(api_headers, admin_headers):
    """【异常场景】已支付订单直接取消，状态拦截生效（需走退款流程）"""
    # 前置：下单→支付
    http_client.send("put", "/api/goods/1/", headers=admin_headers,
                     json={"name": "iPhone 15", "price": 5999, "stock": 10})
    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]
    http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers)

    # 已支付直接取消，预期拦截
    cancel_resp = http_client.send("post", f"/api/orders/{order_id}/cancel/", headers=api_headers)
    AssertUtil.assert_code(cancel_resp, ORDER_STATUS_ERROR)
