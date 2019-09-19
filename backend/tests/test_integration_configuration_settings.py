#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import psycopg2

import mora.settings as settings
from . import util


class Tests(util.LoRATestCase):

    def _create_conf_data(self, inconsistent=False):

        defaults = {'show_roles': 'True',
                    'show_user_key': 'False',
                    'show_location': 'True'}

        p_url = test_support.psql().url()
        p_port = p_url[p_url.rfind(':') + 1:p_url.rfind('/')]

        with psycopg2.connect(p_url) as conn:
            conn.autocommit = True
            with conn.cursor() as curs:
                try:
                    curs.execute(
                        "CREATE USER {} WITH ENCRYPTED PASSWORD '{}'".format(
                            settings.CONF_DB_USER,
                            settings.CONF_DB_PASSWORD
                        )
                    )
                except psycopg2.ProgrammingError:
                    curs.execute(
                        "DROP DATABASE {};".format(
                            settings.CONF_DB_NAME,
                        )
                    )

                curs.execute(
                    "CREATE DATABASE {} OWNER {};".format(
                        settings.CONF_DB_NAME,
                        settings.CONF_DB_USER
                    )
                )
                curs.execute(
                    "GRANT ALL PRIVILEGES ON DATABASE {} TO {};".format(
                        settings.CONF_DB_NAME,
                        settings.CONF_DB_USER
                    )
                )

        with psycopg2.connect(user=settings.CONF_DB_USER,
                              dbname=settings.CONF_DB_NAME,
                              host=settings.CONF_DB_HOST,
                              password=settings.CONF_DB_PASSWORD,
                              port=p_port) as conn:
            conn.autocommit = True
            with conn.cursor() as curs:

                curs.execute("""
                CREATE TABLE orgunit_settings(id serial PRIMARY KEY,
                object UUID, setting varchar(255) NOT NULL,
                value varchar(255) NOT NULL);
                """)

                query = """
                INSERT INTO orgunit_settings (object, setting, value)
                VALUES (NULL, %s, %s);
                """

                for setting, value in defaults.items():
                    curs.execute(query, (setting, value))

                if inconsistent:
                    # Insert once more, making an invalid configuration set
                    for setting, value in defaults.items():
                        curs.execute(query, (setting, value))
        return p_port

    def test_global_user_settings_read(self):
        """
        Test that it is possible to correctly read default global settings.
        """

        p_port = self._create_conf_data()
        url = '/service/configuration'
        with util.override_settings(CONF_DB_PORT=p_port):
            user_settings = self.assertRequest(url)
            self.assertTrue('show_location' in user_settings)
            self.assertTrue('show_user_key' in user_settings)
            self.assertTrue('show_roles' in user_settings)
            self.assertTrue(user_settings['show_location'] is True)

    def test_inconsistent_settings(self):
        """
        Test that the conf module will raise in exception if the configuration
        settings are inconsistent.
        """

        p_port = self._create_conf_data(inconsistent=True)
        url = '/service/configuration'
        payload = {"org_units": {"show_roles": "False"}}
        assertion_raised = False
        with util.override_settings(CONF_DB_PORT=p_port):
            try:
                self.assertRequest(url, json=payload)
            except Exception:
                assertion_raised = True
        self.assertTrue(assertion_raised)

    def test_global_user_settings_write(self):
        """
        Test that it is possible to write a global setting and read it back.
        """

        p_port = self._create_conf_data()
        url = '/service/configuration'

        with util.override_settings(CONF_DB_PORT=p_port):
            payload = {"org_units": {"show_roles": "False"}}
            self.assertRequest(url, json=payload)
            user_settings = self.assertRequest(url)
            self.assertTrue(user_settings['show_roles'] is False)

            payload = {"org_units": {"show_roles": "True"}}
            self.assertRequest(url, json=payload)
            user_settings = self.assertRequest(url)
            self.assertTrue(user_settings['show_roles'] is True)

    def test_ou_user_settings(self):
        """
        Test that reading and writing settings on units works corrcectly.
        """

        p_port = self._create_conf_data()
        self.load_sample_structures()
        uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        with util.override_settings(CONF_DB_PORT=p_port):
            payload = {"org_units": {"show_user_key": "True"}}
            url = '/service/ou/{}/configuration'.format(uuid)
            self.assertRequest(url, json=payload)

            user_settings = self.assertRequest(url)
            self.assertTrue(user_settings['show_user_key'] is True)

    def test_ou_service_response(self):
        """
        Test that the service endpoint for units returns the correct
        configuration settings, including that this endpoint should convert
        the magic strings 'True' and 'False' into boolean values.
        """
        p_port = self._create_conf_data()
        self.load_sample_structures()
        uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        with util.override_settings(CONF_DB_PORT=p_port):
            url = '/service/ou/{}/configuration'.format(uuid)
            payload = {"org_units": {"show_user_key": "True"}}
            self.assertRequest(url, json=payload)
            payload = {"org_units": {"show_location": "False"}}
            self.assertRequest(url, json=payload)

            service_url = '/service/ou/{}/'.format(uuid)
            response = self.assertRequest(service_url)
            user_settings = response['user_settings']['orgunit']
            print(user_settings)
            self.assertTrue(user_settings['show_user_key'])
            self.assertFalse(user_settings['show_location'])
