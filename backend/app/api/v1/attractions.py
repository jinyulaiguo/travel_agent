from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.attraction import (
    AttractionRecommendationRequest, AttractionList, AttractionRecord
)
from app.services.attraction.attraction_service import AttractionService
from app.services.attraction.knowledge_base_service import KnowledgeBaseService
from app.services.state_service import StateService
from app.api import deps
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.intent import ConstraintObject
from app.schemas.destination import DestinationConfig

router = APIRouter(tags=["attractions"])

# Dependency injection for services
def get_kb_service():
    return KnowledgeBaseService()

def get_attraction_service(kb_service: KnowledgeBaseService = Depends(get_kb_service)):
    return AttractionService(kb_service)

@router.post("/recommend", response_model=AttractionList)
async def recommend_attractions(
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db),
    service: AttractionService = Depends(get_attraction_service)
):
    """
    Generate initial recommended attractions using session state.
    """
    state = await StateService.get_state(db, session_id, user_id)
    
    # Needs L0
    if not state.constraints:
         raise HTTPException(status_code=400, detail="意图尚未确认")
    
    # Auto-handle L2_destination if missing (to support current simplified HIL flow)
    l2_node = state.nodes.get("L2_destination")
    if not l2_node or not l2_node.data:
        from app.services.destination_service import destination_service
        from app.schemas.flight import FlightAnchor
        
        l1_node = state.nodes.get("L1_flight")
        if not l1_node or not l1_node.data:
             raise HTTPException(status_code=400, detail="大交通尚未确认")
             
        constraints = ConstraintObject(**state.constraints)
        flight = FlightAnchor(**l1_node.data)
        
        # Build a mock confirm request for first city
        from app.schemas.destination import DestinationConfirmRequest, DestinationItem
        if not constraints.destinations:
             raise HTTPException(status_code=400, detail="意图中未包含目的地")
             
        dest_confirm = DestinationConfirmRequest(
            destinations=[
                DestinationItem(
                    city=constraints.destinations[0].city,
                    country_code=constraints.destinations[0].country_code,
                    lat=constraints.destinations[0].lat or 39.9, # Default for Beijing
                    lng=constraints.destinations[0].lng or 116.4,
                    allocated_days=constraints.available_days or 3
                )
            ]
        )
        
        dest_config = destination_service.lock_destination(dest_confirm, flight, state)
        await StateService.confirm_node(db, session_id, user_id, "L2_destination", dest_config.model_dump(mode='json'))
        # Re-fetch state or use local copy
        state = await StateService.get_state(db, session_id, user_id)
    
    constraints = ConstraintObject(**state.constraints)
    dest_config = DestinationConfig(**state.nodes["L2_destination"].data)
    
    # Build internal request
    rec_request = AttractionRecommendationRequest(
        cities=[d.city for d in dest_config.confirmed_destinations],
        available_days=dest_config.total_days,
        travel_style=constraints.preferences.travel_style
    )
    
    return service.recommend_attractions(rec_request)

@router.get("/search", response_model=List[AttractionRecord])
async def search_attractions(
    query: str,
    city: Optional[str] = None,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Search for attractions in the knowledge base.
    """
    results = kb_service.search_attractions(query, city)
    if not results and city:
        # If no local results, we could call Google Places here in the future
        pass
    return results

@router.post("/confirm", response_model=AttractionList)
async def confirm_attractions(
    attraction_list: AttractionList,
    session_id: str,
    user_id: str = "default_user",
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Confirm the attraction list and persist to L3 node.
    """
    await StateService.confirm_node(db, session_id, user_id, "L3_attractions", attraction_list.model_dump(mode='json'))
    return attraction_list
