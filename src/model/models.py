from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow())


class Entry(BaseModel):
    __tablename__ = "entry"

    amount_in_cents = Column(Integer, nullable=False, default=0)
    parent_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="entries")


class User(BaseModel):
    __tablename__ = "user"

    user_name = Column(String(80), unique=True, nullable=False)
    entries = relationship("Entry", back_populates="user")
