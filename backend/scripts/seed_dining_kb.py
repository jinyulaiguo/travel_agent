import asyncio
import json
import os
import sys

# Add project root to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal
from app.models.dining import Restaurant, SpecialtyDish, DiningEtiquette

# Mock Data for Southeast Asia
DINING_DATA = {
    "清迈": {
        "restaurants": [
            {
                "id": "cm_rest_001",
                "name": {"zh": "Khao Soi Khun Yai", "en": "Khao Soi Khun Yai"},
                "lat": 18.7946, "lng": 98.9865,
                "address": "Sri Poom Rd, Mueang Chiang Mai District, Chiang Mai 50200",
                "cuisine_type": ["Northern Thai", "Khao Soi"],
                "avg_price_min": 50, "avg_price_max": 100, "currency": "THB",
                "established_year": 2010, "stability_rating": 4.8,
                "meal_periods": ["lunch"],
                "last_updated": "2024-03-20", "data_source": "Local Guide",
                "description": "Best Khao Soi in town, local favorite."
            },
            {
                "id": "cm_rest_002",
                "name": {"zh": "The Good View", "en": "The Good View Bar & Restaurant"},
                "lat": 18.7915, "lng": 99.0028,
                "address": "13 Charoen Rat Rd, Wat Ket, Mueang Chiang Mai District, Chiang Mai 50000",
                "cuisine_type": ["Thai", "International", "Live Music"],
                "avg_price_min": 300, "avg_price_max": 800, "currency": "THB",
                "established_year": 1996, "stability_rating": 4.9,
                "meal_periods": ["dinner"],
                "last_updated": "2024-03-20", "data_source": "TripAdvisor",
                "description": "Riverside dining with live music and great atmosphere."
            }
        ],
        "specialties": [
            {"name": {"zh": "泰北金面", "en": "Khao Soi"}, "description": "Curry noodles with crispy topping.", "price_min": 50, "price_max": 120},
            {"name": {"zh": "泰北酸肉", "en": "Sai Oua"}, "description": "Grilled herb sausage.", "price_min": 40, "price_max": 100}
        ],
        "etiquette": [
            {"title": "小费习惯", "content": "通常餐厅会加收 10% 服务费，否则可留 20-50 泰铢小费。"},
            {"title": "用餐礼仪", "content": "使用叉子将食物推入勺子中食用，不要直接用叉子送入嘴中。"}
        ]
    },
    "曼谷": {
        "restaurants": [
            {
                "id": "bk_rest_001",
                "name": {"zh": "Jay Fai", "en": "Raan Jay Fai"},
                "lat": 13.7525, "lng": 100.5048,
                "address": "327 Maha Chai Rd, Samran Rat, Phra Nakhon, Bangkok 10200",
                "cuisine_type": ["Seafood", "Thai Street Food"],
                "avg_price_min": 1000, "avg_price_max": 3000, "currency": "THB",
                "established_year": 1980, "stability_rating": 5.0,
                "meal_periods": ["lunch", "dinner"],
                "last_updated": "2024-03-20", "data_source": "Michelin Guide",
                "description": "Legendary Michelin-starred street food."
            }
        ],
        "specialties": [
            {"name": {"zh": "冬阴功汤", "en": "Tom Yum Goong"}, "description": "Spicy and sour shrimp soup.", "price_min": 150, "price_max": 400}
        ],
        "etiquette": [
            {"title": "筷子使用", "content": "吃面时使用筷子，饭桌上通常使用勺叉。"}
        ]
    }
}

async def seed():
    async with SessionLocal() as db:
        # Fetch existing records for lookup to ensure idempotency
        # and avoid JSON comparison issues in some DBs (like PostgreSQL)
        
        # Load existing specialties
        res_dishes = await db.execute(select(SpecialtyDish))
        existing_dishes = res_dishes.scalars().all()
        # Lookup key: (city, name_text)
        dish_lookup = {
            (d.city, json.dumps(d.name, sort_keys=True)): d 
            for d in existing_dishes
        }
        
        # Load existing etiquette
        res_etiq = await db.execute(select(DiningEtiquette))
        existing_etiq = res_etiq.scalars().all()
        # Lookup key: (city, title)
        etiq_lookup = {(e.city, e.title): e for e in existing_etiq}

        for city, data in DINING_DATA.items():
            # Seed Restaurants
            for r in data["restaurants"]:
                rest = Restaurant(
                    id=r["id"],
                    name=r["name"],
                    city=city,
                    lat=r["lat"],
                    lng=r["lng"],
                    address=r["address"],
                    cuisine_type=r["cuisine_type"],
                    avg_price_min=r["avg_price_min"],
                    avg_price_max=r["avg_price_max"],
                    currency=r["currency"],
                    established_year=r["established_year"],
                    stability_rating=r["stability_rating"],
                    meal_periods=r["meal_periods"],
                    last_updated=r["last_updated"],
                    data_source=r["data_source"],
                    description=r["description"]
                )
                await db.merge(rest)
            
            # Seed Specialties
            for s in data["specialties"]:
                key = (city, json.dumps(s["name"], sort_keys=True))
                if key in dish_lookup:
                    existing = dish_lookup[key]
                    existing.description = s["description"]
                    existing.price_min = s["price_min"]
                    existing.price_max = s["price_max"]
                else:
                    dish = SpecialtyDish(
                        city=city,
                        name=s["name"],
                        description=s["description"],
                        price_min=s["price_min"],
                        price_max=s["price_max"]
                    )
                    db.add(dish)
            
            # Seed Etiquette
            for e in data["etiquette"]:
                key = (city, e["title"])
                if key in etiq_lookup:
                    existing = etiq_lookup[key]
                    existing.content = e["content"]
                else:
                    etiq = DiningEtiquette(
                        city=city,
                        title=e["title"],
                        content=e["content"]
                    )
                    db.add(etiq)
        
        await db.commit()
        print("Seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
