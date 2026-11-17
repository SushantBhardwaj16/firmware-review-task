"""Unpack a KFW1 firmware image into a folder.

A KFW1 image is a 64-byte header followed by the root file system as a
gzip-compressed tar. The header, with every integer little-endian:

    magic "KFW1" | header size u16 (64) | flags u16 | payload offset u32 |
    payload length u32 | CRC-32 of the payload u32 | model, 16 bytes |
    version, 16 bytes | build date, 8 bytes | 4 reserved bytes

Nothing in an image is trusted. A member may not be absolute, contain "..",
lie beneath a file or a link, or appear twice, and a link must point inside
the root. Images are small, so there is no limit on the unpacked size.
"""

import io
import os
import posixpath
import struct
import tarfile
import zlib
from dataclasses import dataclass

HEADER = struct.Struct("<4sHHIII16s16s8s4x")
MANIFEST = "MANIFEST.txt"


class ImageError(ValueError):
    """The file is not a valid KFW1 image."""


@dataclass(frozen=True)
class Entry:
    path: str  # from the root, with forward slashes
    mode: int  # permission bits as the image stores them
    size: int  # in bytes; 0 for a folder or a link
    kind: str  # "file", "dir" or "link"


def _payload(image_path: str) -> bytes:
    """Check the header and return the payload it describes."""
    with open(image_path, "rb") as handle:
        data = handle.read()
    if len(data) < HEADER.size:
        raise ImageError("the file is shorter than a KFW1 header")
    magic, header_size, _flags, offset, length, crc = HEADER.unpack_from(data)[:6]
    if magic != b"KFW1":
        raise ImageError("wrong magic: not a KFW1 image")
    if header_size != HEADER.size:
        raise ImageError(f"header size is {header_size}, expected {HEADER.size}")
    if offset < HEADER.size or offset + length != len(data):
        raise ImageError("payload offset and length do not match the file size")
    if zlib.crc32(data[offset:]) != crc:
        raise ImageError("payload CRC-32 does not match the header")
    return data[offset:]


def _link_target(path: str, target: str) -> str:
    """Where a link points, as a path from the root. An absolute target starts at the root."""
    start = "" if target.startswith("/") else posixpath.dirname(path)
    resolved = posixpath.normpath(posixpath.join(start, target.lstrip("/")))
    if resolved == ".." or resolved.startswith("../"):
        raise ImageError(f"link {path!r} points outside the root: {target!r}")
    return resolved


def _members(payload: bytes) -> list[tuple[Entry, bytes | str]]:
    """Every member with its content (a file) or its target from the root (a link)."""
    members: list[tuple[Entry, bytes | str]] = []
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            for member in archive:
                parts = [part for part in member.name.split("/") if part not in ("", ".")]
                if member.name.startswith("/") or ".." in parts:
                    raise ImageError(f"member {member.name!r} would leave the root")
                if not parts:
                    continue  # the root folder itself
                path, mode = "/".join(parts), member.mode & 0o7777
                if member.isreg():
                    data = archive.extractfile(member).read()
                    members.append((Entry(path, mode, len(data), "file"), data))
                elif member.isdir():
                    members.append((Entry(path, mode, 0, "dir"), b""))
                elif member.issym():
                    members.append((Entry(path, mode, 0, "link"), _link_target(path, member.linkname)))
                else:
                    raise ImageError(f"member {path!r} is not a file, a folder or a symbolic link")
    except (tarfile.TarError, OSError, EOFError, zlib.error) as error:
        raise ImageError(f"the payload is not a gzip-compressed tar: {error}") from None
    paths = [entry.path for entry, _ in members]
    if len(set(paths)) != len(paths):
        raise ImageError("a member appears twice")
    leaves = {entry.path for entry, _ in members if entry.kind != "dir"}
    for path in paths:
        parts = path.split("/")
        if any("/".join(parts[:depth]) in leaves for depth in range(1, len(parts))):
            raise ImageError(f"member {path!r} lies beneath a file or a link")
    return members


def _clear(dest: str) -> None:
    """Remove a file or link already at dest, so nothing is written through a link."""
    if os.path.islink(dest) or os.path.isfile(dest):
        os.remove(dest)


def unpack(image_path: str, out_dir: str) -> list[Entry]:
    """Write the image's root file system under out_dir and return its entries.

    Also writes out_dir/MANIFEST.txt, one line per entry: octal mode, size,
    path. Read modes there: not every operating system keeps them on disk.
    Links are written as relative links that stay inside out_dir; where the
    platform has no symbolic links they are listed but not written.
    """
    members = _members(_payload(image_path))
    os.makedirs(out_dir, exist_ok=True)
    root = os.path.realpath(out_dir)
    for entry, content in members:
        dest = os.path.join(root, *entry.path.split("/"))
        parent = os.path.dirname(dest)
        if os.path.commonpath([root, os.path.realpath(parent)]) != root:
            raise ImageError(f"{entry.path!r} would be written outside {out_dir}")
        os.makedirs(parent, exist_ok=True)
        if entry.kind == "dir":
            os.makedirs(dest, exist_ok=True)
            continue
        _clear(dest)
        if entry.kind == "file":
            with open(dest, "wb") as handle:
                handle.write(content)
            os.chmod(dest, entry.mode & 0o777 | 0o600)
        else:
            try:
                os.symlink(posixpath.relpath(content, posixpath.dirname(entry.path) or "."), dest)
            except (OSError, NotImplementedError):
                pass  # no symbolic links here: the manifest still lists it
    manifest = os.path.join(root, MANIFEST)
    _clear(manifest)
    with open(manifest, "w", encoding="utf-8", errors="surrogateescape", newline="\n") as handle:
        for entry, _ in members:
            handle.write(f"{entry.mode:04o} {entry.size} {entry.path}\n")
    return [entry for entry, _ in members]
