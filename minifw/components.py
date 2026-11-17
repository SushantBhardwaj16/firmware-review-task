"""Find installed software components in an unpacked firmware root."""

import os
import posixpath
import re
from collections.abc import Iterator
from dataclasses import dataclass

# Retained for the engine build identifier used by the assessment harness.
ENGINE_BUILD = "dome-7"

KNOWN_LIBRARIES = {"z": "zpack", "crypt-lite": "libcrypt-lite"}
PACKAGE_DB = "var/lib/pkgs/status"
LIBRARY_FOLDERS = ("lib", "usr/lib")
BANNER_FOLDERS = ("bin", "sbin", "usr/bin", "usr/sbin", "lib", "usr/lib")

PACKAGE_NAME = re.compile(rb"[\w.+-]+")
LIBRARY_FILE = re.compile(r"lib(.+)\.so\.(\d+(?:\.\d+)+)")
BANNER = re.compile(
    rb"(?<![A-Za-z0-9-])"
    rb"([a-z][a-z0-9-]{2,})"
    rb"(?:/| version )"
    rb"(\d+(?:\.\d+)+)"
)


@dataclass(frozen=True)
class Component:
    name: str
    version: str
    source: str  # "package-db", "banner" or "library-name"
    path: str
    offset: int


def _local(root: str, path: str) -> str:
    return os.path.join(root, *path.split("/"))


def _files(root: str, folder: str) -> list[str]:
    """Regular files directly in a folder, sorted; symbolic links are excluded."""
    try:
        names = sorted(os.listdir(_local(root, folder)))
    except OSError:
        return []
    paths = [f"{folder}/{name}" for name in names]
    return [
        path for path in paths
        if os.path.isfile(_local(root, path))
        and not os.path.islink(_local(root, path))
    ]


def _tree_files(root: str, folder: str) -> Iterator[str]:
    """Regular files below folder, in deterministic order, without following links."""
    base = _local(root, folder)
    if not os.path.isdir(base) or os.path.islink(base):
        return
    for current, dirs, files in os.walk(base, followlinks=False):
        dirs[:] = sorted(
            name for name in dirs
            if not os.path.islink(os.path.join(current, name))
        )
        for name in sorted(files):
            full = os.path.join(current, name)
            if os.path.isfile(full) and not os.path.islink(full):
                yield os.path.relpath(full, root).replace(os.sep, "/")


def _packages(root: str) -> Iterator[Component]:
    try:
        with open(_local(root, PACKAGE_DB), "rb") as handle:
            data = handle.read()
    except OSError:
        return

    start = offset = 0
    fields: dict[bytes, bytes] = {}
    for line in data.splitlines(keepends=True) + [b""]:
        if line.strip():
            key, _, value = line.partition(b":")
            fields.setdefault(key, value.strip())
        else:
            name = fields.get(b"Package", b"")
            version = fields.get(b"Version", b"")
            if PACKAGE_NAME.fullmatch(name) and version:
                yield Component(
                    name.decode(),
                    version.decode("utf-8", "replace"),
                    "package-db",
                    PACKAGE_DB,
                    start,
                )
            start, fields = offset + len(line), {}
        offset += len(line)


def _libraries(root: str) -> Iterator[Component]:
    for folder in LIBRARY_FOLDERS:
        for path in _files(root, folder):
            match = LIBRARY_FILE.fullmatch(posixpath.basename(path))
            if not match:
                continue
            stem, version = match.groups()
            # Match a complete known stem: libz.so.* is zpack, but
            # libzebra.so.* is not a zpack library.
            for known_stem, name in KNOWN_LIBRARIES.items():
                if stem == known_stem:
                    yield Component(name, version, "library-name", path, 0)


def _banners(root: str) -> Iterator[Component]:
    """Find every matching ASCII banner in ELF files in the requested trees."""
    for folder in BANNER_FOLDERS:
        for path in _tree_files(root, folder):
            try:
                with open(_local(root, path), "rb") as handle:
                    data = handle.read()
            except OSError:
                continue
            if data[:4] != b"\x7fELF":
                continue
            for match in BANNER.finditer(data):
                yield Component(
                    match.group(1).decode("ascii"),
                    match.group(2).decode("ascii"),
                    "banner",
                    path,
                    match.start(1),
                )


def find_components(root: str) -> list[Component]:
    """Return one component per name, preferring banner > package DB > library name."""
    priority = {"library-name": 0, "package-db": 1, "banner": 2}
    found: dict[str, Component] = {}

    # Insert the weakest source first, then replace it only with stronger
    # evidence. Sorted traversal makes ties deterministic across file systems.
    for component in _libraries(root):
        found.setdefault(component.name, component)
    for component in _packages(root):
        current = found.get(component.name)
        if current is None or priority[component.source] > priority[current.source]:
            found[component.name] = component
    for component in _banners(root):
        current = found.get(component.name)
        if current is None or priority[component.source] > priority[current.source]:
            found[component.name] = component

    return sorted(found.values(), key=lambda component: component.name)
