import pytest
from app.services.itinerary_service import ItineraryService
from app.schemas.state import PlanningState
from datetime import date

@pytest.mark.asyncio
async def test_generate_travel_plan():
    service = ItineraryService()
    
    # 构造假数据
    state = PlanningState(
        plan_id="test_plan_123",
        current_node="L9_output",
        nodes={},
        constraints={
            "destination": {"country": "Japan", "cities": ["Tokyo", "Osaka"]},
            "dates": {"start": "2026-10-01", "end": "2026-10-07"},
            "available_days": 7
        }
    )
    
    plan = await service.generate_travel_plan(state)
    
    assert plan.plan_id == "test_plan_123"
    assert "Japan" in plan.destination
    assert plan.start_date == date(2026, 10, 1)
    
    # 因为没有配置具体的 node 内部数据，所以项目数应该没几个，但是 day bucket 会按 days 被初始化
    assert len(plan.daily_itineraries) == 7
    assert plan.daily_itineraries[0].day_number == 1
    
    # 我们应该有一个 total_cost_summary 从 CostSummaryService 返回，这里至少是个包含 default key 的 dict 
    assert "total_min_cny" in plan.total_cost_summary
