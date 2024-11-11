from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from database.db_connection import Base


class TimeStampModelMixin:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)


class User(Base, TimeStampModelMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, unique=True)
    full_name = Column(String(255))
    email = Column(String(255), index=True, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=False)
