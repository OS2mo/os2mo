# -- coding: utf-8 --

import os
import json


# Settings
fixture_directory = "fixtures"


def load_fixture(fixture_name):

    fixture_location = os.path.dirname(__file__)

    path_to_file = os.path.join(
        fixture_location,
        fixture_directory,
        fixture_name
    )

    with open(path_to_file, "r") as file:
        content = file.read()

    return json.loads(content)
