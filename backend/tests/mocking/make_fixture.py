#!/usr/bin/env python3
# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Create a JSON fixture containing the specified URLs
"""

import json
import sys

import requests


def map_response(r):
    r.raise_for_status()
    return r.url, r.json()


if __name__ == "__main__":
    data = dict(map(map_response, map(requests.get, sys.argv[1:])))

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
