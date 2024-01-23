# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
import re
from copy import deepcopy

import pandas as pd
from fastramqpi.context import Context
from pydantic import parse_obj_as
from ramodels.mo.employee import Employee

from .config import UsernameGeneratorConfig
from .ldap import paged_search
from .logging import logger
from .utils import combine_dn_strings
from .utils import remove_vowels


class UserNameGeneratorBase:
    """
    Class with functions to generate valid LDAP usernames.

    Each customer could have his own username generator function in here. All you need
    to do, is refer to the proper function inside the json dict.
    """

    def __init__(self, context: Context):
        self.context = context
        self.user_context = context["user_context"]
        self.settings = self.user_context["settings"]

        self.mapping = self.user_context["mapping"]

        self.username_generator = parse_obj_as(
            UsernameGeneratorConfig, self.mapping["username_generator"]
        )
        self.char_replacement = self.username_generator.char_replacement
        self.forbidden_usernames = [
            u.lower()
            for u in self.username_generator.forbidden_usernames
            if not self.is_filename(u)
        ]
        self.combinations = self.username_generator.combinations_to_try

        self.dataloader = self.user_context["dataloader"]

        self.files_with_forbidden_usernames = [
            u
            for u in self.username_generator.forbidden_usernames
            if self.is_filename(u)
        ]

        for file in self.files_with_forbidden_usernames:
            self.forbidden_usernames.extend(self.read_usernames_from_text_file(file))

        logger.info(f"Found {len(self.forbidden_usernames)} forbidden usernames")

    @staticmethod
    def is_filename(string):
        """
        Return True if the string is a csv-formatted file
        """
        if string.lower().endswith(".csv"):
            return True
        elif string.lower().endswith(".txt"):
            return True
        else:
            return False

    def read_usernames_from_text_file(self, filename: str) -> list[str]:
        """
        Read usernames from a csv-formatted text file.

        Notes
        ----------
        - The text file can only contain one column and shall only contain usernames
        - The text file should not have a header.
        """
        logger.info(f"Reading {filename}")

        full_path = os.path.join(
            self.user_context["forbidden_usernames_path"],
            filename,
        )
        csv = pd.read_csv(full_path, names=["forbidden_usernames"])

        return [name.lower() for name in csv.loc[:, "forbidden_usernames"]]

    def get_existing_values(self, attributes: list[str]):
        searchParameters = {
            "search_filter": "(objectclass=*)",
            "attributes": attributes,
        }
        search_base = self.settings.ldap_search_base
        output = {}
        search_result = paged_search(self.context, searchParameters, search_base)
        for attribute in attributes:
            output[attribute] = [
                entry["attributes"][attribute].lower()
                for entry in search_result
                if entry["attributes"][attribute]
            ]
        return output

    def _make_cn(self, username_string: str):

        return f"CN={username_string}"

    def _make_dn(self, username_string: str) -> str:

        cn = self._make_cn(username_string)
        dn = combine_dn_strings(
            [
                cn,
                self.settings.ldap_ou_for_new_users,
                self.settings.ldap_search_base,
            ]
        )

        return dn

    def _name_fixer(self, name_parts: list[str]) -> list[str]:
        """Cleanup a structured name to remove non-ascii characters.

        Context:
            self.char_replacement:
                Dictionary from one set of characters to their replacements.

        Args:
            name_parts: An array of names; given_name, middlenames, surname.

        Returns:
            `name_parts` where non-ascii characters have been replaced
            according to the char_replacement map, or if unmatched, removed.
        """

        def fix_name(name: str) -> str:
            # Replace according to replacement list
            for char, replacement in self.char_replacement.items():
                name = name.replace(char, replacement)
            # Remove all remaining characters outside a-z
            return re.sub(r"[^a-z]+", "", name.lower())

        return list(map(fix_name, name_parts))

    def _machine_readable_combi(self, combi: str) -> tuple[list[int | None], int]:
        """Converts a name to a machine processable internal format.

        Args:
            combi: Combination to create a username from. For example "F123LX".

        Returns:
            A two-tuple containing the internal combi format and the max name
            entry we will look up.

        Example:
            Given `combi = "F123LX"`, we return `([0,1,2,3,-1,None], 3)`.
            The name name entry `3` is simply the highest number contained
            within the internal combi format, and the internal combi format
            is produced according to the following lookup table.
        """
        char2pos = {
            # First name
            "F": 0,
            # First middle name
            "1": 1,
            # Second middle name
            "2": 2,
            # Third middle name
            "3": 3,
            # Last name (independent of middle names)
            "L": -1,
            "X": None,
        }
        readable_combi = [char2pos[x] for x in combi]
        max_position = max((x for x in readable_combi if x is not None), default=-1)
        return (readable_combi, max_position)

    def _create_from_combi(self, name: list, combi: str):
        """
        Create a username from a name and a combination.

        Parameters
        -------------
        name : list
            Name of the user given as a list with at least two elements.
        combi : str
            Combination to create a username from. For example "F123LX"

        Returns
        -----------
        username : str
            Username which was generated according to the combi. Note that this
            username still contains 'X' characters, which need to be replaced with
            a number

        Notes
        ---------
        Inspired by ad_integration/usernames.py
        """

        # Convert combi into machine readable code.
        # For example: combi = "F123LX" returns code = [0,1,2,3,-1,None]
        (code, max_position) = self._machine_readable_combi(combi)

        # Do not use codes that uses more names than the actual person has
        if max_position > len(name) - 2:
            return None

        # Do not use codes that require a last name if the person has no last name
        if not name[-1] and -1 in code:
            return None

        # First letter is always first letter of first position
        if code[0] is not None:
            relevant_name = code[0]
            username = name[relevant_name][0].lower()
        else:
            # None translates to 'X'. This is replaced with a number later on.
            username = "X"

        # Loop over all remaining entries in the combi
        current_char = 0
        for i in range(1, len(code)):
            if code[i] == code[i - 1]:
                current_char += 1
            else:
                current_char = 0

            if code[i] is not None:
                relevant_name = code[i]
                if current_char >= len(name[relevant_name]):
                    username = None
                    break
                username += name[relevant_name][current_char].lower()
            else:
                # None translates to 'X'. This is replaced with a number later on.
                username += "X"
        return username

    def _create_username(self, name: list, existing_usernames: list[str]) -> str:
        """
        Create a new username in accordance with the rules specified in the json file.
        The username will be the highest quality available and the value will be
        added to list of used names, so consequtive calles with the same name
        will keep returning new names until the algorithm runs out of options
        and a RuntimeException is raised.

        :param name: Name of the user given as a list with at least two elements.
        :return: New username generated.

        Inspired by ad_integration/usernames.py
        """
        name = self._name_fixer(name)

        # The permutation is a number inside the username, it is normally only used in
        # case a username is already occupied. It can be specified using 'X' in the
        # username template.
        #
        # The first attempted permutation should be '2':
        # For example; If 'cvt' is occupied, a username 'cvt2' will be generated.
        #
        # The last attempted permutation is '9' - because we would like to limit the
        # permutation counter to a single digit.
        for combi in self.combinations:
            for permutation_counter in range(2, 10):
                username = self._create_from_combi(name, combi)
                if not username:
                    continue
                final_username: str = username.replace("X", str(permutation_counter))
                if final_username not in existing_usernames:
                    if username.replace("X", "") not in self.forbidden_usernames:
                        return final_username

        # If we get to here, we completely failed to make a username
        raise RuntimeError("Failed to create user name.")

    def _create_common_name(self, name: list, existing_common_names: list[str]) -> str:
        """
        Create an LDAP-style common name (CN) based on first and last name

        If a name exists, "_2" is added. If that one also exists, "_3" is added,
        and so on

        Examples
        -------------
        >>> _create_common_name(["Keanu","Reeves"])
        >>> "Keanu Reeves"
        """
        clean_name = deepcopy([n for n in name if n])
        common_name = " ".join(clean_name)

        # Shorten a name if it is over 64 chars
        # see http://msdn.microsoft.com/en-us/library/ms675449(VS.85).aspx
        while len(common_name) > 60:
            if len(clean_name) <= 2:
                # Cut off the name (leave place for the permutation counter)
                common_name = " ".join(clean_name)[:60]
            else:
                clean_name.pop(-2)  # Remove the last middle name
                common_name = " ".join(clean_name)  # Try to make a name again

        permutation_counter = 2
        while common_name.lower() in existing_common_names:
            common_name = (
                common_name.replace(f"_{permutation_counter-1}", "")
                + f"_{permutation_counter}"
            )
            permutation_counter += 1

            if permutation_counter >= 1000:
                raise RuntimeError("Failed to create common name")

        return common_name

    async def _get_employee_ldap_attributes(self, employee: Employee, dn: str):
        converter = self.user_context["converter"]
        employee_ldap = await converter.to_ldap(
            {"mo_employee": employee}, "Employee", dn
        )
        attributes = employee_ldap.dict()
        attributes.pop("dn")

        return attributes

    def _get_existing_names(self):
        existing_values = self.get_existing_values(
            ["cn", "sAMAccountName", "userPrincipalName"]
        )

        user_principal_names = [
            s.split("@")[0] for s in existing_values["userPrincipalName"]
        ]

        existing_usernames = existing_values["sAMAccountName"] + user_principal_names
        existing_common_names = existing_values["cn"]

        return existing_usernames, existing_common_names


