import dataclasses
import io
import os
import tarfile

from minifw.tests.support import TempCase, image, payload, write
from minifw.unpack import Entry, ImageError, unpack

MEMBERS = [
    ("etc", 0o755, None),
    ("etc/passwd", 0o644, b"root:x:0:0::/root:/bin/sh\n"),
    ("etc/init.d/S90custom", 0o777, b"#!/bin/sh\n"),
    ("bin/busybox", 0o4755, b"\x7fELF" + bytes(60)),
    ("bin/sh", 0o777, "busybox"),
    ("sbin/init", 0o777, "/bin/busybox"),
]


class UnpackTest(TempCase):
    def setUp(self):
        super().setUp()
        self.out = os.path.join(self.tmp, "out")

    def unpack(self, data):
        return unpack(write(self.tmp, "image.bin", data), self.out)

    def rejects(self, data, words):
        with self.assertRaises(ImageError) as caught:
            self.unpack(data)
        self.assertIn(words, str(caught.exception))
        self.assertEqual(os.listdir(self.tmp), ["image.bin"], "a bad image must write nothing")

    def test_entries_are_returned_in_image_order(self):
        entries = self.unpack(image(payload(MEMBERS)))
        self.assertEqual(entries, [
            Entry("etc", 0o755, 0, "dir"),
            Entry("etc/passwd", 0o644, 26, "file"),
            Entry("etc/init.d/S90custom", 0o777, 10, "file"),
            Entry("bin/busybox", 0o4755, 64, "file"),
            Entry("bin/sh", 0o777, 0, "link"),
            Entry("sbin/init", 0o777, 0, "link"),
        ])
        with self.assertRaises(dataclasses.FrozenInstanceError):
            entries[0].mode = 0

    def test_files_and_folders_are_written(self):
        self.unpack(image(payload(MEMBERS)))
        self.assertTrue(os.path.isdir(os.path.join(self.out, "etc", "init.d")))
        with open(os.path.join(self.out, "etc", "passwd"), "rb") as handle:
            self.assertEqual(handle.read(), b"root:x:0:0::/root:/bin/sh\n")

    def test_manifest_has_mode_size_and_path(self):
        self.unpack(image(payload(MEMBERS)))
        with open(os.path.join(self.out, "MANIFEST.txt"), encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        self.assertEqual(lines, [
            "0755 0 etc",
            "0644 26 etc/passwd",
            "0777 10 etc/init.d/S90custom",
            "4755 64 bin/busybox",
            "0777 0 bin/sh",
            "0777 0 sbin/init",
        ])

    def test_links_stay_inside_the_folder(self):
        self.unpack(image(payload(MEMBERS)))
        for name in ("bin/sh", "sbin/init"):
            link = os.path.join(self.out, *name.split("/"))
            if os.path.islink(link):  # a platform without links writes nothing for them
                self.assertEqual(os.path.realpath(link), os.path.realpath(os.path.join(self.out, "bin", "busybox")))

    def test_unpacking_twice_gives_the_same_tree(self):
        first = self.unpack(image(payload(MEMBERS)))
        self.assertEqual(self.unpack(image(payload(MEMBERS))), first)

    def test_wrong_magic(self):
        self.rejects(image(payload(MEMBERS), magic=b"KFW2"), "magic")

    def test_short_file(self):
        self.rejects(b"KFW1" + bytes(20), "shorter")

    def test_wrong_header_size(self):
        self.rejects(image(payload(MEMBERS), header_size=60), "header size")

    def test_length_that_does_not_match_the_file(self):
        data = payload(MEMBERS)
        self.rejects(image(data, length=len(data) - 1), "file size")
        self.rejects(image(data) + b"\x00", "file size")

    def test_wrong_crc(self):
        self.rejects(image(payload(MEMBERS), crc=0), "CRC")

    def test_payload_that_is_not_a_tar(self):
        self.rejects(image(b"not a gzip-compressed tar"), "tar")

    def test_member_that_leaves_the_root(self):
        for name in ("/etc/evil", "../evil", "etc/../../evil"):
            with self.subTest(name=name):
                self.rejects(image(payload([(name, 0o644, b"x")])), "leave the root")

    def test_link_that_points_outside_the_root(self):
        for name, target in (("evil", ".."), ("etc/evil", "../../outside"), ("evil", "/../outside")):
            with self.subTest(target=target):
                self.rejects(image(payload([(name, 0o777, target)])), "outside the root")

    def test_member_beneath_a_link(self):
        self.rejects(image(payload([("lib64", 0o777, "lib"), ("lib64/evil", 0o644, b"x")])), "beneath")

    def test_member_twice(self):
        self.rejects(image(payload([("etc/a", 0o644, b"x"), ("etc/a", 0o777, "b")])), "twice")

    def test_member_of_another_kind(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            device = tarfile.TarInfo("dev/console")
            device.type = tarfile.CHRTYPE
            archive.addfile(device)
        self.rejects(image(buffer.getvalue()), "not a file")

    def test_existing_link_in_the_folder_is_not_followed(self):
        os.makedirs(self.out)
        try:
            os.symlink(self.tmp, os.path.join(self.out, "etc"))
        except (OSError, NotImplementedError):
            return
        with self.assertRaises(ImageError):
            self.unpack(image(payload(MEMBERS)))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "passwd")))
