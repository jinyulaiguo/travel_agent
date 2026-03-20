from sqlalchemy import Column, String, Float, Integer, JSON
from app.db.base_class import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String, primary_key=True, index=True)
    name = Column(JSON, nullable=False)  # {"zh": "...", "en": "..."}
    city = Column(String, index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    cuisine_type = Column(JSON, nullable=False)  # List[str]
    avg_price_min = Column(Float, nullable=False)
    avg_price_max = Column(Float, nullable=False)
    currency = Column(String, default="CNY")
    established_year = Column(Integer)
    stability_rating = Column(Float)
    meal_periods = Column(JSON)  # ["lunch", "dinner"]
    last_updated = Column(String)
    data_source = Column(String)
    description = Column(String)

class SpecialtyDish(Base):
    __tablename__ = "specialty_dishes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city = Column(String, index=True, nullable=False)
    name = Column(JSON, nullable=False)
    description = Column(String)
    price_min = Column(Float)
    price_max = Column(Float)
    currency = Column(String, default="CNY")

class DiningEtiquette(Base):
    __tablename__ = "dining_etiquette"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
