import dataclasses
import os

from minifw.components import KNOWN_LIBRARIES, Component, find_components
from minifw.tests.support import TempCase, elf, write

STATUS = (
    "Package: harbourd\n"
    "Version: 2.4.1\n"
    "Maintainer: build@lantern.invalid\n"
    "\n"
    "Package: saltcfgd\n"
    "Status: installed\n"
    "Version: 3.2.0\n"
)


class ComponentsTest(TempCase):
    def found(self):
        return [(c.name, c.version, c.source) for c in find_components(self.tmp)]

    def evidence(self, component):
        with open(os.path.join(self.tmp, *component.path.split("/")), "rb") as handle:
            return handle.read()[component.offset:]

    def test_package_database_blocks(self):
        write(self.tmp, "var/lib/pkgs/status", STATUS)
        harbourd, saltcfgd = find_components(self.tmp)
        self.assertEqual(harbourd, Component("harbourd", "2.4.1", "package-db", "var/lib/pkgs/status", 0))
        self.assertEqual(saltcfgd, Component("saltcfgd", "3.2.0", "package-db", "var/lib/pkgs/status", STATUS.index("Package: saltcfgd")))
        self.assertTrue(self.evidence(saltcfgd).startswith(b"Package: saltcfgd\n"))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            harbourd.version = "0"

    def test_package_database_block_without_a_version_is_skipped(self):
        write(self.tmp, "var/lib/pkgs/status", "\n\nPackage: nameonly\n\nVersion: 1.0\n\n" + STATUS)
        self.assertEqual(self.found(), [("harbourd", "2.4.1", "package-db"), ("saltcfgd", "3.2.0", "package-db")])

    def test_no_package_database_and_no_files(self):
        self.assertEqual(find_components(self.tmp), [])
        self.assertEqual(find_components(os.path.join(self.tmp, "missing")), [])

    def test_known_libraries_by_file_name(self):
        self.assertEqual(KNOWN_LIBRARIES, {"z": "zpack", "crypt-lite": "libcrypt-lite"})
        write(self.tmp, "usr/lib/libz.so.1.2.11", elf())
        write(self.tmp, "lib/libcrypt-lite.so.1.0.9", elf())
        self.assertEqual(find_components(self.tmp), [
            Component("libcrypt-lite", "1.0.9", "library-name", "lib/libcrypt-lite.so.1.0.9", 0),
            Component("zpack", "1.2.11", "library-name", "usr/lib/libz.so.1.2.11", 0),
        ])

    def test_other_files_are_not_known_libraries(self):
        for name in ("libkelp.so.2.0.0", "libz.so", "libz.so.1", "libz.so.1.2.11.bak", "z.so.1.2.11"):
            write(self.tmp, f"usr/lib/{name}", elf())
        write(self.tmp, "usr/share/libz.so.1.2.11", elf())
        write(self.tmp, "usr/lib/plugins/libz.so.1.2.11", elf())
        self.assertEqual(self.found(), [])

    def test_package_database_wins_over_library_name(self):
        write(self.tmp, "var/lib/pkgs/status", "Package: zpack\nVersion: 1.2.13\n")
        write(self.tmp, "usr/lib/libz.so.1.2.11", elf())
        self.assertEqual(self.found(), [("zpack", "1.2.13", "package-db")])

    def test_sorted_by_name(self):
        write(self.tmp, "var/lib/pkgs/status", "Package: quayd\nVersion: 1.0\n\nPackage: anchor\nVersion: 2.0\n")
        write(self.tmp, "usr/lib/libz.so.1.2.11", elf())
        self.assertEqual([c.name for c in find_components(self.tmp)], ["anchor", "quayd", "zpack"])
