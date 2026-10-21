from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from common.response import Result
from common.error_code import PARAM_INVALID


class RegisterView(APIView):
    """用户注册"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Result.error(msg="用户名和密码不能为空", code=PARAM_INVALID)

        if User.objects.filter(username=username).exists():
            return Result.error(msg="用户名已存在", code=PARAM_INVALID)

        user = User.objects.create_user(username=username, password=password)
        return Result.success(data={"id": user.id, "username": user.username}, msg="注册成功")


class LoginView(APIView):
    """用户登录"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Result.error(msg="用户名和密码不能为空", code=PARAM_INVALID)

        user = authenticate(username=username, password=password)
        if not user:
            return Result.error(msg="用户名或密码错误", code=PARAM_INVALID)

        refresh = RefreshToken.for_user(user)
        return Result.success(data={
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, msg="登录成功")


class UserInfoView(APIView):
    """获取当前用户信息"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Result.success(data={
            "id": request.user.id,
            "username": request.user.username,
            "is_superuser": request.user.is_superuser
        }, msg="用户信息查询成功")
