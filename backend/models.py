from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text)
    title = Column(Text)
    price = Column(String(50))
    description = Column(Text)
    features = Column(Text)
    images = Column(Text)
    category = Column(String(200))
    source = Column(String(50))
    
 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)  