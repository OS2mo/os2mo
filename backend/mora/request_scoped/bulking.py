# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import Lock
from contextlib import asynccontextmanager
from typing import Any, Dict, Iterable, Optional, Set, Tuple

from mora.common import get_connector
from mora.lora import Connector, LoraObjectType

LORA_OBJ = Dict[Any, Any]
UUID = str


class __BulkBookkeeper:
    """
    Singleton. Probably broken now without flask-features.
    Asyncio-concurrency safe via locks
    """

    def __init__(self):
        self.__locks: Dict[LoraObjectType, Lock] = {}
        self.__raw_cache = {}

    async def clear(self):
        """
        acquire all locks and clear cache

        :return:
        """
        try:
            for lock in self.__locks.values():
                await lock.acquire()

            self.__raw_cache.clear()
        finally:
            for lock in self.__locks.values():
                lock.release()

    def __get_lock(self, type_: LoraObjectType) -> Lock:
        """
        get a lock (and creates one if missing)
        :param type_:
        :return: Asyncio(!) lock, not process/thread-safe locks
        """
        # manually checking avoids creating unneeded Locks
        if type_ in self.__locks:
            return self.__locks[type_]
        return self.__locks.setdefault(type_, Lock())

    def _disable_caching(self):
        """
        NOT the ideal solution. Used to circumvent poor interaction with test suite.
        permanently patches necessary methods in the interface
        :return:
        """

        def get_conn(self):
            return get_connector()

        self.__class__.connector = property(get_conn)

        async def get_sinlge_non_cache(self, type_: LoraObjectType,
                                       uuid: str) -> Optional[LORA_OBJ]:
            return dict(
                await self.__raw_get_all(type_=type_, uuids={uuid})
            ).get(uuid, None)

        self.__class__.get_lora_object = get_sinlge_non_cache

    @property
    def __unprocessed_cache(self) -> Dict[LoraObjectType, Set[UUID]]:
        return self.__raw_cache.setdefault(self.__class__.__name__, {})

    @property
    def __processed_cache(self) -> Dict[LoraObjectType, Dict[UUID, Optional[LORA_OBJ]]]:
        return self.__raw_cache.setdefault(self.__class__.__name__ + '_processed', {})

    async def __raw_get_all(self, type_: LoraObjectType,
                            uuids: Set[str]) -> Iterable[Tuple[UUID, LORA_OBJ]]:
        """
        get without all the caching.
        NOTE: Passing a uuid to this DOES NOT guarantee it to also be in the result.
        :param type_: determines the LoRa endpoint

        :param uuids:
        :return:
        """
        get_all_results = await self.connector.scope(type_).get_all_by_uuid(uuids)
        return get_all_results

    async def __bulk_get(self, type_: LoraObjectType):
        """
        Should be called as rarely as possible. Will bulk fetch from LoRa.
        :param type_: determines the LoRa endpoint
        :return:
        """
        uuids = self.__unprocessed_cache.get(type_, False)
        if uuids:
            all_results = list(await self.__raw_get_all(type_=type_, uuids=uuids))
            self.__processed_cache.setdefault(type_, {}).update(all_results)

            # things that don't exists in the DB yields no response, so fill with None
            type_cache = self.__processed_cache[type_]
            for uuid in uuids:
                if uuid not in type_cache:
                    type_cache[uuid] = None
            # clear unprocessed, as we've moved everything into the processed cache
            self.__unprocessed_cache[type_].clear()

    def __add(self, type_: LoraObjectType, uuid: str):
        """
         adds an uuid to the cache

         :param type_: type of object the uuid refers
         :param uuid:
         :return:
         """
        # if already processed, skip
        if uuid in self.__processed_cache.setdefault(type_, {}):
            return

        # add to unprocessed
        self.__unprocessed_cache.setdefault(type_, set()).add(uuid)

    @property
    def connector(self) -> Connector:
        """
        get used / 'current' connector
        :return:
        """
        key = self.__class__.__name__ + '_connector'
        # manually checking avoids creating unneeded connectors
        if key in self.__raw_cache:
            return self.__raw_cache.get(key)

        # set and return
        return self.__raw_cache.setdefault(key, get_connector())

    async def add(self, type_: LoraObjectType, uuid: str):
        """
        adds an uuid to the cache, concurrency-safe

        :param type_: type of object the uuid refers
        :param uuid:
        :return:
        """
        async with self.__get_lock(type_):
            self.__add(type_=type_, uuid=uuid)

    async def get_lora_object(self, type_: LoraObjectType, uuid: str) -> LORA_OBJ:
        """
        Get a LoRa object. Utilize cache if possible. Concurrency-safe
        :param type_: type of object the uuid refers
        :param uuid:
        :return: The (possibly cached) object from LoRa
        """

        async with self.__get_lock(type_):
            # if uuid processed, return obj
            try:
                return self.__processed_cache[type_][uuid]
            except KeyError:
                pass

            # if not unprocessed, get add it unprocessed
            if uuid not in self.__unprocessed_cache.setdefault(type_, set()):
                self.__add(type_=type_, uuid=uuid)

            # bulk process
            await self.__bulk_get(type_)

            # HAVE to exist now, otherwise legit error
            return self.__processed_cache[type_][uuid]

    @asynccontextmanager
    async def cache_context(self):
        try:
            yield None
        finally:
            await self.clear()


# I'm a singleton
request_wide_bulk = __BulkBookkeeper()
