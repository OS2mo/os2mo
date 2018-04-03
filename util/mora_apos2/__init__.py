#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools

import flask
import flask_jsontools
import flask_restless
import flask_sqlalchemy


app = flask.Flask(__name__, static_folder=None)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/ballerup-apos2'

db = flask_sqlalchemy.SQLAlchemy(app)
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

attachedpersons = db.Table(
    'attachedpersons',
    db.Column('unitUuid', db.String(36), db.ForeignKey('unit.uuid'),
              primary_key=True),
    db.Column('personUuid', db.String(36),
              db.ForeignKey('person.uuid'), nullable=False,
              primary_key=True),
)

tasks = db.Table(
    'tasks',
    db.Column('uuid', db.String(36),
              db.ForeignKey('classes.uuid'), nullable=False,
              primary_key=True),
    db.Column('unitUuid', db.String(36), db.ForeignKey('unit.uuid'),
              primary_key=True),
)

unitlocation = db.Table(
    'unitlocation',
    db.Column('unitUuid', db.String(36), db.ForeignKey('unit.uuid')),
    db.Column('locationUuid', db.String(36),
              db.ForeignKey('GetGeographicDetails.uuid'))
)

functionpersons = db.Table(
    'functionpersons',
    db.Column('functionUuid', db.String(36),
              db.ForeignKey('functions.functionUuid'),
              nullable=False),
    db.Column('personUuid', db.String(36), db.ForeignKey('person.uuid'),
              nullable=False)
)

functiontasks = db.Table(
    'functiontasks',
    db.Column('functionUuid', db.String(36),
              db.ForeignKey('functions.functionUuid'),
              nullable=False),
    db.Column('taskUuid', db.String(36), db.ForeignKey('classes.uuid'),
              nullable=False)
)

functionunits = db.Table(
    'functionunits',
    db.Column('functionUuid', db.String(36),
              db.ForeignKey('functions.functionUuid'),
              nullable=False),
    db.Column('unitUuid', db.String(36), db.ForeignKey('unit.uuid'),
              nullable=False),
)


def api(**kwargs):
    @functools.wraps(api)
    def wrapper(model):
        manager.create_api(model, methods=['GET'], url_prefix='', **kwargs)
        return model

    return wrapper


@app.route('/')
@flask_jsontools.jsonapi
def index():
    return [
        str(rule)
        for rule in app.url_map.iter_rules()
        if "GET" in rule.methods
    ]


@api()
class Person(db.Model):
    uuid = db.Column(db.String(36), unique=True)
    objektid = db.Column(db.Integer, nullable=False, unique=True,
                         primary_key=True)
    userKey = db.Column(db.String(255))
    personNumber = db.Column(db.String(10))
    givenName = db.Column(db.String(255))
    surName = db.Column(db.String(255))
    addresseringsnavn = db.Column(db.String(45), nullable=False)
    koen = db.Column(db.String(5), nullable=False)

    attachments = db.relationship('Unit',
                                  secondary=attachedpersons,
                                  lazy='subquery',
                                  backref=db.backref('attachments', lazy=True))


@api(exclude_columns=['overordnetid', 'objectid'])
class Unit(db.Model):
    uuid = db.Column(db.String(36), nullable=False)
    type = db.Column(db.String(5), nullable=False)
    objectid = db.Column(db.Integer, nullable=False, primary_key=True)
    overordnetid = db.Column(db.Integer, db.ForeignKey('unit.objectid'),
                             nullable=False)
    navn = db.Column(db.String(255), nullable=False)
    brugervendtNoegle = db.Column(db.String(4), nullable=False)

    parent = db.relationship('Unit', remote_side=[objectid],
                             backref=db.backref('children', lazy=True))

    tasks = db.relationship('Class',
                            secondary=tasks,
                            lazy='subquery',
                            backref=db.backref('units', lazy=True))

    addresses = db.relationship('GeoDetail',
                                secondary=unitlocation,
                                lazy='subquery',
                                backref=db.backref('units', lazy=True))


@api()
class Classification(db.Model):
    __tablename__ = 'klassifikation'

    uuid = db.Column(db.String(36), primary_key=True, nullable=False)
    objectid = db.Column(db.Integer, nullable=False)
    brugervendtnoegle = db.Column(db.String(35), nullable=False)
    kaldenavn = db.Column(db.String(35), nullable=False)


@api()
class Class(db.Model):
    __tablename__ = 'classes'

    uuid = db.Column(db.String(36), nullable=False, primary_key=True)
    objektid = db.Column(db.Integer, db.ForeignKey('klassifikation.objectid'),
                         nullable=False)
    title = db.Column(db.String(255), nullable=False)
    brugervendtnoegle = db.Column(db.String(255), nullable=False)

    classification = db.relationship('Classification',
                                     backref=db.backref('classes', lazy=True))


@api()
class JobTitle(db.Model):
    __tablename__ = 'jobtitles'

    uuid = db.Column(db.String(36), nullable=False)
    objektid = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    brugervendtnoegle = db.Column(db.String(255), nullable=False)


