import re
from copy import deepcopy
from typing import Union

from fastramqpi.context import Context
from ramodels.mo.employee import Employee

from .exceptions import IncorrectMapping
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
        self.check_json_inputs()

        self.json_inputs = self.mapping["username_generator"]
        self.char_replacement = self.json_inputs["char_replacement"]
        self.forbidden_usernames = [
            u.lower() for u in self.json_inputs["forbidden_usernames"]
        ]
        self.combinations = self.json_inputs["combinations_to_try"]

        self.dataloader = self.user_context["dataloader"]

    def _check_key(self, key):
        if key not in self.mapping["username_generator"]:
            raise IncorrectMapping(
                f"'{key}' key not present in mapping['username_generator']"
            )

    def _check_type(self, key, type_to_check):
        object_to_check = self.mapping["username_generator"][key]
        if type(object_to_check) is not type_to_check:
            raise IncorrectMapping(f"{key} entry must be a {type_to_check}")
        else:
            return object_to_check

    def _check_key_and_type(self, key, type_to_check):
        self._check_key(key)
        return self._check_type(key, type_to_check)

    def _check_char_replacement(self):
        self._check_key_and_type("char_replacement", dict)

    def _check_forbidden_usernames(self):
        forbidden_usernames = self._check_key_and_type("forbidden_usernames", list)

        for username in forbidden_usernames:
            if type(username) is not str:
                raise IncorrectMapping(
                    (
                        f"Incorrect username in 'forbidden_usernames':{username}. "
                        "Username must be a string"
                    )
                )

    def _check_combinations_to_try(self):
        combinations = self._check_key_and_type("combinations_to_try", list)

        accepted_characters = ["F", "L", "1", "2", "3", "X"]
        for combination in combinations:
            if not all([c in accepted_characters for c in combination]):
                raise IncorrectMapping(
                    (
                        f"Incorrect combination found: '{combination}' username "
                        f"combinations can only contain {accepted_characters}"
                    )
                )

    def check_json_inputs(self):

        if "username_generator" not in self.mapping:
            raise IncorrectMapping("'username_generator' key not present in mapping")
        self._check_char_replacement()
        self._check_forbidden_usernames()
        self._check_combinations_to_try()

    def get_existing_values(self, attribute):
        user_class = self.user_context["mapping"]["mo_to_ldap"]["Employee"][
            "objectClass"
        ]
        searchParameters = {
            "search_filter": f"(objectclass={user_class})",
            "attributes": [attribute],
        }
        search_base = self.settings.ldap_search_base
        existing_values = [
            entry["attributes"][attribute].lower()
            for entry in paged_search(self.context, searchParameters, search_base)
        ]
        return existing_values

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

    def _name_fixer(self, name_to_fix: list[str]) -> list[str]:
        """
        Inspired by ad_integration/usernames.py
        """
        name = deepcopy(name_to_fix)
        for i in range(0, len(name)):
            # Replace according to replacement list
            for char, replacement in self.char_replacement.items():
                name[i] = name[i].replace(char, replacement)

            # Remove all remaining characters outside a-z
            name[i] = re.sub(r"[^a-z]+", "", name[i].lower())

        return name

    def _machine_readable_combi(self, combi: str):
        """
        Inspired by ad_integration/usernames.py
        """
        readable_combi = []
        max_position = -1
        position: Union[int, None]
        for character in combi:
            # First name
            if character == "F":
                position = 0
            # First middle name
            if character == "1":
                position = 1
            # Second middle name
            if character == "2":
                position = 2
            # Third middle name
            if character == "3":
                position = 3
            # Last name (independent of middle names)
            if character == "L":
                position = -1
            if character == "X":
                position = None
            if position is not None and position > max_position:
                max_position = position
            readable_combi.append(position)
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

    def _create_username(self, name: list) -> str:
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
        existing_usernames = self.get_existing_values("sAMAccountName")

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

    def _create_common_name(self, name: list) -> str:
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
        existing_common_names = self.get_existing_values("cn")
        while common_name.lower() in existing_common_names:
            common_name = (
                common_name.replace(f"_{permutation_counter-1}", "")
                + f"_{permutation_counter}"
            )
            permutation_counter += 1

            if permutation_counter >= 1000:
                raise RuntimeError("Failed to create common name")

        return common_name

    def _get_employee_ldap_attributes(self, employee: Employee, dn: str):
        converter = self.user_context["converter"]
        employee_ldap = converter.to_ldap({"mo_employee": employee}, "Employee", dn)
        attributes = employee_ldap.dict()
        attributes.pop("dn")

        return attributes


class UserNameGenerator(UserNameGeneratorBase):
    def generate_dn(self, employee: Employee) -> str:
        """
        Generates a LDAP DN (Distinguished Name) based on information from a MO Employee
        object.

        Also adds an object to LDAP with this DN
        """
        givenname = employee.givenname
        surname = employee.surname
        name = givenname.split(" ")[:4] + [surname]

        username = self._create_username(name)
        logger.info(f"Generated username for {givenname} {surname}: '{username}'")

        common_name = self._create_common_name(name)
        logger.info(f"Generated CommonName for {givenname} {surname}: '{common_name}'")

        dn = self._make_dn(common_name)
        employee_attributes = self._get_employee_ldap_attributes(employee, dn)
        other_attributes = {"sAMAccountName": username}
        self.dataloader.add_ldap_object(dn, employee_attributes | other_attributes)
        return dn


class AlleroedUserNameGenerator(UserNameGeneratorBase):
    def generate_username(self, name):
        # Remove vowels from all but first name
        name = [name[0]] + [remove_vowels(n) for n in self._name_fixer(name)[1:]]

        return self._create_username(name)

    def generate_dn(self, employee: Employee) -> str:
        """
        Generates a LDAP DN (Distinguished Name) based on information from a MO Employee
        object.

        Also adds an object to LDAP with this DN

        Follows guidelines from https://redmine.magenta-aps.dk/issues/56080
        """
        givenname = employee.givenname.strip()
        surname = employee.surname
        name = givenname.split(" ")[:4] + [surname]

        common_name = self._create_common_name(name)
        logger.info(f"Generated CommonName for {givenname} {surname}: '{common_name}'")

        username = self.generate_username(name)
        logger.info(f"Generated username for {givenname} {surname}: '{username}'")

        dn = self._make_dn(common_name)
        employee_attributes = self._get_employee_ldap_attributes(employee, dn)
        other_attributes = {
            "sAMAccountName": username,
            "userPrincipalName": f"{username}@alleroed.dk",
        }

        self.dataloader.add_ldap_object(
            dn,
            employee_attributes | other_attributes,
        )

        return dn
