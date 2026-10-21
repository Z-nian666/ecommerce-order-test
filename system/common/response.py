from rest_framework.response import Response


class Result:
    @staticmethod
    def success(data=None, msg="操作成功"):
        """统一成功响应，返回DRF标准Response对象"""
        return Response({
            "code": 0,
            "msg": msg,
            "data": data
        })

    @staticmethod
    def error(msg="操作失败", code=50000):
        """统一失败响应，返回DRF标准Response对象"""
        return Response({
            "code": code,
            "msg": msg,
            "data": None
        })
