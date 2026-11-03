import random

import pytest

from privip.mac import (generate_mac, is_locally_administered, is_unicast,
                        is_valid_mac, normalize_mac)


@pytest.mark.parametrize("mac", [
    "00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF", "aa:bb:cc:dd:ee:ff", "aa-bb-cc-dd-ee-ff",
])
def test_valid(mac):
    assert is_valid_mac(mac)


@pytest.mark.parametrize("mac", [
    "", "00:11:22:33:44", "00:11:22:33:44:55:66", "GG:11:22:33:44:55",
    "00:11:22:33:44:5", "001122334455", "00:11-22:33-44:55", None, 123,
])
def test_invalid(mac):
    assert not is_valid_mac(mac)


def test_normalize():
    assert normalize_mac("aa-bb-cc-dd-ee-ff") == "AA:BB:CC:DD:EE:FF"


def test_normalize_invalid():
    with pytest.raises(ValueError):
        normalize_mac("nope")


def test_flags():
    assert is_unicast("02:00:00:00:00:00")
    assert not is_unicast("01:00:00:00:00:00")
    assert is_locally_administered("02:00:00:00:00:00")
    assert not is_locally_administered("00:00:00:00:00:00")


def test_generate_always_valid_unicast_local():
    rng = random.Random(1234)
    for _ in range(500):
        mac = generate_mac(rng)
        assert is_valid_mac(mac)
        assert is_unicast(mac)
        assert is_locally_administered(mac)


def test_generate_forces_bits_on_worst_case():
    class AllOnes:
        def getrandbits(self, n):
            return 0xFF
    assert generate_mac(AllOnes()) == "FE:FF:FF:FF:FF:FF"


def test_generate_varies():
    rng = random.Random(1)
    assert len({generate_mac(rng) for _ in range(50)}) == 50
