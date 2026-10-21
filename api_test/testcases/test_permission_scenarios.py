import uuid

from api_test.common.request_util import http_client
from api_test.common.assert_util import AssertUtil
from api_test.common.error_code import PERMISSION_DENIED, NOT_LOGIN, ORDER_NOT_EXIST


def test_vertical_privilege_violation_goods(api_headers):
    """【垂直越权】普通用户调用管理员商品修改接口，权限拦截生效"""
    data = {"name": "越权修改", "price": 1, "stock": 1}
    resp = http_client.send("put", "/api/goods/1/", headers=api_headers, json=data)
    AssertUtil.assert_code(resp, PERMISSION_DENIED)


# def test_horizontal_privilege_violation_order(api_headers, other_user_order):
#     """【水平越权】普通用户查询他人订单，越权拦截生效"""
#     resp = http_client.send(f"get", f"/api/orders/{other_user_order}/", headers=api_headers)
#     AssertUtil.assert_code(resp, ORDER_NOT_EXIST)



def test_not_login_access_goods():
    """【权限校验】未登录状态查询商品，鉴权拦截"""
    resp = http_client.send("get", "/api/goods/1/", headers={})
    AssertUtil.assert_code(resp, NOT_LOGIN)


def test_not_login_create_order():
    """【权限校验】未登录状态下单，鉴权拦截"""
    data = {"goods_id": 1, "request_id": "test_req_001"}
    resp = http_client.send("post", "/api/orders/create/", headers={}, json=data)
    AssertUtil.assert_code(resp, NOT_LOGIN)

def test_horizontal_privilege_violation_order(api_headers, api_headers_b):
    """【水平越权】用户B查询/操作用户A的订单，越权拦截生效"""
    # 1. 用户A创建订单
    order_data = {"goods_id": 1, "request_id": str(uuid.uuid4())}
    create_resp = http_client.send("post", "/api/orders/create/", headers=api_headers, json=order_data)
    order_id = create_resp.json()["data"]["id"]

    # 2. 用户B尝试查询A的订单
    get_resp = http_client.send("get", f"/api/orders/{order_id}/", headers=api_headers_b)
    AssertUtil.assert_code(get_resp, PERMISSION_DENIED)

    # 3. 用户B尝试支付A的订单
    pay_resp = http_client.send("post", f"/api/orders/{order_id}/pay/", headers=api_headers_b)
    AssertUtil.assert_code(pay_resp, PERMISSION_DENIED)

    # 4. 用户B尝试取消A的订单
    cancel_resp = http_client.send("post", f"/api/orders/{order_id}/cancel/", headers=api_headers_b)
    AssertUtil.assert_code(cancel_resp, PERMISSION_DENIED)

