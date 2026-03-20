import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.state import PlanningStateModel
from app.schemas.state import PlanningState, NodeStatus, NodeData

NODE_DEPENDENCIES = {
    "L0_intent": [],
    "L1_flight": ["L0_intent"],
    "L2_destination": ["L1_flight"],
    "L3_attractions": ["L2_destination"],
    "L4_hotel": ["L3_attractions"],
    "L5_itinerary": ["L3_attractions", "L4_hotel"],
    "L6_transport": ["L5_itinerary"],
    "L7_dining": ["L5_itinerary"],
    "L8_cost": ["L1_flight", "L2_destination", "L3_attractions", "L4_hotel", "L5_itinerary", "L6_transport", "L7_dining"],
    "L9_export": ["L8_cost"]
}

IMPACT_TABLE = {
    "L0_intent": ["L1_flight", "L3_attractions", "L4_hotel", "L5_itinerary", "L6_transport", "L7_dining", "L8_cost"],
    "L1_flight": ["L5_itinerary", "L8_cost"],
    "L2_destination": ["L3_attractions", "L4_hotel", "L5_itinerary", "L6_transport", "L7_dining", "L8_cost"],
    "L3_attractions": ["L5_itinerary", "L6_transport", "L8_cost"],
    "L4_hotel": ["L5_itinerary", "L6_transport", "L8_cost"],
    "L5_itinerary": ["L6_transport", "L8_cost"],
}

class StateService:
    @staticmethod
    def get_state(db: Session, session_id: str, user_id: str) -> PlanningState:
        db_state = db.query(PlanningStateModel).filter(
            PlanningStateModel.session_id == session_id
        ).first()

        if not db_state:
            state = PlanningState(
                session_id=session_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            StateService.save_state(db, state)
            return state

        return PlanningState.model_validate(db_state.state_json)

    @staticmethod
    def save_state(db: Session, state: PlanningState):
        db_state = db.query(PlanningStateModel).filter(
            PlanningStateModel.session_id == state.session_id
        ).first()

        state.updated_at = datetime.utcnow()
        state_dict = state.model_dump(mode='json')

        if db_state:
            db_state.state_json = state_dict
            db_state.updated_at = state.updated_at
        else:
            db_state = PlanningStateModel(
                session_id=state.session_id,
                user_id=state.user_id,
                state_json=state_dict,
                created_at=state.created_at,
                updated_at=state.updated_at
            )
            db.add(db_state)
        
        db.commit()

    @staticmethod
    def confirm_node(db: Session, session_id: str, user_id: str, node_id: str, data: Any):
        state = StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")

        # Save snapshot before change
        state.nodes[node_id].snapshots.append({
            "status": state.nodes[node_id].status,
            "data": state.nodes[node_id].data,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep last 20 snapshots
        if len(state.nodes[node_id].snapshots) > 20:
            state.nodes[node_id].snapshots.pop(0)

        state.nodes[node_id].status = NodeStatus.CONFIRMED
        state.nodes[node_id].data = data
        state.nodes[node_id].confirmed_at = datetime.utcnow()

        # Trigger downstream PENDING
        for down_node, up_nodes in NODE_DEPENDENCIES.items():
            if node_id in up_nodes:
                if state.nodes[down_node].status == NodeStatus.PENDING:
                    # Do nothing, it's already pending or check if all dependencies met
                    pass
                elif state.nodes[down_node].status == NodeStatus.STALE:
                    # Keep stale or change to pending? Usually stays stale until recomputed
                    pass

        StateService.save_state(db, state)
        return state

    @staticmethod
    def mark_stale(db: Session, session_id: str, user_id: str, node_id: str, reason: str):
        state = StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        
        if state.nodes[node_id].status == NodeStatus.LOCKED:
            # TODO: add compatibility warning instead of marking stale
            return state

        state.nodes[node_id].status = NodeStatus.STALE
        StateService.save_state(db, state)
        return state

    @staticmethod
    def lock_node(db: Session, session_id: str, user_id: str, node_id: str):
        state = StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        state.nodes[node_id].locked = True
        # If the status was already CONFIRMED, keep it but add LOCKED as a logical state?
        # Requirement says "Locked status icon", but status machine usually needs a primary status.
        # Let's keep status as is or make it LOCKED to distinguish in UI readily.
        state.nodes[node_id].status = NodeStatus.LOCKED
        StateService.save_state(db, state)
        return state

    @staticmethod
    def unlock_node(db: Session, session_id: str, user_id: str, node_id: str):
        state = StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        
        state.nodes[node_id].locked = False
        state.nodes[node_id].compatibility_warning = None
        state.nodes[node_id].status = NodeStatus.CONFIRMED 
        
        StateService.save_state(db, state)
        return state

    @staticmethod
    def batch_confirm_nodes(db: Session, session_id: str, user_id: str):
        """Quick Mode: Batch confirm all unconfirmed nodes using latest data."""
        state = StateService.get_state(db, session_id, user_id)
        for nid, node in state.nodes.items():
            if node.status in [NodeStatus.GENERATED, NodeStatus.STALE]:
                node.status = NodeStatus.CONFIRMED
                node.confirmed_at = datetime.utcnow()
        StateService.save_state(db, state)
        return state

    @staticmethod
    def rollback_node(db: Session, session_id: str, user_id: str, node_id: str):
        state = StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")

        # Save snapshot
        state.nodes[node_id].snapshots.append({
            "status": state.nodes[node_id].status,
            "data": state.nodes[node_id].data,
            "timestamp": datetime.utcnow().isoformat()
        })

        state.nodes[node_id].status = NodeStatus.GENERATED
        # Propagate impact
        from app.services.state_service import ImpactPropagator
        ImpactPropagator.propagate(state, node_id)
        
        StateService.save_state(db, state)
        return state

class ImpactPropagator:
    @staticmethod
    def propagate(state: PlanningState, modified_node_id: str):
        affected_nodes = IMPACT_TABLE.get(modified_node_id, [])
        for node_id in affected_nodes:
            if node_id in state.nodes:
                node = state.nodes[node_id]
                if node.locked:
                    node.compatibility_warning = f"上游节点 [{modified_node_id}] 已变更，请手动核查兼容性。"
                    continue
                node.status = NodeStatus.STALE
                node.compatibility_warning = None
        return state
