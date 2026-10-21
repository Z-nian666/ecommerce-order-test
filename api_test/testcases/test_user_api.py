from api_test.common.request_util import http_client
from api_test.common.assert_util import AssertUtil
from api_test.common.error_code import SUCCESS, NOT_LOGIN, PARAM_INVALID


def test_user_login_success():
    """【正向功能】正常登录，获取Token"""
    login_data = {
        "username": "znn",
        "password": "znn123456"
    }
    resp = http_client.send("post", "/api/users/login/", json=login_data)
    AssertUtil.assert_code(resp, SUCCESS)
    AssertUtil.assert_key_exist(resp, "access")


def test_user_login_param_wrong():
    """【异常场景】密码错误，登录失败"""
    login_data = {
        "username": "znn",
        "password": "wrongpass"
    }
    resp = http_client.send("post", "/api/users/login/", json=login_data)
    AssertUtil.assert_code(resp, PARAM_INVALID)


def test_user_info_query(api_headers):
    """【正向功能】登录后查询用户信息"""
    resp = http_client.send("get", "/api/users/info/", headers=api_headers)
    AssertUtil.assert_code(resp, SUCCESS)
    AssertUtil.assert_key_exist(resp, "username")


def test_user_info_not_login():
    """【权限校验】未登录查询用户信息，鉴权拦截"""
    resp = http_client.send("get", "/api/users/info/", headers={})
    AssertUtil.assert_code(resp, NOT_LOGIN)
