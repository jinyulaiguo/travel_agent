from app.core.planner.base import BasePlannerModule
from app.schemas.state import PlanningState, NodeStatus
from app.services.itinerary_service import ItineraryService
from datetime import datetime

class ExportPlannerModule(BasePlannerModule):
    node_key: str = "L9_export"

    def __init__(self):
        self.service = ItineraryService()

    async def validate_input(self, state: PlanningState) -> bool:
        """L9 是最后一个节点，依赖 L8 (费用) 已确认"""
        l8 = state.nodes.get("L8_cost")
        return l8 is not None and l8.status in [NodeStatus.CONFIRMED]

    async def generate(self, state: PlanningState) -> dict:
        """完成行程导出与分享准备"""
        # 准备导出数据
        # 实际可能在此步生成 PDF 上传 S3 等，
        # 这里仅作逻辑闭环，记录导出时间。
        return {
            "export_ready": True,
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pdf_status": "Ready for download",
            "share_token_status": "Ready"
        }
