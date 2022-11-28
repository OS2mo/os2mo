<!--
SPDX-FileCopyrightText: Magenta ApS

SPDX-License-Identifier: MPL-2.0
-->

# OS2mo HTTP Trigger Protocol

This package contains the interfaces used for the OS2mo http trigger protocol.

## Usage
Install into your project using `pip`:
```
pip install os2mo-http-trigger-protocol
```

Then import it inside a Python file:
```
from typing import List

from os2mo_http_trigger_protocol import (
    EventType,
    MOTriggerPayload,
    MOTriggerRegister,
    RequestType,
)
from fastapi import FastAPI

app = FastAPI()


@app.get(
    "/triggers",
    summary="List triggers to be registered.",
    response_model=List[MOTriggerRegister],
)
def triggers():
    """List triggers to be registered."""
    return [
        {
            "event_type": EventType.ON_BEFORE,
            "request_type": RequestType.EDIT,
            "role_type": "org_unit",
            "url": "/triggers/ou/edit",
        }
    ]

@app.post(
    "/triggers/ou/edit",
    summary="Print that an organizational unit has been edited",
)
async def triggers_ou_create(payload: MOTriggerPayload):
    """Fired when an OU has been created."""
    return {"Hello": "World"}
```
