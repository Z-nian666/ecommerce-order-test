class AssertUtil:
    @staticmethod
    def _safe_parse(resp):
        """安全解析响应，兼容所有格式，永不报错"""
        try:
            data = resp.json()
        except Exception:
            assert False, f"响应解析失败，HTTP状态码：{resp.status_code}"

        # 标准格式：有 code/msg/data
        if "code" in data:
            return data

        # 原始格式：自动补全外层
        return {
            "code": 0 if resp.status_code < 400 else 50000,
            "msg": "success" if resp.status_code < 400 else "请求失败",
            "data": data
        }

    @staticmethod
    def assert_code(resp, expect_code=0):
        """校验业务码，全兼容"""
        data = AssertUtil._safe_parse(resp)
        assert data["code"] == expect_code, \
            f"业务码错误！实际：{data['code']}，预期：{expect_code}，错误信息：{data.get('msg','')}"

    @staticmethod
    def assert_key_exist(resp, key):
        """校验字段存在，全兼容"""
        data = AssertUtil._safe_parse(resp)
        assert key in data["data"], f"响应缺少字段：{key}"
