import typing
import uuid

import hypothesis
from hypothesis import strategies as st
from hypothesis import assume
from hypothesis import given

from pydantic import ValidationError

from mora.common import create_klasse_payload
from mora.common import _create_virkning

from ramodels.lora.klasse import Klasse


def new_create_klasse_payload(
    valid_from: str,
    valid_to: str,
    bvn: str,
    title: str,
    facet_uuid: uuid.UUID,
    org_uuid: uuid.UUID,
    owner: typing.Optional[uuid.UUID] = None,
    description: typing.Optional[str] = None,
    scope: typing.Optional[str] = None,
    parent_uuid: typing.Optional[uuid.UUID] = None,
) -> dict:
    virkning = _create_virkning(valid_from, valid_to)

    # Misses owner, description and parent_uuid
    lora_klasse = Klasse.from_simplified_fields(
        facet_uuid=facet_uuid,
        user_key=bvn,
        organisation_uuid=org_uuid,
        title=title,
        uuid=None,
        scope=scope,
        from_date=valid_from,
        to_date=valid_to
    )
    return lora_klasse.dict(by_alias=True, exclude_none=True)


@given(
    valid_from=st.datetimes(),
    valid_to=st.datetimes(),
    bvn=st.text(),
    title=st.text(),
    facet_uuid=st.uuids(),
    org_uuid=st.uuids(),
    owner=st.one_of(st.none(), st.uuids()),
    description=st.one_of(st.none(), st.text()),
    scope=st.one_of(st.none(), st.text()),
    parent_uuid=st.one_of(st.none(), st.uuids())
)
def test_equivalence(**kwargs):
    kwargs["valid_from"] = kwargs["valid_from"].isoformat()
    kwargs["valid_to"] = kwargs["valid_to"].isoformat()

    new = None
    new_exception = None
    try:
        new = new_create_klasse_payload(**kwargs)
    except Exception as exception:
        new_exception = exception

    old = None
    old_exception = None
    try:
        old = create_klasse_payload(**kwargs)
    except Exception as exception:
        old_exception = exception

    if isinstance(new_exception, ValidationError):
        assume(False)

    if old and not new:
        raise new_exception
    if not old and new:
        raise old_exception
    assert type(old_exception) == type(new_exception)

    from fastapi.encoders import jsonable_encoder
    import json
    old = json.loads(json.dumps(jsonable_encoder(old)).lower())
    new = json.loads(json.dumps(jsonable_encoder(new)).lower())
    old.pop("uuid", None)
    new.pop("uuid", None)

    assert old == new
