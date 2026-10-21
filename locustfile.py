from locust import HttpUser, task, between
import uuid
import json

BASE_HEADERS = {"Content-Type": "application/json"}
TEST_USER = {"username": "znn", "password": "znn123456"}
GOODS_ID = 1


class OrderTestUser(HttpUser):
    wait_time = between(0.1, 0.3)
    headers = None

    def on_start(self):
        """每个虚拟用户启动前先登录获取token"""
        try:
            resp = self.client.post(
                "/api/users/login/",
                data=json.dumps(TEST_USER),
                headers=BASE_HEADERS
            )
            print("登录响应：", resp.text)
            token = resp.json()["data"]["access"]
            self.headers = {
                **BASE_HEADERS,
                "Authorization": f"Bearer {token}"
            }
            print("用户登录成功")
        except Exception as e:
            print("登录失败：", e)

    @task(3)
    def test_create_order_normal(self):
        """普通下单并发：验证超卖防护"""
        if not self.headers:
            return
        request_id = str(uuid.uuid4())
        self.client.post(
            "/api/orders/create/",
            data=json.dumps({"goods_id": GOODS_ID, "request_id": request_id}),
            headers=self.headers
        )

    @task(1)
    def test_create_order_idempotent(self):
        """幂等并发：同一个request_id并发请求，验证只生成1笔订单"""
        if not self.headers:
            return
        request_id = "idempotent-test-" + str(uuid.uuid4())[:8]
        for _ in range(3):
            self.client.post(
                "/api/orders/create/",
                data=json.dumps({"goods_id": GOODS_ID, "request_id": request_id}),
                headers=self.headers
            )