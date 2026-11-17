"""Helpers for the tests: small root trees and KFW1 images, built in a temporary folder."""

import io
import os
import struct
import tarfile
import tempfile
import unittest
import zlib


class TempCase(unittest.TestCase):
    """A test case with its own empty folder, self.tmp, removed afterwards."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.tmp = folder.name


def write(root, path, data=b""):
    """Write bytes or text to path under root, make its folders, and return the full path."""
    full = os.path.join(root, *path.split("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as handle:
        handle.write(data.encode() if isinstance(data, str) else data)
    return full


def elf(*texts, bits=32, endian="little", machine=40):
    """An ELF look-alike: a short header, then each text between NUL bytes, as in a real program."""
    header = b"\x7fELF" + bytes([bits // 32, 1 if endian == "little" else 2, 1]) + bytes(11)
    header += machine.to_bytes(2, endian) + bytes(12)
    return header + b"".join(b"\x00" + text.encode() + b"\x00\xfe\xed" for text in texts)


def payload(members):
    """A gzip-compressed tar. Each member is (name, mode, content): bytes for a file, None for a
    folder, text for a link and its target."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz", format=tarfile.USTAR_FORMAT) as archive:
        for name, mode, content in members:
            info = tarfile.TarInfo(name)
            info.mode = mode
            if content is None:
                info.type = tarfile.DIRTYPE
            elif isinstance(content, str):
                info.type, info.linkname = tarfile.SYMTYPE, content
            else:
                info.size = len(content)
            archive.addfile(info, io.BytesIO(content) if isinstance(content, bytes) else None)
    return buffer.getvalue()


def image(data, magic=b"KFW1", header_size=64, length=None, crc=None):
    """A KFW1 image around a payload. The keyword arguments plant a wrong header field."""
    return struct.pack(
        "<4sHHIII16s16s8s4x",
        magic,
        header_size,
        0,
        64,
        len(data) if length is None else length,
        zlib.crc32(data) if crc is None else crc,
        b"LANTERN-3",
        b"0.9.0",
        b"20260115",
    ) + data
