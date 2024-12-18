from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Report(Base):
    __tablename__ = "report"
    reportId = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    password = Column(String)
    name = Column(String)
    date = Column(DateTime)
    receive = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)