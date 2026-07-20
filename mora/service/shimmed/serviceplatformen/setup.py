#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from setuptools import setup
from setuptools import find_packages

__version__ = "1.0.3"

setup(
    name="service_person_stamdata_udvidet",
    version=__version__,
    description="PersonBaseExtendedService integration for the PersonBaseExtendedService webservice which is a part of SF1520 API (https://digitaliseringskataloget.dk/integration/sf1520)",
    author="Magenta ApS",
    author_email="info@magenta.dk",
    license="MPL 2.0",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "": ["*.txt", "*.xml"]
    },
    zip_safe=False,
    install_requires=[
        "certifi==2022.12.7",
        "chardet==3.0.4",
        "charset-normalizer==2.1.1",
        "idna==3.4",
        "Jinja2==3.1.2",
        "MarkupSafe==2.1.2",
        "requests==2.28.2",
        "urllib3==1.26.14",
        "xmltodict==0.13.0",
        ],
    classifiers=[
        "Development Status :: RC 1.0",
        "Topic :: Utilities",
        "License :: OSI Approved :: MPL License",
    ],
    url="https://github.com/magenta-aps/service_person_stamdata_udvidet",
)
