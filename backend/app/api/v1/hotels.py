from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from app.schemas.module_05 import HotelSelection
from app.services.module_05.hotel_service import HotelService

router = APIRouter()
hotel_service = HotelService()

@router.post("/recommend", response_model=HotelSelection)
async def recommend_hotels(
    attractions: List[Dict[str, Any]],
    check_in: str,
    check_out: str,
    budget: Optional[float] = None
):
    """
    Recommend hotels based on a list of confirmed attractions and dates.
    """
    try:
        recommendations = await hotel_service.get_hotel_recommendations(
            attractions=attractions,
            check_in=check_in,
            check_out=check_out,
            budget=budget
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
