from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
from app.api import deps
from app.services.state_service import StateService
from app.schemas.state import PlanningState, NodeStatus

router = APIRouter()

@router.get("/{session_id}", response_model=PlanningState)
def get_state(
    session_id: str,
    user_id: str, # In real app, get from auth
    db: Session = Depends(deps.get_db)
):
    return StateService.get_state(db, session_id, user_id)

@router.post("/{session_id}/nodes/{node_id}/confirm")
def confirm_node(
    session_id: str,
    node_id: str,
    data: Any,
    user_id: str,
    db: Session = Depends(deps.get_db)
):
    try:
        return StateService.confirm_node(db, session_id, user_id, node_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/nodes/{node_id}/lock")
def lock_node(
    session_id: str,
    node_id: str,
    user_id: str,
    db: Session = Depends(deps.get_db)
):
    return StateService.lock_node(db, session_id, user_id, node_id)

@router.post("/{session_id}/nodes/{node_id}/unlock")
def unlock_node(
    session_id: str,
    node_id: str,
    user_id: str,
    db: Session = Depends(deps.get_db)
):
    return StateService.unlock_node(db, session_id, user_id, node_id)

@router.post("/{session_id}/nodes/{node_id}/rollback")
def rollback_node(
    session_id: str,
    node_id: str,
    user_id: str,
    db: Session = Depends(deps.get_db)
):
    try:
        return StateService.rollback_node(db, session_id, user_id, node_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/batch-confirm")
def batch_confirm(
    session_id: str,
    user_id: str,
    db: Session = Depends(deps.get_db)
):
    """
    一键确认所有已生成或过期的节点（快速模式）。
    """
    return StateService.batch_confirm_nodes(db, session_id, user_id)
