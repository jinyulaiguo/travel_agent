import math
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

    def _safe_get_value(self, wrapper_or_dict: Any) -> float:
        """安全获取 ConfidenceWrapper 的数值"""
        if hasattr(wrapper_or_dict, 'value'):
            return float(wrapper_or_dict.value or 0)
        if isinstance(wrapper_or_dict, dict):
            return float(wrapper_or_dict.get('value', 0))
        return float(wrapper_or_dict or 0)

    async def aggregate_costs(self, state: PlanningState) -> CostSummaryResponse:
        """
        汇总所有模块的费用数据。
        """
        items: List[CostItem] = []
        currency_rates = {}

        # 0. 提取基础参数 (从 L0/Intent 解析结果)
        constraints = state.constraints or {}
        travelers_info = constraints.get("travelers", {})
        total_travelers = travelers_info.get("total") or 1
        # 假设 1 间房住 2 人
        rooms_needed = math.ceil(total_travelers / 2)
        
        target_budget = constraints.get("preferences", {}).get("budget", {}).get("total")
        if not target_budget:
            # 兼容：如果只有人均预算
            per_person = constraints.get("preferences", {}).get("budget", {}).get("per_person")
            if per_person:
                target_budget = per_person * total_travelers

        # 1. 航班费用 (L1) - 假设已是总价
        flight_node = state.nodes.get("L1_flight")
        if flight_node and flight_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            data = flight_node.data
            if data:
                outbound = data.get("outbound", {})
                inbound = data.get("inbound", {})
                
                price = (outbound.get("price") or 0) + (inbound.get("price") or 0)
                snapshot_time = data.get("price_snapshot_time") or outbound.get("price_snapshot_time")
                
                if isinstance(snapshot_time, str):
                    snapshot_time = datetime.fromisoformat(snapshot_time)

                item = await self._create_cost_item(
                    category=CostCategory.FLIGHT,
                    source_module="L1_flight",
                    amount_min=price,
                    amount_max=price,
                    currency="CNY",
                    confidence=ConfidenceLevel(data.get("confidence_level", "L1")),
                    snapshot_time=snapshot_time,
                    description=f"机票往返 (共{total_travelers}人)"
                )
                items.append(item)

        # 2. 酒店费用 (L4) - 考虑房量
        hotel_node = state.nodes.get("L4_hotel")
        if hotel_node and hotel_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            data = hotel_node.data
            if data:
                selected = data.get("selected_hotel", {})
                price_per_night = selected.get("price_per_night") or 0
                nights = constraints.get("available_days") or 1
                # 总计 = 单价 * 天数 * 房间数
                total_price = price_per_night * nights * rooms_needed
                
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
                    description=f"酒店 {nights}晚 ({rooms_needed}间房，{selected.get('name', '未定')})"
                )
                items.append(item)

        # 3. 景点门票 (L3) - 乘以人数
        attraction_node = state.nodes.get("L3_attractions")
        if attraction_node and attraction_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            data = attraction_node.data
            if data:
                confirmed_list = data.get("confirmed_attractions", [])
                total_admission = 0
                for attr in confirmed_list:
                    # 单人票价 * 总人数
                    fee = attr.get("admission_fee", {}).get("adult") or 0
                    total_admission += (fee * total_travelers)
                
                if total_admission > 0:
                    items.append(CostItem(
                        category=CostCategory.ADMISSION,
                        source_module="L3_attractions",
                        amount_min={"value": total_admission, "confidence_level": ConfidenceLevel.L4_KNOWLEDGE},
                        amount_max={"value": total_admission, "confidence_level": ConfidenceLevel.L4_KNOWLEDGE},
                        currency="CNY",
                        converted_amount_min_cny={"value": total_admission, "confidence_level": ConfidenceLevel.L4_KNOWLEDGE},
                        converted_amount_max_cny={"value": total_admission, "confidence_level": ConfidenceLevel.L4_KNOWLEDGE},
                        confidence=ConfidenceLevel.L4_KNOWLEDGE,
                        description=f"景点门票 ({total_travelers}人汇总)"
                    ))

        # 4. 城市内交通 (L6) - 经验区间 (通常一家一辆车，不按人数翻倍)
        transport_node = state.nodes.get("L6_transport")
        if transport_node and transport_node.status in [NodeStatus.GENERATED, NodeStatus.CONFIRMED]:
            pass 
        else:
            avail_days = constraints.get("available_days") or 1
            items.append(CostItem(
                category=CostCategory.TRANSPORT,
                source_module="System_Estimate",
                amount_min={"value": 50 * total_travelers * avail_days, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
                amount_max={"value": 100 * total_travelers * avail_days, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
                currency="CNY",
                converted_amount_min_cny={"value": 50 * total_travelers * avail_days, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
                converted_amount_max_cny={"value": 100 * total_travelers * avail_days, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
                confidence=ConfidenceLevel.L5_ESTIMATE,
                description="市内交通估算"
            ))

        # 5. 餐饮 (L5 / System) - 乘以人数
        days = constraints.get("available_days") or 1
        items.append(CostItem(
            category=CostCategory.DINING,
            source_module="System_Estimate",
            amount_min={"value": 150 * days * total_travelers, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            amount_max={"value": 400 * days * total_travelers, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            currency="CNY",
            converted_amount_min_cny={"value": 150 * days * total_travelers, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            converted_amount_max_cny={"value": 400 * days * total_travelers, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            confidence=ConfidenceLevel.L5_ESTIMATE,
            description=f"预计餐饮 (每人每天¥150~400，共{total_travelers}人)"
        ))
        
        # 6. 备用金 (10%)
        current_min = sum(self._safe_get_value(i.converted_amount_min_cny) for i in items)
        items.append(CostItem(
            category=CostCategory.MISC,
            source_module="System_Estimate",
            amount_min={"value": current_min * 0.1, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            amount_max={"value": current_min * 0.1, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            currency="CNY",
            converted_amount_min_cny={"value": current_min * 0.1, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            converted_amount_max_cny={"value": current_min * 0.1, "confidence_level": ConfidenceLevel.L5_ESTIMATE},
            confidence=ConfidenceLevel.L5_ESTIMATE,
            description="杂费/备用金 (10%)"
        ))

        # 计算总计
        total_min = 0.0
        total_max = 0.0
        confirmed_cny = 0.0
        
        for i in items:
            t_min = self._safe_get_value(i.converted_amount_min_cny)
            t_max = self._safe_get_value(i.converted_amount_max_cny)
            total_min += t_min
            total_max += t_max
            if i.confidence in [ConfidenceLevel.L1_REALTIME, ConfidenceLevel.L2_SNAPSHOT]:
                confirmed_cny += t_min

        # 预算状态
        budget_status_message = None
        if target_budget:
            if total_min > target_budget:
                diff = int(total_min - target_budget)
                budget_status_message = f"方案预估 ¥{int(total_min):,}，已超出您的初始预算约 ¥{diff:,}"
            elif total_max < target_budget:
                budget_status_message = "当前方案完美契合您的预算范围"

        summary_text = f"预计总额 ¥{int(total_min):,} ～ ¥{int(total_max):,}，快照确认 ¥{int(confirmed_cny):,}"

        # 检查快照过期
        for item in items:
            self._check_snapshot_expiration(item)

        return CostSummaryResponse(
            items=items,
            total_min_cny=round(total_min, 2),
            total_max_cny=round(total_max, 2),
            confirmed_cny=round(confirmed_cny, 2),
            target_budget_cny=float(target_budget) if target_budget else None,
            budget_status_message=budget_status_message,
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
            amount_min={"value": amount_min, "confidence_level": confidence},
            amount_max={"value": amount_max, "confidence_level": confidence},
            currency=currency,
            converted_amount_min_cny={"value": amount_min * rate, "confidence_level": confidence},
            converted_amount_max_cny={"value": amount_max * rate, "confidence_level": confidence},
            confidence=confidence,
            snapshot_time=snapshot_time,
            description=description
        )

    def _check_snapshot_expiration(self, item: CostItem):
        if item.snapshot_time:
            # 超过30分钟视为过期
            if datetime.now() - item.snapshot_time > timedelta(minutes=30):
                item.expired_warning = True
