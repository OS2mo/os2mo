# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os

# Parts of the LoRa test suite assume that Keycloak authentication is turned on.
# We turn it on here before running the actual test suite.
os.environ["LORA_AUTH"] = "true"
