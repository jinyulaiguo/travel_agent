import pytest
from datetime import datetime, timedelta
from app.tools.exchange_rate import get_exchange_rate, COUNTRY_TO_CURRENCY, FALLBACK_RATES
from app.services.cost_summary_service import CostSummaryService
from app.schemas.state import PlanningState, NodeData, NodeStatus

@pytest.mark.asyncio
async def test_exchange_rate_mapping():
    # 测试国家到币种的映射
    res_th = await get_exchange_rate("TH")
    assert res_th["currency"] == "THB"
    
    res_unknown = await get_exchange_rate("XX")
    assert res_unknown["currency"] == "USD" # 默认回退到 USD

@pytest.mark.asyncio
async def test_exchange_rate_fallback(mocker):
    # 模拟 API 失败，触发回退
    mocker.patch("httpx.AsyncClient.get", side_effect=Exception("API Down"))
    
    res = await get_exchange_rate("TH")
    assert res["source"] == "fallback_config"
    assert res["rate"] == FALLBACK_RATES["THB"]
    assert "date" in res

@pytest.mark.asyncio
async def test_cost_aggregation():
    service = CostSummaryService()
    
    # 构造 Mock State
    mock_state = PlanningState(
        session_id="test_session",
        user_id="test_user",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        constraints={
            "available_days": 2,
            "travelers": {"total": 1}
        },
        nodes={
            "L1_flight": NodeData(
                status=NodeStatus.CONFIRMED,
                data={
                    "outbound": {"airline": "Testing", "price": 1000, "price_snapshot_time": datetime.now().isoformat()},
                    "confidence_level": "L1"
                }
            )
        }
    )
    
    summary = await service.aggregate_costs(mock_state)
    
    # 基本检查
    assert summary.total_min_cny > 1000
    assert "预计 ¥" in summary.summary_text
    assert "其中已快照确认 ¥1,000" in summary.summary_text
    
    # 检查酒店逻辑 (默认汇总逻辑中如果没有酒店则不计入，除非我在 service 中加了默认值)
    # 在我的实现中，没有酒店节点则不加酒店费用
    
    # 检查餐饮 (2天, 1人, 100-300 = 200-600)
    dining_item = next(i for i in summary.items if i.category == "dining")
    assert dining_item.amount_min == 200
    assert dining_item.amount_max == 600
