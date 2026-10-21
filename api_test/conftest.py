import sys
import os
import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def api_headers():
    """普通用户请求头（纯普通账号，无管理员权限）"""
    login_data = {
        "username": "znn",
        "password": "znn123456"
    }
    resp = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
    resp_data = resp.json()
    # 兼容新旧格式取token
    if "data" in resp_data:
        token = resp_data["data"]["access"]
    else:
        token = resp_data["access"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }



@pytest.fixture(scope="session")
def admin_headers():
    """管理员请求头，兼容新旧格式"""
    login_data = {
        "username": "zn",
        "password": "123456"
    }
    resp = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
    resp_data = resp.json()
    if "data" in resp_data:
        token = resp_data["data"]["access"]
    else:
        token = resp_data["access"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="session")
def api_headers_b():
    """第二个普通用户请求头，用于水平越权测试"""
    login_data = {
        "username": "testuser2",
        "password": "test123456"
    }
    resp = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
    resp_data = resp.json()
    if "data" in resp_data:
        token = resp_data["data"]["access"]
    else:
        token = resp_data["access"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
