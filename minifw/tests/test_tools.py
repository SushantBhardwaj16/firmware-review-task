from minifw import tools
from minifw.tests.support import TempCase, elf, write


class ToolsTest(TempCase):
    def test_strings_gives_offsets_and_text(self):
        path = write(self.tmp, "blob", b"\x00\x01abc\x00quayd/3.0.2\x00\xff~ ok ~\n")
        self.assertEqual(tools.strings(path), [(6, "quayd/3.0.2"), (19, "~ ok ~")])

    def test_strings_minimum_length(self):
        path = write(self.tmp, "blob", b"\x00\x01abc\x00quayd/3.0.2\x00")
        self.assertEqual(tools.strings(path, minimum=3), [(2, "abc"), (6, "quayd/3.0.2")])
        self.assertEqual(tools.strings(path, minimum=12), [])

    def test_elfinfo(self):
        path = write(self.tmp, "program", elf("quayd/3.0.2"))
        self.assertEqual(tools.elfinfo(path), {"class": 32, "endian": "little", "machine": 40})
        path = write(self.tmp, "program", elf(bits=64, endian="big", machine=8))
        self.assertEqual(tools.elfinfo(path), {"class": 64, "endian": "big", "machine": 8})

    def test_elfinfo_rejects_other_files(self):
        for data in (b"#!/bin/sh\necho not a program at all\n", b"\x7fELF", b"\x7fELF" + b"\x09" * 40):
            with self.assertRaises(ValueError):
                tools.elfinfo(write(self.tmp, "other", data))
