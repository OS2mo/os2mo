# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType

Base = declarative_base()


class Config(Base):
    __tablename__ = "orgunit_settings"

    id = Column(Integer, primary_key=True)
    object = Column(UUIDType(binary=False))
    setting = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
