from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    description = Column(String, nullable=False)


class ServiceHistory(Base):
    __tablename__ = 'service_history'

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    status = Column(String, nullable=False)
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="history")


Service.history = relationship("ServiceHistory",
                               order_by=ServiceHistory.id,
                               back_populates="service")
