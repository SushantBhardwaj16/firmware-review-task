"""Load advisories and match them against the components of an image.

The advisories file is a JSON list of objects such as:

    {"id": "DVS-2026-0000", "component": "exampled", "introduced": "1.2.0",
     "fixed": "1.4.3", "severity": "high"}

A component is affected when introduced <= version < fixed. A null
"introduced" means from the first release; a null "fixed" means every later
release. Versions compare as dotted integers, so 1.10 is later than 1.9 and
1.2 equals 1.2.0. Other keys in an advisory are kept and not used here.
"""

import json
import re


def _parse(version) -> tuple[int, ...] | None:
    """A dotted-integer version as a tuple without trailing zeros, or None for anything else."""
    if not isinstance(version, str) or not re.fullmatch(r"\d+(\.\d+)*", version):
        return None
    groups = [int(group) for group in version.split(".")]
    while groups and groups[-1] == 0:
        groups.pop()
    return tuple(groups)


def load(path: str) -> list[dict]:
    """Read and check an advisories file."""
    with open(path, encoding="utf-8") as handle:
        advisories = json.load(handle)
    if not isinstance(advisories, list):
        raise ValueError(f"{path}: expected a JSON list of advisories")
    for advisory in advisories:
        if not isinstance(advisory, dict) or not all(
            isinstance(advisory.get(key), str) for key in ("id", "component", "severity")
        ):
            raise ValueError(f"{path}: an advisory needs the text fields id, component and severity")
        for key in ("introduced", "fixed"):
            if advisory.get(key) is not None and _parse(advisory[key]) is None:
                raise ValueError(f"{path}: {advisory['id']}: {key} is not a dotted-integer version")
    return advisories


def match(components, advisories: list[dict]) -> list[dict]:
    """Return one row per component and advisory that affects it, sorted by component, then advisory."""
    affected = []
    for component in components:
        version = _parse(component.version)
        if version is None:
            continue
        for advisory in advisories:
            if advisory["component"].lower() != component.name.lower():
                continue
            introduced, fixed = advisory.get("introduced"), advisory.get("fixed")
            if (introduced is None or _parse(introduced) <= version) and (fixed is None or version < _parse(fixed)):
                affected.append({
                    "advisory": advisory["id"],
                    "component": component.name,
                    "version": component.version,
                    "severity": advisory["severity"],
                })
    return sorted(affected, key=lambda row: (row["component"], row["advisory"]))
