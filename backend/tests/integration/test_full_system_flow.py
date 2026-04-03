import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.db.base_class import Base
from app.services.state_service import StateService
from app.schemas.state import NodeStatus, PlanningState
from app.core.state_machine.engine import create_planning_graph
from app.schemas.intent import ConstraintObject, Preferences, BudgetPreference
from app.schemas.flight import FlightAnchor, FlightCandidate, FlightList
from app.schemas.destination import DestinationConfirmRequest, DestinationItem

# Setup Async SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_full_flow.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.mark.asyncio
async def test_full_system_integration():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        session_id = "test_full_flow_999"
        user_id = "test_user_v1"
        
        # 1. 初始状态获取
        state = await StateService.get_state(db, session_id, user_id)
        assert state.session_id == session_id
        
        # 2. L0: 确认意图
        intent = ConstraintObject(
            departure_date=datetime(2024, 5, 1),
            return_date=datetime(2024, 5, 5),
            adults=2,
            destinations=[{"city": "清迈", "country_code": "TH"}],
            preferences=Preferences(
                travel_style=["文化", "美食"],
                budget=BudgetPreference(per_person=5000)
            )
        )
        await StateService.update_constraints(db, session_id, user_id, intent.model_dump(mode='json'))
        
        # 3. L1: 模拟确认航班
        flight_anchor = FlightAnchor(
            outbound=FlightCandidate(
                airline="Thai Airways", 
                flight_number="TG615", 
                departure_time=datetime(2024, 5, 1, 10, 0),
                arrival_time=datetime(2024, 5, 1, 14, 0),
                price=1500
            ),
            inbound=FlightCandidate(
                airline="Thai Airways", 
                flight_number="TG616", 
                departure_time=datetime(2024, 5, 5, 18, 0),
                arrival_time=datetime(2024, 5, 5, 22, 0),
                price=1600
            )
        )
        await StateService.confirm_node(db, session_id, user_id, "L1_flight", flight_anchor.model_dump(mode='json'))
        
        # 4. L2: 模拟确认目的地
        dest_request = DestinationConfirmRequest(
            destinations=[
                DestinationItem(city="清迈", country_code="TH", allocated_days=5, order=0)
            ]
        )
        # 实际上 API 会重新计算字段，这里直接用 Service 模拟
        from app.services.destination_service import destination_service
        config = destination_service.lock_destination(dest_request, flight_anchor, state)
        await StateService.confirm_node(db, session_id, user_id, "L2_destination", config.model_dump(mode='json'))
        
        # 5. 启动 LangGraph 规划引擎 (模拟一键生成)
        graph = create_planning_graph()
        
        # 再次获取最新 state (包含 L0, L1, L2 的 CONFIRMED 状态)
        current_state = await StateService.get_state(db, session_id, user_id)
        
        # 模拟 graph.ainvoke
        # 注意：这里需要传入 db_factory 使引擎内部能持久化
        def db_factory():
            return AsyncSessionLocal()
            
        run_config = {"configurable": {"db_factory": db_factory}}
        final_state_data = await graph.ainvoke(current_state, run_config)
        
        # 6. 验证后续节点
        # L3, L4, L5, L8 应该都进入了 GENERATED 状态
        assert final_state_data.nodes["L3_attractions"].status == NodeStatus.GENERATED
        assert final_state_data.nodes["L4_hotel"].status == NodeStatus.GENERATED
        assert final_state_data.nodes["L5_itinerary"].status == NodeStatus.GENERATED
        assert final_state_data.nodes["L8_cost"].status == NodeStatus.GENERATED
        
        # 7. 验证最终行程输出 API 兼容性
        from app.services.itinerary_service import ItineraryService
        it_service = ItineraryService()
        travel_plan = await it_service.generate_travel_plan(final_state_data)
        
        assert travel_plan.session_id == session_id
        assert len(travel_plan.daily_plans) > 0
        print(f"✅ Full flow test passed. Generated {len(travel_plan.daily_plans)} days of itinerary.")

if __name__ == "__main__":
    asyncio.run(test_full_system_integration())
