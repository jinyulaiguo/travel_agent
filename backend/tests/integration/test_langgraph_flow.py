import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.services.state_service import StateService
from app.schemas.state import NodeStatus, PlanningState
from app.core.state_machine.engine import create_planning_graph

# Setup in-memory sqlite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.mark.asyncio
async def test_langgraph_workflow():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    session_id = "test_flow_1"
    user_id = "test_user_1"
    
    # 1. Get initial state
    state = StateService.get_state(db, session_id, user_id)
    graph = create_planning_graph()
    
    # 2. Setup mock data for dependencies
    # L7_dining needs L2_destination and L5_itinerary to be CONFIRMED
    state.nodes["L2_destination"].status = NodeStatus.CONFIRMED
    state.nodes["L2_destination"].data = {
        "confirmed_destinations": [{"city": "清迈", "lat": 18.79, "lng": 98.98}]
    }
    state.nodes["L5_itinerary"].status = NodeStatus.CONFIRMED
    state.nodes["L5_itinerary"].data = {
        "days": []
    }
    # Also confirm L0, L1 to allow flow to reach L2/L3/L4
    state.nodes["L0_intent"].status = NodeStatus.CONFIRMED
    state.nodes["L1_flight"].status = NodeStatus.CONFIRMED
    
    StateService.save_state(db, state)
    
    # 3. Run the graph
    config = {"configurable": {"db": db}}
    # ainvoke returns the final state
    final_state = await graph.ainvoke(state, config)
    
    # 4. Verify results
    # Since L0-L6 are currently echo-nodes in engine.py (TODOs), 
    # they should remain CONFIRMED or transition as defined.
    # L7_dining should have been triggered
    assert final_state.nodes["L7_dining"].status in [NodeStatus.GENERATED, NodeStatus.PENDING]
    
    # Check that it saved to DB (re-fetch)
    db_state = StateService.get_state(db, session_id, user_id)
    assert db_state.nodes["L7_dining"].status == final_state.nodes["L7_dining"].status
    
    db.close()
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    asyncio.run(test_langgraph_workflow())
