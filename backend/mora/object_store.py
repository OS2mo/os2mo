# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from minio import Minio

from . import settings


def get_bucket_name():
    return "mo-exports-bucket"


def create_client():
    client = Minio(
        settings.config["minio"]["url"],
        access_key=settings.config["minio"]["access_key"],
        secret_key=settings.config["minio"]["secret_key"],
        secure=settings.config["minio"]["secure"]
    )
    return client
