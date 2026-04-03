from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services.dining_service import DiningService
from app.schemas.dining import RestaurantRecord, SpecialtyDish, DiningEtiquette, Coordinates
from typing import List

router = APIRouter(tags=["dining"])

@router.get("/recommend/classic", response_model=List[RestaurantRecord])
async def get_classic_recommendations(
    city: str, lat: float, lng: float, limit: int = 5, db: AsyncSession = Depends(deps.get_db)
):
    """获取经典餐饮推荐"""
    return await DiningService.recommend_classic_restaurants(db, city, lat, lng, limit)

@router.get("/recommend/popular", response_model=List[RestaurantRecord])
async def get_popular_recommendations(
    city: str, lat: float, lng: float, limit: int = 5, db: AsyncSession = Depends(deps.get_db)
):
    """获取热门餐饮参考"""
    return await DiningService.recommend_popular_restaurants(db, city, lat, lng, limit)

@router.get("/specialties", response_model=List[SpecialtyDish])
async def get_specialties(city: str, db: AsyncSession = Depends(deps.get_db)):
    """获取城市特色菜"""
    return await DiningService.get_city_specialties(db, city)

@router.get("/etiquette", response_model=List[DiningEtiquette])
async def get_etiquette(city: str, db: AsyncSession = Depends(deps.get_db)):
    """获取城市用餐礼仪"""
    return await DiningService.get_city_etiquette(db, city)
