from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from typing import Any

from app.schemas.confidence import ConfidenceLevel

class AdapterResponse(BaseModel):
    data: dict[str, Any]
    confidence: ConfidenceLevel
    fetched_at: datetime
    source: str          # 数据来源标识
    is_fallback: bool = False # 是否触发了降级
    fallback_reason: str | None = None

class BaseAdapter(ABC):
    @abstractmethod
    async def fetch(self, **kwargs) -> AdapterResponse:
        ...

    async def fetch_with_fallback(self, **kwargs) -> AdapterResponse:
        try:
            return await self.fetch(**kwargs)
        except Exception as e:
            return await self.fallback(error=e, **kwargs)

    @abstractmethod
    async def fallback(self, error: Exception, **kwargs) -> AdapterResponse:
        ...
