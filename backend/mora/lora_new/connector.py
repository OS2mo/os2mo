from .helpers import validity_tuple
from mora import config
from mora import exceptions
from mora import util


class Connector:
    def __init__(self, **defaults):
        self.__validity = defaults.pop("validity", None) or "present"

        self.now = util.parsedatetime(
            defaults.pop("effective_date", None) or util.now(),
        )

        if self.__validity == "present":
            # we should probably use 'virkningstid' but that means we
            # have to override each and every single invocation of the
            # accessors later on
            if "virkningfra" in defaults:
                self.now = util.parsedatetime(defaults.pop("virkningfra"))

        try:
            self.start, self.end = validity_tuple(self.__validity, now=self.now)
        except TypeError:
            exceptions.ErrorCodes.V_INVALID_VALIDITY(validity=self.__validity)

        if self.__validity == "present" and "virkningtil" in defaults:
            self.end = util.parsedatetime(defaults.pop("virkningtil"))

        defaults.update(
            virkningfra=util.to_lora_time(self.start),
            virkningtil=util.to_lora_time(self.end),
        )
        if config.get_settings().consolidate:
            # LoRa does not check the value of the 'konsolider' paramter, but the mere
            # existence of the _key_. For this reason, the value CANNOT be set to
            # False, it must instead be absent from the dict.
            defaults.update(
                konsolider=True,
            )

        self.__defaults = defaults
        self.__scopes = {}

    @property
    def defaults(self):
        return self.__defaults

    @property
    def validity(self):
        return self.__validity

    def is_range_relevant(self, start, end, effect):
        if self.validity == "present":
            return util.do_ranges_overlap(self.start, self.end, start, end)
        return start > self.start and end <= self.end

    def scope(self, type_: LoraObjectType) -> "Scope":
        if type_ in self.__scopes:
            return self.__scopes[type_]
        return self.__scopes.setdefault(type_, Scope(self, type_.value))

    @property
    def organisation(self) -> "Scope":
        return self.scope(LoraObjectType.org)

    @property
    def organisationenhed(self) -> "Scope":
        return self.scope(LoraObjectType.org_unit)

    @property
    def organisationfunktion(self) -> "Scope":
        return self.scope(LoraObjectType.org_func)

    @property
    def bruger(self) -> "Scope":
        return self.scope(LoraObjectType.user)

    @property
    def itsystem(self) -> "Scope":
        return self.scope(LoraObjectType.it_system)

    @property
    def klasse(self) -> "Scope":
        return self.scope(LoraObjectType.class_)

    @property
    def facet(self) -> "Scope":
        return self.scope(LoraObjectType.facet)
