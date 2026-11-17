from minifw.components import Component, find_components
from minifw.tests.support import TempCase, elf, write


class BannerDetectionTest(TempCase):
    def test_banner_overrides_package_database_and_library_name(self):
        write(self.tmp, "var/lib/pkgs/status", "Package: harbourd\nVersion: 1.0.0\n")
        write(self.tmp, "usr/lib/libz.so.1.2.3", elf())
        write(self.tmp, "usr/sbin/harbourd", elf("harbourd/2.4.1"))
        found = {item.name: item for item in find_components(self.tmp)}
        self.assertEqual(found["harbourd"], Component("harbourd", "2.4.1", "banner", "usr/sbin/harbourd", 33))
        self.assertEqual(found["zpack"].source, "library-name")

    def test_both_banner_forms_and_multiple_banners(self):
        write(self.tmp, "bin/one", elf("firstd/1.2", "secondd version 3.4.5"))
        found = {item.name: item for item in find_components(self.tmp)}
        self.assertEqual(found["firstd"].version, "1.2")
        self.assertEqual(found["secondd"].version, "3.4.5")
        self.assertEqual(found["secondd"].source, "banner")

    def test_banner_requires_token_boundary_and_elf(self):
        write(self.tmp, "sbin/not-elf", b"prefix goodd/1.2")
        write(self.tmp, "sbin/elf", elf("9goodd/1.2", "Goodd/1.2", "goodd/1.2"))
        self.assertEqual([(item.name, item.version) for item in find_components(self.tmp)], [("goodd", "1.2")])

    def test_banner_wins_over_package_even_if_version_differs(self):
        write(self.tmp, "var/lib/pkgs/status", "Package: exampled\nVersion: 1.0\n")
        write(self.tmp, "usr/bin/exampled", elf("exampled version 2.0"))
        self.assertEqual(find_components(self.tmp), [Component("exampled", "2.0", "banner", "usr/bin/exampled", 33)])

    def test_documentation_does_not_override_package_version(self):
        write(self.tmp, "var/lib/pkgs/status", "Package: linkcfgd\nVersion: 1.8.2\n")
        write(self.tmp, "usr/share/doc/linkcfgd/CHANGES", "linkcfgd 1.8\n")
        self.assertEqual(find_components(self.tmp), [Component("linkcfgd", "1.8.2", "package-db", "var/lib/pkgs/status", 0)])

    def test_zebra_library_does_not_become_zpack(self):
        write(self.tmp, "usr/lib/libzebra.so.1.2.3", elf())
        self.assertEqual(find_components(self.tmp), [])

    def test_library_exact_stem_still_works(self):
        write(self.tmp, "usr/lib/libz.so.1.2.3", elf())
        self.assertEqual(find_components(self.tmp), [Component("zpack", "1.2.3", "library-name", "usr/lib/libz.so.1.2.3", 0)])

    def test_recursive_nested_elf_scan_and_forward_slashes(self):
        write(self.tmp, "usr/lib/plugins/one/thing", elf("nested/4.5"))
        self.assertEqual(find_components(self.tmp), [Component("nested", "4.5", "banner", "usr/lib/plugins/one/thing", 33)])
