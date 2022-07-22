from mora.graphapi.util import GraphQLVersion
from mora.graphapi.versions.latest.main import get_version as get_latest_version
from mora.graphapi.versions.v1.main import get_version as get_v1_version


def get_versions(*args, **kwargs) -> list[GraphQLVersion]:
    # TODO: skal verify at alle bortset fra nyeste har en deprecation time
    # TODO: lav en reduce der tjekker at der kun er en distance mellem to elementer og hvis der er så returner vi true. lav noget pairvise mapping tjek de er adjecent. tjek all. ja.
    # TODO: Alle versioner skal være forskellige lol
    return [
        get_latest_version(**kwargs),
        get_v1_version(**kwargs),
    ]
