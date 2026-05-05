# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Parser utility to get LoRa data from localhost.

This script is only intended for one-time use. Results are committed to git and used
when mocking LoRa with pytest fixtures.
"""

import json
from pathlib import Path

import httpx
from mora.lora import LoraObjectType


def main() -> None:
    """Get relevant data as given by LoraObjectType from local LoRa.

    Data is dumped to a JSON file with a name corresponding to the LoraObjectType name.
    """
    data_path = Path(__file__).parent
    for lora_obj in LoraObjectType:
        json_file = data_path / f"{lora_obj.name}.json"
        resp = httpx.get(f"http://localhost:8080/{lora_obj.value}?list=1", timeout=None)
        data = resp.json()
        json_file.write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
