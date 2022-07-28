from datetime import date

from mora.graphapi.version import GraphQLVersion
import importlib
from pathlib import Path

VERSIONS_GETTERS = [
    importlib.import_module(f".{p.stem}.main", __package__).get_version
    for p in Path(__file__).parent.iterdir()
    if p.is_dir()
]


def get_versions(**kwargs) -> list[GraphQLVersion]:
    # TODO: skal verify at alle bortset fra nyeste har en deprecation time
    # TODO: lav en reduce der tjekker at der kun er en distance mellem to elementer og hvis der er så returner vi true. lav noget pairvise mapping tjek de er adjecent. tjek all. ja.
    # TODO: Alle versioner skal være forskellige lol
    # TODO: test at alle versionsDEPRECEATION_DATOERNE er kronologiske
    # TODO KUN EN MÅ VÆRE NONE
    print("LOL", VERSIONS_GETTERS)
    versions = (getter(**kwargs) for getter in VERSIONS_GETTERS)
    active_versions = (
        v
        for v in versions
        if v.deprecation_date is None or v.deprecation_date > date.today()
    )
    return list(sorted(active_versions, key=lambda v: v.version, reverse=True))
