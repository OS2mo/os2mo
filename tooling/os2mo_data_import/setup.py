# -- coding: utf-8 --

from setuptools import setup

setup(
    name='os2mo-importer',
    version='0.0.1',
    description='Data import utility for os2mo',
    author='Steffen Park',
    author_email='steffen@magenta.dk',
    license="MPL 2.0",
    packages=['os2mo_data_import'],
    zip_safe=False,
    install_requires=[
        "certifi==2018.8.24",
        "chardet==3.0.4",
        "idna==2.7",
        "requests==2.19.1",
        "urllib3==1.23"
    ]
)
