import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.state import PlanningStateModel
from app.schemas.state import PlanningState, NodeStatus, NodeData
from app.core.influence.dependency_map import INFLUENCE_MAP

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


class StateService:
    @staticmethod
    async def get_state(db: AsyncSession, session_id: str, user_id: str) -> PlanningState:
        result = await db.execute(
            select(PlanningStateModel).filter(
                PlanningStateModel.session_id == session_id
            )
        )
        db_state = result.scalars().first()

        if not db_state:
            state = PlanningState(
                session_id=session_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await StateService.save_state(db, state)
            return state

        return PlanningState.model_validate(db_state.state_json)

    @staticmethod
    async def save_state(db: AsyncSession, state: PlanningState):
        result = await db.execute(
            select(PlanningStateModel).filter(
                PlanningStateModel.session_id == state.session_id
            )
        )
        db_state = result.scalars().first()

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
        
        await db.commit()

    @staticmethod
    async def update_constraints(db: AsyncSession, session_id: str, user_id: str, constraints: Dict[str, Any]):
        """更新会话的根约束 (L0 intent)"""
        state = await StateService.get_state(db, session_id, user_id)
        state.constraints = constraints
        
        # 同时更新 L0_intent 节点的确认状态
        if "L0_intent" in state.nodes:
            state.nodes["L0_intent"].status = NodeStatus.CONFIRMED
            state.nodes["L0_intent"].data = constraints
            state.nodes["L0_intent"].confirmed_at = datetime.utcnow()
        
        # 触发影响域传播
        ImpactPropagator.propagate(state, "L0_intent")
        
        await StateService.save_state(db, state)
        return state

    @staticmethod
    async def confirm_node(db: AsyncSession, session_id: str, user_id: str, node_id: str, data: Any):
        state = await StateService.get_state(db, session_id, user_id)
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

        # 触发影响域传播 (L1-L9)
        ImpactPropagator.propagate(state, node_id)

        await StateService.save_state(db, state)
        return state

    @staticmethod
    async def mark_stale(db: AsyncSession, session_id: str, user_id: str, node_id: str, reason: str):
        state = await StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        
        if state.nodes[node_id].status == NodeStatus.LOCKED:
            # TODO: add compatibility warning instead of marking stale
            return state

        state.nodes[node_id].status = NodeStatus.STALE
        await StateService.save_state(db, state)
        return state

    @staticmethod
    async def lock_node(db: AsyncSession, session_id: str, user_id: str, node_id: str):
        state = await StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        state.nodes[node_id].locked = True
        # If the status was already CONFIRMED, keep it but add LOCKED as a logical state?
        # Requirement says "Locked status icon", but status machine usually needs a primary status.
        # Let's keep status as is or make it LOCKED to distinguish in UI readily.
        state.nodes[node_id].status = NodeStatus.LOCKED
        await StateService.save_state(db, state)
        return state

    @staticmethod
    async def unlock_node(db: AsyncSession, session_id: str, user_id: str, node_id: str):
        state = await StateService.get_state(db, session_id, user_id)
        if node_id not in state.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        
        state.nodes[node_id].locked = False
        state.nodes[node_id].compatibility_warning = None
        state.nodes[node_id].status = NodeStatus.CONFIRMED 
        
        await StateService.save_state(db, state)
        return state

    @staticmethod
    async def batch_confirm_nodes(db: AsyncSession, session_id: str, user_id: str):
        """Quick Mode: Disabled. Only allow if all nodes are confirmed."""
        state = await StateService.get_state(db, session_id, user_id)
        for nid in ["L1_flight", "L2_destination", "L3_attractions", "L4_hotel", "L5_itinerary"]:
            if state.nodes.get(nid) and state.nodes[nid].status not in [NodeStatus.CONFIRMED, NodeStatus.LOCKED]:
                raise ValueError(f"一键生成功能已禁用，只有在所有状态都确认完成后才可以进行一键生成。未确认节点: {nid}")
                
        # If all confirmed, we can potentially trigger L9 or just return state
        await StateService.save_state(db, state)
        return state

    @staticmethod
    async def rollback_node(db: AsyncSession, session_id: str, user_id: str, node_id: str):
        state = await StateService.get_state(db, session_id, user_id)
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
        
        await StateService.save_state(db, state)
        return state

class ImpactPropagator:
    @staticmethod
    def propagate(state: PlanningState, modified_node_id: str):
        affected_nodes = INFLUENCE_MAP.get(modified_node_id, [])
        for node_id in affected_nodes:
            if node_id in state.nodes:
                node = state.nodes[node_id]
                if node.locked:
                    node.compatibility_warning = f"上游节点 [{modified_node_id}] 已变更，请手动核查兼容性。"
                    continue
                node.status = NodeStatus.STALE
                node.compatibility_warning = None
        return state
