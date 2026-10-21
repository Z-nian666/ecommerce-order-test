import uuid
from api_test.common.request_util import http_client
from api_test.common.assert_util import AssertUtil
from api_test.common.error_code import SUCCESS, PARAM_INVALID, PERMISSION_DENIED, ORDER_NOT_EXIST


def test_goods_list_query(admin_headers):
    """【正向功能】商品列表查询"""
    resp = http_client.send("get", "/api/goods/", headers=admin_headers)
    AssertUtil.assert_code(resp, SUCCESS)


def test_goods_detail_query(admin_headers):
    """【正向功能】商品详情查询"""
    resp = http_client.send("get", "/api/goods/1/", headers=admin_headers)
    AssertUtil.assert_code(resp, SUCCESS)
    AssertUtil.assert_key_exist(resp, "name")
    AssertUtil.assert_key_exist(resp, "stock")


def test_goods_create_success(admin_headers):
    """【正向功能】管理员新增商品"""
    data = {
        "name": f"测试商品{uuid.uuid4().hex[:8]}",
        "price": 99.99,
        "stock": 10
    }
    resp = http_client.send("post", "/api/goods/", headers=admin_headers, json=data)
    AssertUtil.assert_code(resp, SUCCESS)
    AssertUtil.assert_key_exist(resp, "id")


def test_goods_update_success(admin_headers):
    """【正向功能】管理员修改商品信息"""
    data = {
        "name": "iPhone 15 标准版",
        "price": 5999,
        "stock": 200
    }
    resp = http_client.send("put", "/api/goods/1/", headers=admin_headers, json=data)
    AssertUtil.assert_code(resp, SUCCESS)
    # 验证修改后数据生效
    detail_resp = http_client.send("get", "/api/goods/1/", headers=admin_headers)
    assert detail_resp.json()["data"]["stock"] == 200


def test_goods_param_missing(admin_headers):
    """【参数异常】新增商品必填字段缺失"""
    # 缺失商品名称
    data1 = {"price": 100, "stock": 10}
    resp1 = http_client.send("post", "/api/goods/", headers=admin_headers, json=data1)
    AssertUtil.assert_code(resp1, PARAM_INVALID)

    # 缺失库存字段
    data2 = {"name": "测试商品", "price": 100}
    resp2 = http_client.send("post", "/api/goods/", headers=admin_headers, json=data2)
    AssertUtil.assert_code(resp2, PARAM_INVALID)


def test_goods_param_illegal(admin_headers):
    """【参数异常】非法参数入参校验"""
    # 价格为负数
    data = {"name": "测试商品", "price": -10, "stock": 10}
    resp = http_client.send("post", "/api/goods/", headers=admin_headers, json=data)
    AssertUtil.assert_code(resp, PARAM_INVALID)


def test_goods_not_exist(admin_headers):
    """【业务边界】查询不存在的商品"""
    resp = http_client.send("get", "/api/goods/9999/", headers=admin_headers)
    AssertUtil.assert_code(resp, ORDER_NOT_EXIST)


def test_goods_user_no_permission(api_headers):
    """【权限校验】普通用户无权限新增商品"""
    data = {"name": "越权测试商品", "price": 100, "stock": 10}
    resp = http_client.send("post", "/api/goods/", headers=api_headers, json=data)
    AssertUtil.assert_code(resp, PERMISSION_DENIED)


def test_goods_user_update_no_permission(api_headers):
    """【权限校验】普通用户无权限修改商品"""
    data = {"name": "越权修改", "price": 1, "stock": 1}
    resp = http_client.send("put", "/api/goods/1/", headers=api_headers, json=data)
    AssertUtil.assert_code(resp, PERMISSION_DENIED)
