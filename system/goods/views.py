from rest_framework import viewsets, permissions
from .models import Goods
from .serializers import GoodsSerializer
from common.response import Result
from common.error_code import PERMISSION_DENIED, ORDER_NOT_EXIST


class GoodsViewSet(viewsets.ModelViewSet):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    def get_permissions(self):
        # 查询仅需登录，增删改需管理员（双重保险：视图内再校验一次）
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def _check_admin(self, request):
        """内部工具：校验是否为超级管理员，不是直接返回权限不足"""
        if not request.user.is_superuser:
            return Result.error(msg="权限不足，仅管理员可操作", code=PERMISSION_DENIED)
        return None

    def list(self, request, *args, **kwargs):
        """商品列表查询"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            page_data = self.get_paginated_response(serializer.data).data
            return Result.success(data=page_data, msg="商品列表查询成功")
        serializer = self.get_serializer(queryset, many=True)
        return Result.success(data=serializer.data, msg="商品列表查询成功")

    def retrieve(self, request, *args, **kwargs):
        """商品详情查询（兜底异常）"""
        try:
            instance = self.get_object()
        except Exception:
            return Result.error(msg="商品不存在", code=ORDER_NOT_EXIST)
        serializer = self.get_serializer(instance)
        return Result.success(data=serializer.data, msg="商品详情查询成功")

    def create(self, request, *args, **kwargs):
        """新增商品（管理员校验+参数校验）"""
        # 先校验管理员权限
        auth_check = self._check_admin(request)
        if auth_check:
            return auth_check
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Result.success(data=serializer.data, msg="商品创建成功")

    def update(self, request, *args, **kwargs):
        """全量修改商品（管理员校验+异常兜底）"""
        auth_check = self._check_admin(request)
        if auth_check:
            return auth_check
        try:
            instance = self.get_object()
        except Exception:
            return Result.error(msg="商品不存在", code=ORDER_NOT_EXIST)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Result.success(data=serializer.data, msg="商品修改成功")

    def partial_update(self, request, *args, **kwargs):
        """部分修改商品"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除商品（管理员校验）"""
        auth_check = self._check_admin(request)
        if auth_check:
            return auth_check
        try:
            instance = self.get_object()
        except Exception:
            return Result.error(msg="商品不存在", code=ORDER_NOT_EXIST)
        self.perform_destroy(instance)
        return Result.success(msg="商品删除成功")
