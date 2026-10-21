from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied, NotAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .response import Result
from .error_code import *
from .exceptions import BusinessException


def global_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # 1. 自定义业务异常
    if isinstance(exc, BusinessException):
        return Result.error(msg=exc.msg, code=exc.code)

    # 2. 资源不存在（双重捕获，优先级最高）
    if isinstance(exc, (NotFound, ObjectDoesNotExist)):
        return Result.error(msg="资源不存在", code=ORDER_NOT_EXIST)

    # 3. 参数校验异常
    if isinstance(exc, ValidationError):
        err_msg = list(exc.detail.values())[0][0] if exc.detail else "参数校验失败"
        return Result.error(msg=str(err_msg), code=PARAM_INVALID)

    # 4. 权限不足
    if isinstance(exc, PermissionDenied):
        return Result.error(msg="权限不足", code=PERMISSION_DENIED)

    # 5. 未登录
    if isinstance(exc, NotAuthenticated):
        return Result.error(msg="请先登录", code=NOT_LOGIN)

    # 6. 系统异常兜底
    if response is None:
        return Result.error(msg=str(exc), code=SYSTEM_ERROR)

    return response
