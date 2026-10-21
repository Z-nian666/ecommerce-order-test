import requests
from api_test.config.settings import BASE_URL

class HttpRequest:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_URL

    def send(self, method, path, data=None, json=None, headers=None, params=None):
        base = self.base_url.rstrip("/")
        path = path.lstrip("/")
        url = f"{base}/{path}"
        # 调试打印
        print(f"==== DEBUG 完整请求URL: {url}, method:{method}")
        resp = self.session.request(method=method, url=url, data=data, json=json, headers=headers, params=params)
        print(f"==== DEBUG 响应状态码: {resp.status_code}")
        return resp

# 全局请求单例
http_client = HttpRequest()

def get_resp_json(resp):
    """安全解析响应json，解析失败返回None"""
    try:
        return resp.json()
    except Exception:
        return None
