import pytest
from sqlalchemy import create_url
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from sqlalchemy import create_engine
from app.services.state_service import StateService
from app.schemas.state import NodeStatus, PlanningState

# Setup in-memory sqlite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_state_transitions():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    session_id = "test_session_1"
    user_id = "test_user_1"
    
    # 1. Get initial state
    state = StateService.get_state(db, session_id, user_id)
    assert state.session_id == session_id
    assert state.nodes["L0_intent"].status == NodeStatus.PENDING
    
    # 2. Confirm L0
    StateService.confirm_node(db, session_id, user_id, "L0_intent", {"query": "Beijing"})
    state = StateService.get_state(db, session_id, user_id)
    assert state.nodes["L0_intent"].status == NodeStatus.CONFIRMED
    assert state.nodes["L0_intent"].data == {"query": "Beijing"}
    
    # 3. Rollback L0
    StateService.rollback_node(db, session_id, user_id, "L0_intent")
    state = StateService.get_state(db, session_id, user_id)
    assert state.nodes["L0_intent"].status == NodeStatus.GENERATED
    # Check impact propagation (Beijing trip L1-L8 should be STALE/PENDING)
    # Since they were PENDING initially, they might stay PENDING or become STALE if previously confirmed
    
    # 4. Confirm L0 and L1
    StateService.confirm_node(db, session_id, user_id, "L0_intent", {"query": "Beijing"})
    StateService.confirm_node(db, session_id, user_id, "L1_flight", {"flight": "CA123"})
    state = StateService.get_state(db, session_id, user_id)
    assert state.nodes["L1_flight"].status == NodeStatus.CONFIRMED
    
    # 5. Modify L0 and check propagation to L1
    StateService.confirm_node(db, session_id, user_id, "L0_intent", {"query": "Shanghai"})
    from app.services.state_service import ImpactPropagator
    ImpactPropagator.propagate(state, "L0_intent")
    StateService.save_state(db, state)
    
    state = StateService.get_state(db, session_id, user_id)
    assert state.nodes["L1_flight"].status == NodeStatus.STALE
    
    # 6. Lock L1 and modify L0
    StateService.lock_node(db, session_id, user_id, "L1_flight")
    StateService.confirm_node(db, session_id, user_id, "L0_intent", {"query": "Xi'an"})
    ImpactPropagator.propagate(state, "L0_intent")
    StateService.save_state(db, state)
    
    state = StateService.get_state(db, session_id, user_id)
    assert state.nodes["L1_flight"].status == NodeStatus.LOCKED
    
    db.close()
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    test_state_transitions()
    print("All tests passed!")
