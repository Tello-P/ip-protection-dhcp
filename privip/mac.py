"""Generar y validar direcciones MAC. Sin dependencias de GUI ni de sistema."""
import random
import re

_MAC_RE = re.compile(r"^[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}$")

LOCAL_BIT = 0x02      # locally administered
MULTICAST_BIT = 0x01  # group address


def is_valid_mac(mac):
    """True si `mac` es XX:XX:XX:XX:XX:XX (o con guiones), sin mezclar separadores."""
    return isinstance(mac, str) and _MAC_RE.match(mac) is not None


def normalize_mac(mac):
    """Devuelve la MAC en mayúsculas y con ':'. Lanza ValueError si no es válida."""
    if not is_valid_mac(mac):
        raise ValueError(f"MAC inválida: {mac!r}")
    return mac.replace("-", ":").upper()


def _first_octet(mac):
    return int(normalize_mac(mac)[:2], 16)


def is_unicast(mac):
    return not _first_octet(mac) & MULTICAST_BIT


def is_locally_administered(mac):
    return bool(_first_octet(mac) & LOCAL_BIT)


def generate_mac(rng=random):
    """MAC aleatoria igual que el motor C: bit local puesto, multicast limpio.

    `rng` es inyectable (cualquier objeto con `getrandbits`) para tests.
    """
    octets = [rng.getrandbits(8) for _ in range(6)]
    octets[0] = (octets[0] & 0xFC) | LOCAL_BIT
    return ":".join(f"{o:02X}" for o in octets)
