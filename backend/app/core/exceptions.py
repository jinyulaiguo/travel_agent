from typing import Any, Optional


class BaseAppError(Exception):
    """所有应用异常的基类"""
    def __init__(
        self, 
        message: str, 
        code: int = 500, 
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class TravelAgentError(BaseAppError):
    """旅游规划相关异常的基类"""
    def __init__(self, message: str, code: int = 4000, details: Optional[Any] = None):
        super().__init__(message, code, details)


class BusinessError(BaseAppError):
    """业务逻辑错误"""
    def __init__(self, message: str, code: int = 4000, details: Optional[Any] = None):
        super().__init__(message, code, details)


class NotFoundError(BaseAppError):
    """资源不存在错误"""
    def __init__(self, resource: str, identifier: Any):
        message = f"未找到资源 {resource}: {identifier}"
        super().__init__(message, code=404)


class ValidationError(BaseAppError):
    """输入验证错误"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, code=422, details=details)


class UnauthorizedError(BaseAppError):
    """鉴权错误"""
    def __init__(self, message: str = "未授权访问"):
        super().__init__(message, code=401)


class ForbiddenError(BaseAppError):
    """禁止访问错误"""
    def __init__(self, message: str = "访问被拒绝"):
        super().__init__(message, code=403)


class ExternalServiceError(BaseAppError):
    """外部服务调用错误"""
    def __init__(self, service_name: str, message: str, details: Optional[Any] = None):
        full_message = f"外部服务 {service_name} 错误: {message}"
        super().__init__(full_message, code=502, details=details)


# 保持向后兼容
class UpstreamNodeNotConfirmedError(TravelAgentError):
    def __init__(self, node_key: str):
        super().__init__(f"上游节点 {node_key} 未确认", code=4001)


class AdapterFallbackError(TravelAgentError):
    def __init__(self, adapter: str, reason: str):
        super().__init__(f"适配器 {adapter} 降级：{reason}", code=4003)
