#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

from sqlalchemy import Column, Index, Integer, String, Table
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB = os.environ.get('DB', 'localhost/ballerup')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASS = os.environ.get('DB_PASS', '')

engine = create_engine("mysql+pymysql://{}:{}@{}".format(DB_USER, DB_PASS, DB))

Base = declarative_base()
metadata = Base.metadata

Session = sessionmaker(bind=engine)
session = Session()

# OK
t_GetGeographicDetails = Table(
    'GetGeographicDetails', metadata,
    Column('uuid', String(36), index=True, primary_key=True),
    Column('objektid', Integer, nullable=False),
    Column('postnummer', Integer, nullable=False),
    Column('postdistrikt', String(35), nullable=False),
    Column('bynavn', String(35), nullable=False),
    Column('vejnavn', String(35), nullable=False),
    Column('husnummer', String(5), nullable=False),
    Column('name', String(255)),
    Column('coordinate-lat', String(12)),
    Column('coordinate-long', String(12)),
    Index('FULL TEXT', 'name', 'uuid')
)


class GetGeographicDetails(Base):
    __tablename__ = 'GetGeographicalDetails'
    __table__ = t_GetGeographicDetails


# OK
t_attachedpersons = Table(
    'attachedpersons', metadata,
    Column('unitUuid', String(36), nullable=False, primary_key=True),
    Column('personUuid', String(36), nullable=False, primary_key=True)
)


class Attachedpersons(Base):
    __table__ = t_attachedpersons


# OK
t_classes = Table(
    'classes', metadata,
    Column('uuid', String(36), nullable=False),
    Column('objektid', Integer, nullable=False),
    Column('title', String(255), nullable=False),
    Column('brugervendtnoegle', String(255), nullable=False)
)

# OK
t_contactchannel = Table(
    'contactchannel', metadata,
    Column('uuid', String(36), index=True, primary_key=True),
    Column('ownerUuid', String(36), index=True),
    Column('typeUuid', String(36)),
    Column('value', String(255)),
    Column('order_r', Integer),
    Column('usages', String(255))
)


class ContactChannel(Base):
    __tablename__ = 'ContactChannel'
    __table__ = t_contactchannel


# OK
t_contactchannel_properties = Table(
    'contactchannel_properties', metadata,
    Column('uuid', String(36), nullable=False),
    Column('prop_uuid', String(36), nullable=False),
    Column('legend', String(72), nullable=False)
)


# OK
class Engagement(Base):
    __tablename__ = 'engagement'
    __table_args__ = (
        Index('userKeyIndex', 'personUuid', 'userKey'),
        Index('personUuid', 'personUuid', 'uuid', 'userKey', 'unitUuid',
              'locationUuid', 'name')
    )

    uuid = Column(String(36), index=True)
    stillingUuid = Column(String(36))
    userKey = Column(String(255))
    personUuid = Column(String(36))
    unitUuid = Column(String(36))
    locationUuid = Column(String(36))
    name = Column(String(255))
    Id = Column(Integer, primary_key=True)


# EMPTY
t_facetter = Table(
    'facetter', metadata,
    Column('uuid', String(36), nullable=False),
    Column('type', String(5), nullable=False),
    Column('objektid', Integer, nullable=False),
    Column('brugervendtnoegle', String(35), nullable=False),
    Column('title', String(75), nullable=False)
)

# OK
t_functionpersons = Table(
    'functionpersons', metadata,
    Column('functionUuid', String(36), nullable=False, primary_key=True),
    Column('personUuid', String(36), nullable=False, primary_key=True),
)


class Functionpersons(Base):
    __tablename__ = 'functionpersons'
    __table__ = t_functionpersons


# OK
t_functions = Table(
    'functions', metadata,
    Column('functionUuid', String(36), nullable=False, primary_key=True),
    Column('objectid', Integer, nullable=False),
    Column('name', String(30), nullable=False)
)


class Functions(Base):
    __tablename__ = 'functions'
    __table__ = t_functions


