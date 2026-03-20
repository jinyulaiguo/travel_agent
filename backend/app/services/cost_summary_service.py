import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.schemas.cost import CostItem, CostSummaryResponse, CostCategory, ConfidenceLevel
from app.tools.exchange_rate import get_exchange_rate
from app.schemas.state import PlanningState, NodeStatus

logger = logging.getLogger(__name__)

class CostSummaryService:
    def __init__(self):
        # 模拟各种手动覆盖的存储（实际应从数据库或状态机读取）
        self.manual_overrides: Dict[str, CostItem] = {}

    async def aggregate_costs(self, state: PlanningState) -> CostSummaryResponse:
        """
        汇总所有模块的费用数据。
        """
        items: List[CostItem] = []
        currency_rates = {}

        # 1. 航班费用 (L1)
        flight_node = state.nodes.get("L1_flight")
        if flight_node and flight_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            data = flight_node.data
            if data:
                # 假设 data 结构符合 FlightAnchor
                outbound = data.get("outbound", {})
                inbound = data.get("inbound", {})
                
                price = outbound.get("price", 0) + inbound.get("price", 0)
                snapshot_time = data.get("price_snapshot_time") or outbound.get("price_snapshot_time")
                
                # 转换日期格式
                if isinstance(snapshot_time, str):
                    snapshot_time = datetime.fromisoformat(snapshot_time)

                item = await self._create_cost_item(
                    category=CostCategory.FLIGHT,
                    source_module="L1_flight",
                    amount_min=price,
                    amount_max=price,
                    currency="CNY", # 假设 API 返回的是 CNY，实际可能根据接口变化
                    confidence=ConfidenceLevel(data.get("confidence_level", "L1")),
                    snapshot_time=snapshot_time,
                    description=f"机票往返 ({outbound.get('airline', '')})"
                )
                items.append(item)

        # 2. 酒店费用 (L4)
        hotel_node = state.nodes.get("L4_hotel")
        if hotel_node and hotel_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            data = hotel_node.data
            if data:
                selected = data.get("selected_hotel", {})
                price_per_night = selected.get("price_per_night", 0)
                # 估算天数，从 DestinationConfig 获取或简单从 state 计算
                nights = state.constraints.get("available_days", 1) if state.constraints else 1
                total_price = price_per_night * nights
                
                snapshot_time = selected.get("price_snapshot_time")
                if isinstance(snapshot_time, str):
                    snapshot_time = datetime.fromisoformat(snapshot_time)

                item = await self._create_cost_item(
                    category=CostCategory.HOTEL,
                    source_module="L4_hotel",
                    amount_min=total_price,
                    amount_max=total_price,
                    currency="CNY",
                    confidence=ConfidenceLevel(selected.get("confidence_level", "L1")),
                    snapshot_time=snapshot_time,
                    description=f"酒店 {nights} 晚 ({selected.get('name', '未定')})"
                )
                items.append(item)

        # 3. 景点门票 (L3)
        attraction_node = state.nodes.get("L3_attractions")
        if attraction_node and attraction_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            data = attraction_node.data
            if data:
                # 累加所有景点的门票 (假设知识库已提供 admission_fee)
                confirmed_list = data.get("confirmed_attractions", [])
                total_admission = 0
                for attr in confirmed_list:
                    # 简化：假设已折算为 CNY 或者在知识库中是 CNY
                    # 实际可能需要根据 attr['currency'] 调用 exchange_rate
                    fee = attr.get("admission_fee", {}).get("adult", 0)
                    total_admission += fee
                
                if total_admission > 0:
                    items.append(CostItem(
                        category=CostCategory.ADMISSION,
                        source_module="L3_attractions",
                        amount_min=total_admission,
                        amount_max=total_admission,
                        currency="CNY",
                        converted_amount_min_cny=total_admission,
                        converted_amount_max_cny=total_admission,
                        confidence=ConfidenceLevel.L4_KNOWLEDGE,
                        description="景点门票汇总"
                    ))

        # 4. 城市内交通 (L6) - 统计估算区间
        transport_node = state.nodes.get("L6_transport")
        # 如果还没生成，根据目的地给个经验区间 (L5)
        if transport_node and transport_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            # 获取实际规划的交通估价
            pass 
        else:
            # 经验估算 L5
            items.append(CostItem(
                category=CostCategory.TRANSPORT,
                source_module="System_Estimate",
                amount_min=200,
                amount_max=500,
                currency="CNY",
                converted_amount_min_cny=200,
                converted_amount_max_cny=500,
                confidence=ConfidenceLevel.L5_ESTIMATE,
                description="城市内交通（经验估算）"
            ))

        # 5. 餐饮/杂费 (L7 / System)
        # 经验区间：人均 100-300 / 天
        days = state.constraints.get("available_days", 1) if state.constraints else 1
        travelers = state.constraints.get("travelers", {}).get("total", 1) if state.constraints else 1
        
        items.append(CostItem(
            category=CostCategory.DINING,
            source_module="System_Estimate",
            amount_min=100 * days * travelers,
            amount_max=300 * days * travelers,
            currency="CNY",
            converted_amount_min_cny=100 * days * travelers,
            converted_amount_max_cny=300 * days * travelers,
            confidence=ConfidenceLevel.L5_ESTIMATE,
            description=f"餐饮（预算区间，{days}天人均100-300）"
        ))
        
        # 6. 备用金 (10%)
        current_min = sum(i.converted_amount_min_cny for i in items)
        items.append(CostItem(
            category=CostCategory.MISC,
            source_module="System_Estimate",
            amount_min=current_min * 0.1,
            amount_max=current_min * 0.1,
            currency="CNY",
            converted_amount_min_cny=current_min * 0.1,
            converted_amount_max_cny=current_min * 0.1,
            confidence=ConfidenceLevel.L5_ESTIMATE,
            description="杂费/备用金 (10%)"
        ))

        # 计算总计
        total_min = sum(i.converted_amount_min_cny for i in items)
        total_max = sum(i.converted_amount_max_cny for i in items)
        confirmed_cny = sum(i.converted_amount_min_cny for i in items if i.confidence in [ConfidenceLevel.L1_REALTIME, ConfidenceLevel.L2_SNAPSHOT])

        summary_text = f"预计 ¥{int(total_min):,} ～ ¥{int(total_max):,}，其中已快照确认 ¥{int(confirmed_cny):,}"

        # 检查快照过期
        for item in items:
            self._check_snapshot_expiration(item)

        return CostSummaryResponse(
            items=items,
            total_min_cny=round(total_min, 2),
            total_max_cny=round(total_max, 2),
            confirmed_cny=round(confirmed_cny, 2),
            summary_text=summary_text,
            updated_at=datetime.now()
        )

    async def _create_cost_item(self, category, source_module, amount_min, amount_max, currency, confidence, snapshot_time=None, description=None) -> CostItem:
        """辅助方法：处理汇率转换并创建 CostItem"""
        if currency == "CNY":
            rate = 1.0
        else:
            # 简化：实际应从 state 获取目的地 country_code
            # 这里硬编码或传入
            res = await get_exchange_rate("TH") # 默认测试用 TH
            rate = res["rate"]
            
        return CostItem(
            category=category,
            source_module=source_module,
            amount_min=amount_min,
            amount_max=amount_max,
            currency=currency,
            converted_amount_min_cny=amount_min * rate,
            converted_amount_max_cny=amount_max * rate,
            confidence=confidence,
            snapshot_time=snapshot_time,
            description=description
        )

    def _check_snapshot_expiration(self, item: CostItem):
        if item.snapshot_time:
            # 超过30分钟视为过期
            if datetime.now() - item.snapshot_time > timedelta(minutes=30):
                item.expired_warning = True