@api()
class Location(db.Model):
    __tablename__ = 'locations'

    uuid = db.Column(db.String(36), primary_key=True)
    navn = db.Column(db.String(255), nullable=False)
    GeographicUuid = db.Column(db.String(36),
                               db.ForeignKey('GetGeographicDetails.uuid'),
                               nullable=False)
    unitUuid = db.Column(db.String(36), db.ForeignKey('unit.uuid'),
                         nullable=False)
    aabningstider = db.Column(db.String(255), nullable=False)
    pnummer = db.Column(db.String(255), nullable=False)
    primaer = db.Column(db.String(3), nullable=False)

    unit = db.relationship('Unit', backref=db.backref('locations'))
    details = db.relationship('GeoDetail', lazy='joined')


@api()
class ContactChannel(db.Model):
    __tablename__ = 'contactchannel'

    uuid = db.Column(db.String(36), primary_key=True)
    ownerUuid = db.Column(db.String(36), db.ForeignKey('person.uuid'),
                          index=True)
    typeUuid = db.Column(db.String(36), db.ForeignKey('classes.uuid'))
    value = db.Column(db.String(255))
    order_r = db.Column(db.Integer)
    usages = db.Column(db.String(255))

    type = db.relationship('Class',
                           backref=db.backref('contact_channels', lazy=True))

    location = db.relationship(
        'Location',
        primaryjoin="foreign(ContactChannel.ownerUuid)==Location.uuid",
        backref=db.backref('contact_channels'),
    )
    engagement = db.relationship(
        'Engagement',
        primaryjoin="foreign(ContactChannel.ownerUuid)==Engagement.uuid",
        backref=db.backref('contact_channels'),
    )


@api()
class ContactChannelProps(db.Model):
    __tablename__ = 'contactchannel_properties'

    uuid = db.Column('uuid', db.String(36),
                     db.ForeignKey('contactchannel.uuid'),
                     primary_key=True,
                     nullable=False)
    prop_uuid = db.Column(db.String(36), nullable=False)
    legend = db.Column(db.String(72), nullable=False)

    owner = db.relationship(
        'ContactChannel',
        backref=db.backref('properties', uselist=False),
    )


@api()
class GeoDetail(db.Model):
    __tablename__ = 'GetGeographicDetails'

    uuid = db.Column(db.String(36), index=True)
    objektid = db.Column(db.Integer, primary_key=True, nullable=False)
    postnummer = db.Column(db.Integer, nullable=False)
    postdistrikt = db.Column(db.String(35), nullable=False)
    bynavn = db.Column(db.String(35), nullable=False)
    vejnavn = db.Column(db.String(35), nullable=False)
    husnummer = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(255))

    coord_lat = db.Column('coordinate-lat', db.String(12))
    coord_long = db.Column('coordinate-long', db.String(12))


@api(exclude_columns=['stillingUuid', 'personUuid', 'unitUuid'])
class Engagement(db.Model):

    Id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), index=True)

    name = db.Column(db.String(255))
    userKey = db.Column(db.String(255))

    stillingUuid = db.Column(db.String(36), db.ForeignKey('classes.uuid'))
    personUuid = db.Column(db.String(36), db.ForeignKey('person.uuid'))
    unitUuid = db.Column(db.String(36), db.ForeignKey('unit.uuid'))
    locationUuid = db.Column(db.String(36), db.ForeignKey('locations.uuid'))

    position = db.relationship('Class',
                               backref=db.backref('engagements', lazy=True))
    unit = db.relationship('Unit')
    person = db.relationship('Person')


@api(exclude_columns=['stillingUuid', 'personUuid', 'unitUuid'])
class Functions(db.Model):
    functionUuid = db.Column(db.String(36), primary_key=True, nullable=False)
    objectid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(30), nullable=False)

    persons = db.relationship('Person',
                              secondary=functionpersons,
                              lazy='subquery',
                              backref=db.backref('functions', lazy=True))

    tasks = db.relationship('Class',
                            secondary=functiontasks,
                            lazy='subquery',
                            backref=db.backref('functions', lazy=True))

    units = db.relationship('Unit',
                            secondary=functionunits,
                            lazy='subquery',
                            backref=db.backref('functions', lazy=True))


@app.route('/test')
@flask_jsontools.jsonapi
def test():
    '''Print out differences between the 'classes' and 'jobtitles'
    tables.

    '''

    jobtitles = {
        obj.uuid: obj.__dict__
        for obj in db.session.query(JobTitle).order_by(JobTitle.uuid).all()
    }
    classes = {
        obj.uuid: obj.__dict__
        for obj in db.session.query(Class).order_by(Class.uuid).all()
    }

    bad = set()

    for k in jobtitles.keys() | classes.keys():
        if jobtitles[k] != classes[k]:
            for v in jobtitles[k].keys() | classes[k].keys():
                if v.startswith('_') or v == 'objektid':
                    continue

                c = classes[k][v]

                if v == 'title':
                    c = c[:45]
                if v == 'brugervendtnoegle':
                    c = c[:35]

                if jobtitles[k][v] != c:
                    bad.add(jobtitles[k]['uuid'])

    def to_dict(q):
        return list(map(
            flask_restless.helpers.to_dict,
            q.all(),
        ))

    return {
        objid: {
            'class': to_dict(Class.query.filter_by(uuid=objid)),
            'jobtitle': to_dict(JobTitle.query.filter_by(uuid=objid)),
        }
        for objid in sorted(bad)
    }
