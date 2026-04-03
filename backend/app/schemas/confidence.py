from enum import Enum
from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel, model_validator

T = TypeVar("T")

class ConfidenceLevel(str, Enum):
    L1 = "L1"
    L1_REALTIME = "L1"   # 实时接口，30分钟内有效
    L2 = "L2"
    L2_SNAPSHOT = "L2"   # 快照，已超时效
    L3 = "L3"
    L3_STATIC = "L3"     # 历史统计
    L4 = "L4"
    L4_KNOWLEDGE = "L4"  # 知识库
    L5 = "L5"
    L5_ESTIMATE = "L5"   # 模型估算

class ConfidenceWrapper(BaseModel, Generic[T]):
    value: T
    confidence_level: ConfidenceLevel
    snapshot_time: Optional[str] = None
    note: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_confidence_wrapper(cls, data: Any) -> Any:
        # print(f"DEBUG: ConfidenceWrapper validating data: {data}")
        if isinstance(data, dict) and "value" in data:
            # If it's already a wrapper, ensure confidence_level exists
            if "confidence_level" not in data:
                data["confidence_level"] = ConfidenceLevel.L4
            return data
        
        # If it's a raw value, wrap it
        return {
            "value": data,
            "confidence_level": ConfidenceLevel.L4,
            "note": "Automatically wrapped from raw value"
        }

    class Config:
        use_enum_values = True
