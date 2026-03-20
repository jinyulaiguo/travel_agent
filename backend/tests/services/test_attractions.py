import pytest
from app.schemas.attraction import AttractionRecommendationRequest, Coordinates
from app.services.attraction.knowledge_base_service import KnowledgeBaseService
from app.services.attraction.attraction_service import AttractionService
from app.services.attraction.map_service import MapService

def test_recommendation_logic():
    kb = KnowledgeBaseService()
    service = AttractionService(kb)
    
    request = AttractionRecommendationRequest(
        cities=["清迈"],
        available_days=2,
        travel_style=["文化古迹"]
    )
    
    result = service.recommend_attractions(request)
    
    assert len(result.confirmed_attractions) > 0
    # Expected clusters roughly equal to available_days
    cluster_ids = set(a.cluster_id for a in result.confirmed_attractions)
    assert len(cluster_ids) <= 2
    
    # Check if Wat Phra That Doi Suthep (culture) is included
    names = [a.name for a in result.confirmed_attractions]
    assert "双龙寺" in names or "清迈古城" in names

@pytest.mark.asyncio
async def test_map_route_fallback():
    service = MapService()
    origin = Coordinates(lat=18.8049, lng=98.9216)  # Doi Suthep
    dest = Coordinates(lat=18.7883, lng=98.9853)    # Old City
    
    route = await service.map_route(origin, dest, mode="driving")
    
    assert route["status"] == "fallback_calculated"
    assert route["distance_km"] > 0
    assert "驾车" in route["description"]

def test_reason_generation():
    kb = KnowledgeBaseService()
    service = AttractionService(kb)
    
    attraction = kb.get_all_attractions()[0]
    reason = service.generate_reason(attraction, ["文化古迹"])
    assert "文化古迹" in reason
