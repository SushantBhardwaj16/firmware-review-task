"""Find the software components in an unpacked firmware root.

Components come from the package database, var/lib/pkgs/status, and from the
file names of well-known shared libraries in lib and usr/lib.
"""

import os
import posixpath
import re
from collections.abc import Iterator
from dataclasses import dataclass

KNOWN_LIBRARIES = {"z": "zpack", "crypt-lite": "libcrypt-lite"}
PACKAGE_DB = "var/lib/pkgs/status"
DOCUMENTS = "usr/share/doc"
LIBRARY_FOLDERS = ("lib", "usr/lib")

PACKAGE_NAME = re.compile(rb"[\w.+-]+")
LIBRARY_FILE = re.compile(r"lib(.+)\.so\.(\d+(?:\.\d+)+)")


@dataclass(frozen=True)
class Component:
    name: str
    version: str
    source: str  # "package-db", "document" or "library-name"
    path: str  # the file that is the evidence, from the root, with forward slashes
    offset: int  # the byte offset of the evidence in that file


def _local(root: str, path: str) -> str:
    return os.path.join(root, *path.split("/"))


def _files(root: str, folder: str) -> list[str]:
    """The regular files directly in a folder, in sorted order. Links are not followed."""
    try:
        names = sorted(os.listdir(_local(root, folder)))
    except OSError:
        return []
    paths = [f"{folder}/{name}" for name in names]
    return [path for path in paths if os.path.isfile(_local(root, path)) and not os.path.islink(_local(root, path))]


def _packages(root: str) -> Iterator[Component]:
    try:
        with open(_local(root, PACKAGE_DB), "rb") as handle:
            data = handle.read()
    except OSError:
        return
    start = offset = 0
    fields: dict[bytes, bytes] = {}
    for line in data.splitlines(keepends=True) + [b""]:  # the empty last line closes the last block
        if line.strip():
            key, _, value = line.partition(b":")
            fields.setdefault(key, value.strip())
        else:
            name, version = fields.get(b"Package", b""), fields.get(b"Version", b"")
            if PACKAGE_NAME.fullmatch(name) and version:
                yield Component(name.decode(), version.decode("utf-8", "replace"), "package-db", PACKAGE_DB, start)
            start, fields = offset + len(line), {}
        offset += len(line)


def _documented(root: str, package: Component) -> Component:
    """The package with the version its own notes give, when they give one."""
    stated = re.compile(re.escape(package.name.encode()) + rb" (\d+(?:\.\d+)+)")
    for path in _files(root, f"{DOCUMENTS}/{package.name}"):
        with open(_local(root, path), "rb") as handle:
            version = stated.search(handle.read())
        if version:
            return Component(package.name, version[1].decode(), "document", path, version.start())
    return package


def _libraries(root: str) -> Iterator[Component]:
    for folder in LIBRARY_FOLDERS:
        for path in _files(root, folder):
            library = LIBRARY_FILE.fullmatch(posixpath.basename(path))
            if not library:
                continue
            for stem, name in KNOWN_LIBRARIES.items():
                if library[1].startswith(stem):
                    yield Component(name, library[2], "library-name", path, 0)


def find_components(root: str) -> list[Component]:
    """Return the components the package database and the library file names show, one per name, sorted by name."""
    found: dict[str, Component] = {}
    # The database is written when the image is built and can lag behind what was
    # installed, so each package is checked against the notes shipped with it.
    for package in _packages(root):
        found.setdefault(package.name, _documented(root, package))
    for library in _libraries(root):
        found.setdefault(library.name, library)
    return sorted(found.values(), key=lambda component: component.name)
