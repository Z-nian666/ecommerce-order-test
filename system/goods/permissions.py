from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """仅超级管理员可访问增删改接口"""
    def has_permission(self, request, view):
        # 必须同时满足：已登录 + 是超级管理员
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