# OK
t_functiontasks = Table(
    'functiontasks', metadata,
    Column('functionUuid', String(36), nullable=False, primary_key=True),
    Column('taskUuid', String(36), nullable=False, primary_key=True)
)


class Functiontasks(Base):
    __tablename__ = 'functiontasks'
    __table__ = t_functiontasks


# OK
t_functionunits = Table(
    'functionunits', metadata,
    Column('functionUuid', String(36), nullable=False, primary_key=True),
    Column('unitUuid', String(36), nullable=False, primary_key=True),
    Index('FullIndex', 'functionUuid', 'unitUuid')
)


class Functionunits(Base):
    __tablename__ = 'functionunits'
    __table__ = t_functionunits


# OK - DUPLICATE OF CLASSES? -- see /test
t_jobtitles = Table(
    'jobtitles', metadata,
    Column('uuid', String(36), nullable=False, primary_key=True),
    Column('objektid', Integer, nullable=False),
    Column('title', String(45), nullable=False),
    Column('brugervendtnoegle', String(35), nullable=False)
)


class Jobtitles(Base):
    __tablename__ = 'jobtitles'
    __table__ = t_jobtitles


# OK - BUT HOW?
t_klassifikation = Table(
    'KLASSIFIKATION_UUID', metadata,
    Column('uuid', String(36), nullable=False),
    Column('objectid', Integer, nullable=False),
    Column('brugervendtnoegle', String(35), nullable=False),
    Column('kaldenavn', String(35), nullable=False)
)

# OK:
t_locations = Table(
    'locations', metadata,
    Column('uuid', String(36), nullable=False, primary_key=True),
    Column('navn', String(255), nullable=False),
    Column('GeographicUuid', String(36), nullable=False),
    Column('unitUuid', String(36), nullable=False),
    Column('aabningstider', String(255), nullable=False),
    Column('pnummer', String(255), nullable=False),
    Column('primaer', String(3), nullable=False)
)


# OK:
class Locations(Base):
    __tablename__ = 'locations'
    __table__ = t_locations


t_person = Table(
    'person', metadata,
    Column('uuid', String(36), unique=True),
    Column('objektid', Integer, nullable=False, unique=True, primary_key=True),
    Column('userKey', String(255)),
    Column('personNumber', String(10)),
    Column('givenName', String(255)),
    Column('surName', String(255)),
    Column('addresseringsnavn', String(45), nullable=False),
    Column('koen', String(5), nullable=False),
    Index('FullText', 'userKey', 'givenName', 'surName')
)


# OK:
class Person(Base):
    __tablename__ = 'person'
    __table__ = t_person


# OK:
t_tasks = Table(
    'tasks', metadata,
    Column('uuid', String(36), nullable=False),
    Column('unitUuid', String(36), nullable=False)
)

# OK:
t_unit = Table(
    'unit', metadata,
    Column('uuid', String(36), nullable=False, primary_key=True),
    Column('type', String(5), nullable=False),
    Column('objectid', Integer, nullable=False),
    Column('overordnetid', Integer, nullable=False),
    Column('navn', String(255), nullable=False),
    Column('brugervendtNoegle', String(4), nullable=False),
    Index('FullText', 'uuid', 'navn', 'brugervendtNoegle'),
    Index('uuid', 'uuid', 'objectid', unique=True)
)


class Unit(Base):
    __tablename__ = 'unit'
    __table__ = t_unit


# OK:
t_unitlocation = Table(
    'unitlocation', metadata,
    Column('unitUuid', String(36)),
    Column('locationUuid', String(36))
)

# EMPTY
t_v2_contactchannel = Table(
    'v2_contactchannel', metadata,
    Column('uuid', String(36), index=True),
    Column('ownerUuid', String(36), index=True),
    Column('typeUuid', String(36)),
    Column('value', String(255)),
    Column('order_r', Integer),
    Column('usages', String(255)),
    Column('sms', ENUM('0', '1'), nullable=False),
    Column('begraenset', ENUM('0', '1'), nullable=False)
)
