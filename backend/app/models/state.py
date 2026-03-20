from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime
from app.db.base_class import Base

class PlanningStateModel(Base):
    __tablename__ = "planning_states"

    session_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    state_json = Column(JSON, nullable=False)  # Stores the PlanningState schema as JSON
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
