import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. 管理员登录获取token
login_data = {"username": "admin", "password": "你的管理员密码"}
resp = requests.post(f"{BASE_URL}/api/users/login/", json=login_data)
token = resp.json()["data"]["access"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 重置商品1的库存为100
goods_data = {"name": "iPhone 15", "price": 5999, "stock": 100}
resp = requests.put(f"{BASE_URL}/api/goods/1/", json=goods_data, headers=headers)
print("重置结果：", resp.json())
