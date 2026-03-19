from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """统一错误响应模型"""
    code: int = Field(..., description="业务错误码或HTTP状态码")
    message: str = Field(..., description="错误详情描述")
    details: Optional[Any] = Field(None, description="额外的错误细节信息")


class ValidationErrorDetail(BaseModel):
    """验证错误细节"""
    loc: list[str]
    msg: str
    type: str
