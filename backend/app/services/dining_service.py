import math
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.dining import Restaurant, SpecialtyDish, DiningEtiquette
from app.schemas.dining import RestaurantRecord, SpecialtyDish as SpecialtyDishSchema, DiningEtiquette as DiningEtiquetteSchema, Coordinates, PriceRange

class DiningService:
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """计算两点间的距离 (km)"""
        R = 6371  # 地球半径 (km)
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    async def recommend_classic_restaurants(
        cls, db: AsyncSession, city: str, center_lat: float, center_lng: float, limit: int = 2
    ) -> List[RestaurantRecord]:
        """推荐经典餐厅：经营年限 >= 3年 + 稳定性评级 >= 4星 + 距离 <= 2km"""
        # 简单起见，2024年作为当前基准
        stmt = select(Restaurant).where(
            and_(
                Restaurant.city == city,
                Restaurant.established_year <= 2021,  # 2024 - 3
                Restaurant.stability_rating >= 4.0
            )
        )
        result = await db.execute(stmt)
        all_candidates = result.scalars().all()
        
        filtered = []
        for r in all_candidates:
            dist = cls.calculate_distance(center_lat, center_lng, r.lat, r.lng)
            if dist <= 2.0:
                filtered.append(cls._to_schema(r))
        
        filtered.sort(key=lambda x: x.stability_rating, reverse=True)
        return filtered[:limit]

    @classmethod
    async def recommend_popular_restaurants(
        cls, db: AsyncSession, city: str, center_lat: float, center_lng: float, limit: int = 2
    ) -> List[RestaurantRecord]:
        """推荐热门餐厅：稳定性评级 >= 3.5 + 距离 <= 5km"""
        stmt = select(Restaurant).where(
            and_(
                Restaurant.city == city,
                Restaurant.stability_rating >= 3.5
            )
        )
        result = await db.execute(stmt)
        all_candidates = result.scalars().all()
        
        filtered = []
        for r in all_candidates:
            dist = cls.calculate_distance(center_lat, center_lng, r.lat, r.lng)
            if dist <= 5.0:
                schema_r = cls._to_schema(r)
                schema_r.confidence_level = "L3" # 热门标注为 L3 (统计/外部)
                filtered.append(schema_r)
        
        filtered.sort(key=lambda x: x.stability_rating, reverse=True)
        return filtered[:limit]

    @staticmethod
    async def get_city_specialties(db: AsyncSession, city: str) -> List[SpecialtyDishSchema]:
        """获取城市特色菜"""
        stmt = select(SpecialtyDish).where(SpecialtyDish.city == city)
        result = await db.execute(stmt)
        return [
            SpecialtyDishSchema(
                name=s.name,
                description=s.description,
                price_range=PriceRange(min=s.price_min, max=s.price_max, currency=s.currency) if s.price_min else None
            ) for s in result.scalars().all()
        ]

    @staticmethod
    async def get_city_etiquette(db: AsyncSession, city: str) -> List[DiningEtiquetteSchema]:
        """获取城市用餐礼仪"""
        stmt = select(DiningEtiquette).where(DiningEtiquette.city == city)
        result = await db.execute(stmt)
        return [
            DiningEtiquetteSchema(title=e.title, content=e.content)
            for e in result.scalars().all()
        ]

    @staticmethod
    def _to_schema(r: Restaurant) -> RestaurantRecord:
        return RestaurantRecord(
            id=r.id,
            name=r.name,
            city=r.city,
            coordinates=Coordinates(lat=r.lat, lng=r.lng),
            address=r.address,
            cuisine_type=r.cuisine_type,
            avg_price_per_person=PriceRange(min=r.avg_price_min, max=r.avg_price_max, currency=r.currency),
            established_year=r.established_year,
            stability_rating=r.stability_rating,
            meal_periods=r.meal_periods,
            last_updated=r.last_updated,
            data_source=r.data_source,
            description=r.description,
            confidence_level="L4"
        )
