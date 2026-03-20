import uuid
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.db.base_class import Base

class ShareLink(Base):
    __tablename__ = "share_links"

    token = Column(String(32), primary_key=True, index=True, default=lambda: uuid.uuid4().hex)
    plan_id = Column(String(50), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
