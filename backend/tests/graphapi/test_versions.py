from mora.graphapi.main import versions


def test_todo():
    # TODO: Alle versioner skal være forskellige lol
    version_numbers = [v.version for v in versions]
    assert set(version_numbers) == list(version_numbers)
    assert False


# TODO: skal verify at alle bortset fra nyeste har en deprecation time
# TODO: lav en reduce der tjekker at der kun er en distance mellem to elementer og hvis der er så returner vi true. lav noget pairvise mapping tjek de er adjecent. tjek all. ja.
# TODO: test at alle versionsDEPRECEATION_DATOERNE er kronologiske
# TODO: Test at versioner stopper med at virke når deprecation_date overskrides (freezegun?)
