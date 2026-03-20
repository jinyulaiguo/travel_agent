import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date

from sqlalchemy.orm import Session
from app.schemas.state import PlanningState, NodeStatus
from app.schemas.itinerary import (
    TravelPlan, DailyItinerary, ItineraryItem, AlternativeOption, 
    ShareLinkCreate, ShareLinkResponse, ItemType, ConfidenceLevel
)
from app.models.itinerary import ShareLink
from app.services.cost_summary_service import CostSummaryService

logger = logging.getLogger(__name__)

class ItineraryService:
    def __init__(self, db: Session = None):
        self.db = db

    async def generate_travel_plan(self, state: PlanningState) -> TravelPlan:
        """
        聚合全部已确认的节点状态到最终行程单
        """
        plan_id = state.plan_id
        
        # 1. 提取基础约束
        dest_constraints = state.constraints.get("destination", {}) if state.constraints else {}
        destination = dest_constraints.get("country", "")
        # 如果有具体城市可以拼接
        if dest_constraints.get("cities"):
            destination += " - " + " / ".join(dest_constraints.get("cities"))
            
        start_date_str = state.constraints.get("dates", {}).get("start") if state.constraints else None
        end_date_str = state.constraints.get("dates", {}).get("end") if state.constraints else None
        
        try:
            start_date = date.fromisoformat(start_date_str) if start_date_str else date.today()
            end_date = date.fromisoformat(end_date_str) if end_date_str else date.today()
        except Exception:
            start_date = date.today()
            end_date = date.today()
            
        days = state.constraints.get("available_days", 1) if state.constraints else 1
        
        # 2. 从各个 Node 收集 Item 并丢入按天划分的桶中
        day_buckets: Dict[int, List[ItineraryItem]] = {d: [] for d in range(1, days + 1)}
        important_reminders = []
        
        # Flight
        flight_node = state.nodes.get("L1_flight")
        if flight_node and flight_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            flight_data = flight_node.data or {}
            outbound = flight_data.get("outbound", {})
            inbound = flight_data.get("inbound", {})
            alts = flight_data.get("alternatives", [])
            
            flight_alts = [AlternativeOption(
                id=f"alt_{i}", name=f"{alt.get('airline', 'Flight')} - {alt.get('price', 0)}",
                cost_estimate=alt.get("price"),
                metadata=alt
            ) for i, alt in enumerate(alts[:2])]

            if outbound:
                day_buckets[1].append(ItineraryItem(
                    id="item_flight_outbound",
                    type=ItemType.FLIGHT,
                    name=f"去程航班: {outbound.get('airline', '未知航司')} {outbound.get('flight_number', '')}",
                    description=f"从 {outbound.get('departure_airport', '')} 到 {outbound.get('arrival_airport', '')}",
                    cost_estimate=outbound.get("price", 0),
                    confidence_level=ConfidenceLevel(flight_data.get("confidence_level", "green")),
                    alternatives=flight_alts
                ))
                
            if inbound:
                day_buckets[days].append(ItineraryItem(
                    id="item_flight_inbound",
                    type=ItemType.FLIGHT,
                    name=f"返程航班: {inbound.get('airline', '未知航司')} {inbound.get('flight_number', '')}",
                    description=f"从 {inbound.get('departure_airport', '')} 到 {inbound.get('arrival_airport', '')}",
                    cost_estimate=inbound.get("price", 0),
                    confidence_level=ConfidenceLevel(flight_data.get("confidence_level", "green")),
                    alternatives=[]
                ))
                
            visa_req = flight_data.get("visa_requirement")
            if visa_req:
                important_reminders.append(f"签证提醒: {visa_req}")

        # Hotel
        hotel_node = state.nodes.get("L4_hotel")
        if hotel_node and hotel_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            hotel_data = hotel_node.data or {}
            selected = hotel_data.get("selected_hotel", {})
            alts = hotel_data.get("alternatives", [])
            hotel_alts = [AlternativeOption(
                id=f"alt_hotel_{i}", name=alt.get("name", "Other Hotel"),
                cost_estimate=alt.get("price_per_night", 0),
                metadata=alt
            ) for i, alt in enumerate(alts[:2])]
            
            # 为方便演示，将酒店信息加到第一天
            if selected:
                day_buckets[1].append(ItineraryItem(
                    id="item_hotel_main",
                    type=ItemType.HOTEL,
                    name=f"住宿: {selected.get('name', '未定')}",
                    description=f"单晚均价 ¥{selected.get('price_per_night', 0)}",
                    cost_estimate=selected.get("price_per_night", 0) * days,
                    confidence_level=ConfidenceLevel.GREEN,
                    alternatives=hotel_alts
                ))

        # Attractions (L3) 和 排序机制等简化实现
        attr_node = state.nodes.get("L3_attractions")
        if attr_node and attr_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            attr_data = attr_node.data or {}
            confirmed = attr_data.get("confirmed_attractions", [])
            # 简单把景点均分到有空的日期
            for i, attr in enumerate(confirmed):
                day_idx = (i % days) + 1
                day_buckets[day_idx].append(ItineraryItem(
                    id=f"item_attr_{i}",
                    type=ItemType.SIGHTSEEING,
                    name=attr.get("name", "未定景点"),
                    description=attr.get("description", ""),
                    cost_estimate=attr.get("admission_fee", {}).get("adult", 0),
                    confidence_level=ConfidenceLevel.GREEN,
                    alternatives=[]
                ))

        # 3. 计算费用
        cost_service = CostSummaryService()
        cost_res = await cost_service.aggregate_costs(state)
        
        # 4. 组装每日行程对象
        daily_itineraries = []
        for d in range(1, days + 1):
            curr_date = start_date + timedelta(days=d-1)
            daily_itineraries.append(DailyItinerary(
                date=curr_date,
                day_number=d,
                items=day_buckets[d]
            ))
            
        return TravelPlan(
            plan_id=plan_id,
            destination=destination or "未知目的地",
            start_date=start_date,
            end_date=end_date,
            important_reminders=important_reminders,
            daily_itineraries=daily_itineraries,
            total_cost_summary={
                "total_min_cny": cost_res.total_min_cny,
                "total_max_cny": cost_res.total_max_cny,
                "confirmed_cny": cost_res.confirmed_cny
            }
        )

    def create_share_link(self, plan_id: str, req: ShareLinkCreate) -> ShareLinkResponse:
        """
        创建分享凭证令牌
        """
        if not self.db:
            raise ValueError("Database session required")
            
        token = uuid.uuid4().hex
        expires_at = datetime.utcnow() + timedelta(days=req.expires_in_days)
        
        link = ShareLink(token=token, plan_id=plan_id, expires_at=expires_at)
        self.db.add(link)
        self.db.commit()
        
        # 返回假定的前端访问路径 /share/{token}
        share_url = f"/share/{token}"
        
        return ShareLinkResponse(token=token, share_url=share_url, expires_at=expires_at)

    def get_plan_id_by_token(self, token: str) -> Optional[str]:
        """验证token有效性"""
        if not self.db:
            raise ValueError("Database session required")
            
        link = self.db.query(ShareLink).filter(ShareLink.token == token).first()
        if not link:
            return None
        if link.expires_at < datetime.utcnow():
            return None
        return link.plan_id

    async def replace_alternative(self, state: PlanningState, item_id: str, alternative_id: str):
        """
        一键替换主选的业务逻辑：
        这里模拟针对不同节点（如 Flight 或 Hotel），从 alternatives 列表中找到指定项替换。
        完成后将下游依赖设为 STALE。
        """
        # (实际需反查影响域机制，在此做状态机更改演示)
        state.mark_downstream_stale("L1_flight") # 例如如果是换了航班，影响 L6 / L4 
        return True

    def generate_pdf_bytes(self, plan: TravelPlan) -> bytes:
        """
        生成 PDF (WeasyPrint Backend render)
        """
        try:
            from weasyprint import HTML
            # 简单的 HTML 模板，实际应挂载 Jinja 模板构建出美观排版
            html_content = f"<html><head><style>body {{ font-family: 'sans-serif'; }}</style></head><body>"
            html_content += f"<h1>{plan.destination} 行程单</h1>"
            html_content += f"<p>日期：{plan.start_date} ~ {plan.end_date}</p>"
            html_content += f"<h2>总预算预估（CNY）：{plan.total_cost_summary.get('total_min_cny')} ~ {plan.total_cost_summary.get('total_max_cny')}</h2>"
            
            for day in plan.daily_itineraries:
                html_content += f"<h3>第 {day.day_number} 天 ({day.date})</h3><ul>"
                for item in day.items:
                    html_content += f"<li>{item.type.value.upper()}: {item.name} - ¥{item.cost_estimate or 0}</li>"
                html_content += "</ul>"
            
            html_content += f"<hr/><p><small>{plan.disclaimer}</small></p>"
            html_content += "</body></html>"
            
            pdf_bytes = HTML(string=html_content).write_pdf()
            return pdf_bytes
        except ImportError:
            # Fallback 如果 Weasyprint 不可用
            logger.error("WeasyPrint not installed. Returning empty bytes.")
            return b"WeasyPrint required but not installed."

