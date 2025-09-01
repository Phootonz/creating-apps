# Database model
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    nice_name = Column(String, index=True, unique=True)
    motto = Column(String)
    status = Column(String)
    