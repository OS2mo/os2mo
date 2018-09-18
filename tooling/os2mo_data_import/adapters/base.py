# -- coding: utf-8 --

from uuid import uuid4


class MoxUtility:

    def create_uuid(self):
        """
        Generates a UUID (version 4)
        Helper function

        :return:    UUID
        :rtype:     str
        """

        identifier = uuid4()
        return str(identifier)

    def validity_range(self, from_date, to_date):
        if not from_date:
            from_date = "1900-01-01"

        if not to_date:
            to_date = "infinity"

        return {
            "from": from_date,
            "to": to_date
        }


class MemoryMap(MoxUtility):
    """
    In memory store
    """

    parent_org = None
    storage_map = {}

    def set_parent_org(self, parent_org):
        self.parent_org = parent_org

    def get_uuid(self, identifier):
        """
        Get UUID by identifier

        :param identifier:  User defined identifier

        :return:            UUID
        """
        item = self.storage_map[identifier]
        return item["uuid"]

    def get_data(self, identifier):
        """
        Get data by identifier

        :param identifier:  User defined identifier

        :return:            Data set as stored
        """
        item = self.storage_map[identifier]
        return item["data"]

    def get_available(self):
        """
        Show available identifiers/uuids

        :return:
        """
        return {
            key: val["uuid"]
            for key, val in self.storage_map.items()
        }

    def save(self, identifier, data):
        """
        Save data type in memory only

        :param identifier:  User defined identifier
        :param data:        Data payload (Type: dict)
        :return:            Created UUID
        """

        if not isinstance(data, dict):
            raise TypeError("Data must be of type dict")

        # Use existing uuid when overwriting
        if identifier in self.storage_map:
            import_uuid = self.get_uuid(identifier)
        else:
            import_uuid = self.create_uuid()

        self.storage_map[identifier] = {
            "uuid": import_uuid,
            "data": data,
            "metadata": []
        }

        return import_uuid

    def db_export(self):
        """
        Export list of tuples containing UUID and data
        Example:

            ("77b49f9b-166e-4c07-8a47-598b99cdee04", { <payload> })

        :return:    Database payload
        :rtype:     tuple
        """

        return [
            (item["uuid"], item["data"])
            for item in self.storage_map.values()
        ]
