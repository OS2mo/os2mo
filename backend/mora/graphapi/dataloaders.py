# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Dict
from typing import List

from strawberry.dataloader import DataLoader

from mora.service import org

from mora.graphapi.schema import Organisation


async def load_org(keys: List[int]) -> List[Organisation]:
    """Dataloader function to load Organisation.

    A dataloader is used even though only a single Organisation can ever exist, as the
    dataloader also implements caching, and as there may be more than one reference to
    the organisation within one query.
    """
    # We fake the ID of our Organisation as 0 and expect nothing else as inputs
    keyset = set(keys)
    if keyset != {0}:
        raise ValueError("Only one organisation can exist!")

    obj = await org.get_configured_organisation()
    return [Organisation.construct(obj)] * len(keys)


def get_loaders() -> Dict[str, DataLoader]:
    """Get all available dataloaders as a dictionary."""
    return {
        "org_loader": DataLoader(load_fn=load_org),
    }
