# 通用状态码
SUCCESS = 0
SYSTEM_ERROR = 50000

# 订单业务模块 10xxx
STOCK_NOT_ENOUGH = 10001  # 库存不足
IDEMPOTENT_PROCESSING = 10002  # 幂等请求处理中
ORDER_NOT_EXIST = 10003  # 订单不存在

# 参数校验模块 20xxx
PARAM_INVALID = 20001  # 参数非法

# 权限模块 40xxx
PERMISSION_DENIED = 40001  # 权限不足
NOT_LOGIN = 40002  # 未登录

# 商品业务模块 11xxx
GOODS_NOT_EXIST = 11001  # 商品不存在
# 订单状态异常
ORDER_STATUS_ERROR = 10005
