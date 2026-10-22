# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The CEL environment that rolebinding rules are written against."""

from typing import NewType

from cel_expr_python.cel import NewEnv
from cel_expr_python.cel import Type
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from google.protobuf.descriptor_pool import DescriptorPool

from mora.cel._compile import compile
from mora.cel._types import CEL
from mora.cel._types import CelError

RolebindingRuleCEL = NewType("RolebindingRuleCEL", CEL)

_PACKAGE = "mo.rolebinding"


def _descriptor_pool() -> DescriptorPool:
    file = FileDescriptorProto(
        name="mo/rolebinding.proto", package=_PACKAGE, syntax="proto3"
    )

    STRING = FieldDescriptorProto.TYPE_STRING
    MESSAGE = FieldDescriptorProto.TYPE_MESSAGE
    OPTIONAL = FieldDescriptorProto.LABEL_OPTIONAL
    REPEATED = FieldDescriptorProto.LABEL_REPEATED

    # Messages are the "types" allowed in the CEL environment.
    # The inner tuple is (field type, label, and type name). The label can be
    # confusing, and some things like ITUser.uuid are obviously required, not
    # OPTIONAL:
    # https://capnproto.org/faq.html#how-do-i-make-a-field-required-like-in-protocol-buffers
    MESSAGES: dict[str, dict[str, tuple[int, int, str | None]]] = {
        "ITUser": {
            "uuid": (STRING, OPTIONAL, None),
            "user_key": (STRING, OPTIONAL, None),
            "external_id": (STRING, OPTIONAL, None),
            "engagements": (MESSAGE, REPEATED, "Engagement"),
        },
        "Engagement": {
            "uuid": (STRING, OPTIONAL, None),
            "job_function": (MESSAGE, OPTIONAL, "JobFunction"),
            "engagement_type": (MESSAGE, OPTIONAL, "EngagementType"),
            "org_unit": (MESSAGE, OPTIONAL, "OrgUnit"),
        },
        "JobFunction": {
            "uuid": (STRING, OPTIONAL, None),
        },
        "EngagementType": {
            "uuid": (STRING, OPTIONAL, None),
        },
        "OrgUnit": {
            "uuid": (STRING, OPTIONAL, None),
            "path_uuids": (STRING, REPEATED, None),
        },
    }

    for message_name, fields in MESSAGES.items():
        message = file.message_type.add(name=message_name)
        for number, (field_name, (field_type, label, type_name)) in enumerate(
            fields.items(), start=1
        ):
            field = message.field.add(
                name=field_name, number=number, type=field_type, label=label
            )
            if type_name is not None:
                field.type_name = f".{_PACKAGE}.{type_name}"

    pool = DescriptorPool()
    pool.Add(file)
    return pool


_POOL = _descriptor_pool()
_ENV = NewEnv(
    descriptor_pool=_POOL,
    variables={"ituser": Type(f"{_PACKAGE}.ITUser")},
)


def validate(expression: str) -> RolebindingRuleCEL:
    return_type = compile(_ENV, expression).return_type()
    if return_type != Type.BOOL:
        raise CelError(f"the expression must be true or false, but is {return_type}")
    return RolebindingRuleCEL(CEL(expression))
