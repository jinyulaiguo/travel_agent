from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api import deps
from app.services.state_service import StateService
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.intent import ConstraintObject
from app.schemas.destination import DestinationConfig
from app.schemas.attraction import AttractionList
from app.schemas.module_05 import HotelSelection
from app.services.module_05.hotel_service import HotelService

router = APIRouter(tags=["hotels"])
hotel_service = HotelService()

@router.post("/recommend", response_model=HotelSelection)
async def recommend_hotels(
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Recommend hotels based on session state (confirmed attractions and dates).
    """
    try:
        state = await StateService.get_state(db, session_id, user_id)
        
        # Needs L0, L2, L3
        if not state.constraints or not state.nodes.get("L3_attractions") or not state.nodes["L3_attractions"].data:
             raise HTTPException(status_code=400, detail="意图或景点列表尚未确认")
        
        constraints = ConstraintObject(**state.constraints)
        attractions = AttractionList(**state.nodes["L3_attractions"].data)
        
        # Convert Pydantic models to dicts for service compatibility
        attraction_dicts = [a.model_dump() for a in attractions.confirmed_attractions]
        
        # Determine hotel check-in/out based on first destination or entire trip
        recommendations = await hotel_service.get_hotel_recommendations(
            attractions=attraction_dicts,
            check_in=constraints.departure_date,
            check_out=constraints.return_date,
            budget=constraints.preferences.budget.total if constraints.preferences.budget else None
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm", response_model=HotelSelection)
async def confirm_hotels(
    selection: HotelSelection,
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Confirm hotel selection and persist to L4 node.
    """
    await StateService.confirm_node(db, session_id, user_id, "L4_hotel", selection.model_dump(mode='json'))
    return selection

@router.post("/refresh", response_model=HotelSelection)
async def refresh_hotels(
    hotel_ids: List[str],
    # Other context needed to refresh
):
    """
    Refresh hotel prices and status.
    """
    # Placeholder for refresh logic
    return HotelSelection(recommended_area="Refresh logic pending implementation", area_rationale="")
