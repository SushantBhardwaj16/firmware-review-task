"""Two small tools for looking inside a file, so nothing else needs installing."""

import re


def strings(path: str, minimum: int = 4) -> list[tuple[int, str]]:
    """Return (byte offset, text) for every run of printable ASCII of at least minimum characters."""
    with open(path, "rb") as handle:
        data = handle.read()
    runs = re.finditer(rb"[\x20-\x7e]{%d,}" % max(1, minimum), data)
    return [(run.start(), run[0].decode("ascii")) for run in runs]


def elfinfo(path: str) -> dict:
    """Return the class (32 or 64), the endian (little or big) and the machine number of an ELF file."""
    with open(path, "rb") as handle:
        header = handle.read(20)
    if len(header) < 20 or header[:4] != b"\x7fELF" or header[4] not in (1, 2) or header[5] not in (1, 2):
        raise ValueError(f"{path}: not an ELF file, or its header is damaged")
    endian = "little" if header[5] == 1 else "big"
    return {
        "class": 32 if header[4] == 1 else 64,
        "endian": endian,
        "machine": int.from_bytes(header[18:20], endian),
    }
