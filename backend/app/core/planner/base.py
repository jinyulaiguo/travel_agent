from abc import ABC, abstractmethod
from app.schemas.state import PlanningState, NodeStatus

class BasePlannerModule(ABC):
    node_key: str  # 例如 "L3_attractions"

    @abstractmethod
    async def generate(self, state: PlanningState) -> dict:
        """生成候选方案，返回结构化数据"""
        ...

    @abstractmethod
    async def validate_input(self, state: PlanningState) -> bool:
        """校验上游依赖节点是否已 CONFIRMED"""
        ...

    def get_context(self, state: PlanningState) -> dict:
        """从 state 中提取本模块所需的上游数据"""
        return {
            "constraints": state.constraints,
            "confirmed_nodes": {
                k: v.data for k, v in state.nodes.items()
                if v.status == NodeStatus.CONFIRMED
            }
        }
