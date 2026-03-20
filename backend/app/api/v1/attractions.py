from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.attraction import (
    AttractionRecommendationRequest, AttractionList, AttractionRecord
)
from app.services.attraction.attraction_service import AttractionService
from app.services.attraction.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/api/v1/attractions", tags=["Attractions"])

# Dependency injection for services
def get_kb_service():
    return KnowledgeBaseService()

def get_attraction_service(kb_service: KnowledgeBaseService = Depends(get_kb_service)):
    return AttractionService(kb_service)

@router.post("/recommend", response_model=AttractionList)
async def recommend_attractions(
    request: AttractionRecommendationRequest,
    service: AttractionService = Depends(get_attraction_service)
):
    """
    Generate initial recommended attractions.
    """
    return service.recommend_attractions(request)

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

@router.post("/confirm")
async def confirm_attractions(
    attraction_list: AttractionList
):
    """
    Confirm the attraction list and trigger impact domain propagation.
    """
    # Trigger impact domain (Simulation for now)
    impacted_modules = ["L5_daily_schedule", "L6_transport", "L8_cost_summary"]
    
    return {
        "status": "success",
        "message": "景点列表已确认",
        "impact_domain_trigger": {
            "source": "L3_attractions",
            "stale_modules": impacted_modules,
            "warning": "修改景点列表将影响：每日行程编排、交通规划、费用汇总"
        },
        "data": attraction_list
    }
