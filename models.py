from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(String, unique=True, index=True) # Telegram chat ID
    group_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    target_language = Column(String, default="en") # en, ru, es, etc.
    expiry_date = Column(DateTime, nullable=True)
    status = Column(String, default="unpaid") # unpaid, active, expired
    payment_method = Column(String, nullable=True) # ton, uzcard
