from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType

Base = declarative_base()


class Config(Base):
    __tablename__ = "orgunit_settings"

    id = Column(Integer, primary_key=True)
    object = Column(UUIDType(binary=False))
    setting = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
