#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from sqlalchemy import Column, Index, Integer, String, Table
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


# OK
t_GetGeographicDetails = Table(
    'GetGeographicDetails', metadata,
    Column('uuid', String(36), index=True),
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


# OK
t_attachedpersons = Table(
    'attachedpersons', metadata,
    Column('unitUuid', String(36), nullable=False),
    Column('personUuid', String(36), nullable=False)
)


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
    Column('uuid', String(36), index=True),
    Column('ownerUuid', String(36), index=True),
    Column('typeUuid', String(36)),
    Column('value', String(255)),
    Column('order_r', Integer),
    Column('usages', String(255))
)


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
    Column('functionUuid', String(36), nullable=False),
    Column('personUuid', String(36), nullable=False)
)


# OK
t_functions = Table(
    'functions', metadata,
    Column('functionUuid', String(36), nullable=False),
    Column('objectid', Integer, nullable=False),
    Column('name', String(30), nullable=False)
)


# OK
t_functiontasks = Table(
    'functiontasks', metadata,
    Column('functionUuid', String(36), nullable=False),
    Column('taskUuid', String(36), nullable=False)
)


# OK
t_functionunits = Table(
    'functionunits', metadata,
    Column('functionUuid', String(36), nullable=False),
    Column('unitUuid', String(36), nullable=False),
    Index('FullIndex', 'functionUuid', 'unitUuid')
)


# OK - DUPLICATE OF CLASSES? -- see /test
t_jobtitles = Table(
    'jobtitles', metadata,
    Column('uuid', String(36), nullable=False),
    Column('objektid', Integer, nullable=False),
    Column('title', String(45), nullable=False),
    Column('brugervendtnoegle', String(35), nullable=False)
)


# OK - BUT HOW?
t_klassifikation = Table(
    'klassifikation', metadata,
    Column('uuid', String(36), nullable=False),
    Column('objectid', Integer, nullable=False),
    Column('brugervendtnoegle', String(35), nullable=False),
    Column('kaldenavn', String(35), nullable=False)
)


# OK:
t_locations = Table(
    'locations', metadata,
    Column('uuid', String(36), nullable=False),
    Column('navn', String(255), nullable=False),
    Column('GeographicUuid', String(36), nullable=False),
    Column('unitUuid', String(36), nullable=False),
    Column('aabningstider', String(255), nullable=False),
    Column('pnummer', String(255), nullable=False),
    Column('primaer', String(3), nullable=False)
)


# OK:
t_person = Table(
    'person', metadata,
    Column('uuid', String(36), unique=True),
    Column('objektid', Integer, nullable=False, unique=True),
    Column('userKey', String(255)),
    Column('personNumber', String(10)),
    Column('givenName', String(255)),
    Column('surName', String(255)),
    Column('addresseringsnavn', String(45), nullable=False),
    Column('koen', String(5), nullable=False),
    Index('FullText', 'userKey', 'givenName', 'surName')
)


# OK:
t_tasks = Table(
    'tasks', metadata,
    Column('uuid', String(36), nullable=False),
    Column('unitUuid', String(36), nullable=False)
)


# OK:
t_unit = Table(
    'unit', metadata,
    Column('uuid', String(36), nullable=False),
    Column('type', String(5), nullable=False),
    Column('objectid', Integer, nullable=False),
    Column('overordnetid', Integer, nullable=False),
    Column('navn', String(255), nullable=False),
    Column('brugervendtNoegle', String(4), nullable=False),
    Index('FullText', 'uuid', 'navn', 'brugervendtNoegle'),
    Index('uuid', 'uuid', 'objectid', unique=True)
)

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