class UserNameGenerator(UserNameGeneratorBase):
    async def generate_dn(self, employee: Employee) -> str:
        """
        Generates a LDAP DN (Distinguished Name) based on information from a MO Employee
        object.

        Also adds an object to LDAP with this DN
        """
        existing_usernames, existing_common_names = self._get_existing_names()

        givenname = employee.givenname
        surname = employee.surname
        name = givenname.split(" ")[:4] + [surname]

        username = self._create_username(name, existing_usernames)
        logger.info(f"Generated username for {givenname} {surname}: '{username}'")

        common_name = self._create_common_name(name, existing_common_names)
        logger.info(f"Generated CommonName for {givenname} {surname}: '{common_name}'")

        dn = self._make_dn(common_name)
        employee_attributes = await self._get_employee_ldap_attributes(employee, dn)
        other_attributes = {"sAMAccountName": username}
        self.dataloader.add_ldap_object(dn, employee_attributes | other_attributes)
        return dn


class AlleroedUserNameGenerator(UserNameGeneratorBase):
    def generate_username(self, name, existing_usernames: list[str]):
        # Remove vowels from all but first name
        name = [name[0]] + [remove_vowels(n) for n in self._name_fixer(name)[1:]]

        return self._create_username(name, existing_usernames)

    async def generate_dn(self, employee: Employee) -> str:
        """
        Generates a LDAP DN (Distinguished Name) based on information from a MO Employee
        object.

        Also adds an object to LDAP with this DN

        Follows guidelines from https://redmine.magenta-aps.dk/issues/56080
        """
        existing_usernames, existing_common_names = self._get_existing_names()

        converter = self.user_context["converter"]
        sAMAccountName_it_users = await self.dataloader.load_all_it_users(
            converter.get_it_system_uuid("ADSAMA")
        )

        # "existing_usernames_in_mo" covers all usernames which MO has ever generated.
        # Because we never delete from MO's database; We just put end-dates on objects.
        #
        # We need to block these usernames from being generated, because it is possible
        # That MO generates a user, which is deleted from AD some years later. In that
        # Case we should never generate the username of the deleted user.
        # Ref: https://redmine.magenta-aps.dk/issues/57043
        existing_usernames_in_mo = [s["user_key"] for s in sAMAccountName_it_users]

        givenname = employee.givenname.strip()
        surname = employee.surname
        name = givenname.split(" ")[:4] + [surname]

        common_name = self._create_common_name(name, existing_common_names)
        logger.info(f"Generated CommonName for {givenname} {surname}: '{common_name}'")

        username = self.generate_username(
            name, existing_usernames + existing_usernames_in_mo
        )
        logger.info(f"Generated username for {givenname} {surname}: '{username}'")

        dn = self._make_dn(common_name)
        employee_attributes = await self._get_employee_ldap_attributes(employee, dn)
        other_attributes = {
            "sAMAccountName": username,
            "userPrincipalName": f"{username}@alleroed.dk",
        }

        self.dataloader.add_ldap_object(
            dn,
            employee_attributes | other_attributes,
        )

        return dn
