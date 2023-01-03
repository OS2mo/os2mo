from typing import Union

import structlog
from fastramqpi.context import Context
from ramodels.mo.employee import Employee

from .exceptions import IncorrectMapping
from .ldap import paged_search


class UserNameGeneratorBase:
    """
    Class with functions to generate valid LDAP usernames.

    Each customer could have his own username generator function in here. All you need
    to do, is refer to the proper function inside the json dict.
    """

    def __init__(self, context: Context):

        self.logger = structlog.get_logger()

        self.context = context
        self.user_context = context["user_context"]
        self.settings = self.user_context["settings"]

        self.mapping = self.user_context["mapping"]
        self.check_json_inputs()

        self.json_inputs = self.mapping["username_generator"]
        self.char_replacement = self.json_inputs["char_replacement"]
        self.forbidden_usernames = [
            u.lower() for u in self.json_inputs["forbidden_usernames"]
        ]
        self.combinations = self.json_inputs["combinations_to_try"]

    def _check_key(self, key):
        if key not in self.mapping["username_generator"].keys():
            raise IncorrectMapping(
                f"'{key}' key not present in mapping['username_generator']"
            )

    def _check_type(self, key, type_to_check):
        object_to_check = self.mapping["username_generator"][key]
        if type(object_to_check) is not type_to_check:
            raise IncorrectMapping(f"{key} entry must be a {type_to_check}")
        else:
            return object_to_check

    def _check_char_replacement(self):
        self._check_key("char_replacement")
        self._check_type("char_replacement", dict)

    def _check_forbidden_usernames(self):
        self._check_key("forbidden_usernames")
        forbidden_usernames = self._check_type("forbidden_usernames", list)

        for username in forbidden_usernames:
            if type(username) is not str:
                raise IncorrectMapping(
                    (
                        f"Incorrect username in 'forbidden_usernames':{username}. "
                        "Username must be a string"
                    )
                )

    def _check_combinations_to_try(self):
        self._check_key("combinations_to_try")
        combinations = self._check_type("combinations_to_try", list)

        accepted_characters = ["F", "L", "1", "2", "3", "X"]
        for combination in combinations:
            if not all([c in accepted_characters for c in combination]):
                raise IncorrectMapping(
                    (
                        f"Incorrect combination found: '{combination}' username "
                        "combinations can only contain {accepted_characters}"
                    )
                )

    def check_json_inputs(self):

        if "username_generator" not in self.mapping.keys():
            raise IncorrectMapping("'username_generator' key not present in mapping")
        self._check_char_replacement()
        self._check_forbidden_usernames()
        self._check_combinations_to_try()

    def _get_existing_usernames(self):
        user_class = self.user_context["mapping"]["mo_to_ldap"]["Employee"][
            "objectClass"
        ]
        searchParameters = {
            "search_filter": f"(objectclass={user_class})",
            "attributes": ["cn"],
        }
        existing_usernames = [
            entry["attributes"]["cn"].lower()
            for entry in paged_search(self.context, searchParameters)
        ]
        return existing_usernames

    def _get_ou(self):
        """
        Return LDAPs OU (Organizational Unit)
        """
        return self.settings.ldap_organizational_unit

    def _get_dc(self):
        """
        Return LDAPs DC (Domain Component)
        """
        return self.settings.ldap_search_base  # Domain Component

    def _make_cn(self, username_string):

        return f"CN={username_string}"

    def _make_dn(self, username_string):

        cn = self._make_cn(username_string)
        ou = self._get_ou()
        dc = self._get_dc()
        dn = ",".join([cn, ou, dc])  # Distinguished Name
        return dn

    def _name_fixer(self, name: list) -> list:
        """
        Inspired by ad_integration/usernames.py
        """
        for i in range(0, len(name)):
            # Replace according to replacement list
            for char, replacement in self.char_replacement.items():
                name[i] = name[i].replace(char, replacement)

            # Remove all remaining characters outside a-z
            for char in name[i].lower():
                if ord(char) not in range(ord("a"), ord("z") + 1):
                    name[i] = name[i].replace(char, "")

        return name

    def _machine_readable_combi(self, combi):
        """
        Inspired by ad_integration/usernames.py
        """
        readable_combi = []
        max_position = -1
        position: Union[int, None]
        for i in range(0, len(combi)):
            # First name
            if combi[i] == "F":
                position = 0
            # First middle name
            if combi[i] == "1":
                position = 1
            # Second middle name
            if combi[i] == "2":
                position = 2
            # Third middle name
            if combi[i] == "3":
                position = 3
            # Last name (independent of middle names)
            if combi[i] == "L":
                position = -1
            if combi[i] == "X":
                position = None
            if position is not None and position > max_position:
                max_position = position
            readable_combi.append(position)
        return (readable_combi, max_position)

    def _create_from_combi(self, name, combi):
        """
        Create a username from a name and a combination.

        Inspired by ad_integration/usernames.py
        """
        (code, max_position) = self._machine_readable_combi(combi)

        # Do not use codes that uses more names than the actual person has
        if max_position > len(name) - 2:
            return None

        # First letter is always first letter of first position
        if code[0] is not None:
            relevant_name = code[0]
            username = name[relevant_name][0].lower()
        else:
            username = "X"

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
                username += "X"
        return username

    def _create_username(self, name: list) -> str:
        """
        Create a new username in accodance with the rules specified in this file.
        The username will be the highest quality available and the value will be
        added to list of used names, so consequtive calles with the same name
        will keep returning new names until the algorithm runs out of options
        and a RuntimeException is raised.

        :param name: Name of the user given as a list with at least two elements.
        :return: New username generated.

        Inspired by ad_integration/usernames.py
        """
        name = self._name_fixer(name)
        existing_usernames = self._get_existing_usernames()

        for permutation_counter in range(2, 10):
            i = 0
            for combi in self.combinations:
                i = i + 1
                username = self._create_from_combi(name, combi)
                if not username:
                    continue
                final_username: str = username.replace("X", str(permutation_counter))
                if final_username not in existing_usernames:
                    if username.replace("X", "") not in self.forbidden_usernames:
                        return final_username

        # If we get to here, we completely failed to make a username
        raise RuntimeError("Failed to create user name.")


class UserNameGenerator(UserNameGeneratorBase):
    def generate_dn(self, employee: Employee):
        """
        Generates a LDAP DN (Distinguished Name) based on information from a MO Employee
        object
        """
        givenname = employee.givenname
        surname = employee.surname

        name = givenname.split(" ")[:4] + [surname]
        username = self._create_username(name)

        self.logger.info(f"Generated username for {givenname} {surname}: '{username}'")

        return self._make_dn(username)
