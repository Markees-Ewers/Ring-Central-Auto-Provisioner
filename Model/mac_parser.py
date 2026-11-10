"""MAC-address parsing and validation helpers.

Author: Markees Ewers
Responsibility: Normalize MAC addresses and apply optional camera-scan prefixes.
"""

from __future__ import annotations

import re

MAC_VALUE_PATTERN = re.compile(r"^[0-9A-Fa-f]{12}$")
FORMATTED_MAC_PATTERN = re.compile(
    r"^(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$"
)
MAC_PREFIX_PATTERN = re.compile(r"^[0-9A-Fa-f]{6}$")


def parse_mac(value: str) -> str | None:
    """Return a normalized colon-separated MAC, or None for non-MAC input."""
    compact = value.strip().replace(":", "").replace("-", "")
    if not MAC_VALUE_PATTERN.fullmatch(compact):
        return None
    return ":".join(compact[index : index + 2] for index in range(0, 12, 2)).upper()


def is_mac(value: str) -> bool:
    """Return whether value is a supported compact or formatted MAC."""
    return parse_mac(value) is not None


def parse_mac_prefix(value: str) -> str | None:
    """Return a normalized six-hex-digit MAC prefix, or None if invalid."""
    compact = value.strip().replace(":", "").replace("-", "")
    if not MAC_PREFIX_PATTERN.fullmatch(compact):
        return None
    return compact.upper()


def apply_mac_prefix(mac_address: str, prefix: str | None) -> str | None:
    """Replace the first three MAC octets with a validated prefix."""
    mac = parse_mac(mac_address)
    if mac is None:
        return None
    normalized_prefix = parse_mac_prefix(prefix) if prefix else None
    if prefix and normalized_prefix is None:
        return None
    return parse_mac((normalized_prefix or mac.replace(":", "")[:6]) + mac.replace(":", "")[6:])
