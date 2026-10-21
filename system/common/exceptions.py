class BusinessException(Exception):
    """业务异常，全局处理器统一捕获返回"""
    def __init__(self, msg, code=50000):
        self.msg = msg
        self.code = code
        super().__init__(msg)
