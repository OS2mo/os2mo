#!/usr/bin/env python3
# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Update, i.e. re-fetch, a JSON fixture
"""

import json
import os
import sys

import click
import requests


@click.command()
@click.option("-u", "--base-url", default="http://localhost:5000")
@click.argument(
    "files", type=click.Path(exists=True, dir_okay=False), required=True, nargs=-1
)
def main(base_url, files):
    sess = requests.Session()

    def get(url):
        if url.startswith("/"):
            url = base_url + url
        print(url, file=sys.stderr)
        r = sess.get(url)
        r.raise_for_status()

        return r.json()

    for fn in files:
        with open(fn) as fp:
            d = json.load(fp)

        with open(fn + "~", "w") as fp:
            json.dump(
                dict(zip(d, map(get, d))),
                fp,
                indent=2,
                sort_keys=True,
            )

            # ensure trailing newline
            fp.write("\n")

        os.rename(fp.name, fn)


if __name__ == "__main__":
    main()
