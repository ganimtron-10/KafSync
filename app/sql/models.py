from sqlalchemy import Column,  Integer, String

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)


class IDMap(Base):
    __tablename__ = "idmap"

    localid = Column(Integer, primary_key=True, index=True, nullable=False)
    externalid = Column(String, nullable=False)
