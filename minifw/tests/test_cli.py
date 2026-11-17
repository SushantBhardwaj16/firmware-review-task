import contextlib
import io
import json
import os
import subprocess
import sys

import minifw
from minifw.__main__ import main
from minifw.tests.support import TempCase, elf, image, payload, write

REPOSITORY = os.path.dirname(os.path.dirname(os.path.abspath(minifw.__file__)))
STATUS = b"Package: quayd\nVersion: 3.0.2\n"
MEMBERS = [("var/lib/pkgs/status", 0o644, STATUS), ("usr/sbin/quayd", 0o755, elf("quayd started"))]
ADVISORIES = [{"id": "TWA-2026-0001", "component": "quayd", "introduced": "3.0.0", "fixed": "3.0.6", "severity": "high"}]


class CommandLineTest(TempCase):
    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = main(list(args))
        return status, out.getvalue(), err.getvalue()

    def unpacked(self):
        root = os.path.join(self.tmp, "root")
        self.assertEqual(self.run_main("unpack", write(self.tmp, "image.bin", image(payload(MEMBERS))), root)[0], 0)
        return root

    def test_unpack(self):
        root = os.path.join(self.tmp, "root")
        status, out, err = self.run_main("unpack", write(self.tmp, "image.bin", image(payload(MEMBERS))), root)
        self.assertEqual((status, err), (0, ""))
        self.assertIn("2 entries", out)
        self.assertTrue(os.path.isfile(os.path.join(root, "MANIFEST.txt")))

    def test_unpack_bad_image(self):
        bad = write(self.tmp, "image.bin", image(payload(MEMBERS), crc=1))
        status, out, err = self.run_main("unpack", bad, os.path.join(self.tmp, "root"))
        self.assertEqual((status, out), (2, ""))
        self.assertTrue(err.startswith("error: "), err)
        self.assertEqual(self.run_main("unpack", os.path.join(self.tmp, "missing.bin"), self.tmp)[0], 2)

    def test_components(self):
        status, out, _ = self.run_main("components", self.unpacked())
        self.assertEqual(status, 0)
        self.assertEqual(out.split(), ["quayd", "3.0.2", "package-db", "var/lib/pkgs/status", "@", "0"])
        self.assertEqual(self.run_main("components", os.path.join(self.tmp, "missing"))[0], 2)

    def test_analyse(self):
        rules = write(self.tmp, "advisories.json", json.dumps(ADVISORIES))
        status, out, _ = self.run_main("analyse", self.unpacked(), rules)
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(out), {
            "components": [{"name": "quayd", "version": "3.0.2", "source": "package-db", "path": "var/lib/pkgs/status", "offset": 0}],
            "affected": [{"advisory": "TWA-2026-0001", "component": "quayd", "version": "3.0.2", "severity": "high"}],
        })
        self.assertEqual(self.run_main("analyse", self.unpacked(), write(self.tmp, "advisories.json", "{"))[0], 2)

    def test_strings(self):
        status, out, _ = self.run_main("strings", os.path.join(self.unpacked(), "usr", "sbin", "quayd"))
        self.assertEqual((status, out), (0, "      33 quayd started\n"))

    def test_elfinfo(self):
        status, out, _ = self.run_main("elfinfo", os.path.join(self.unpacked(), "usr", "sbin", "quayd"))
        self.assertEqual((status, out), (0, "class: 32\nendian: little\nmachine: 40\n"))
        self.assertEqual(self.run_main("elfinfo", os.path.join(self.unpacked(), "MANIFEST.txt"))[0], 2)

    def test_wrong_arguments(self):
        for args in ([], ["help"], ["unpack"], ["unpack", "image.bin"], ["components"], ["components", "a", "b"],
                     ["analyse", "a"], ["strings"], ["elfinfo", "a", "b"]):
            status, out, err = self.run_main(*args)
            self.assertEqual((status, out), (64, ""), args)
            self.assertTrue(err.startswith("usage: python -m minifw"), args)

    def test_runs_as_a_module(self):
        environment = dict(os.environ, PYTHONPATH=REPOSITORY)
        done = subprocess.run([sys.executable, "-B", "-m", "minifw", "components", self.unpacked()],
                              cwd=REPOSITORY, env=environment, capture_output=True, text=True, timeout=60)
        self.assertEqual((done.returncode, done.stdout.split()[:2]), (0, ["quayd", "3.0.2"]), done.stderr)
