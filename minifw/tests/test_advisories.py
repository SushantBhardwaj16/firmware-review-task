import json

from minifw import advisories
from minifw.components import Component
from minifw.tests.support import TempCase, write


def component(name, version):
    return Component(name, version, "package-db", "var/lib/pkgs/status", 0)


def advisory(identifier, name, introduced, fixed, severity="high"):
    return {"id": identifier, "component": name, "introduced": introduced, "fixed": fixed, "severity": severity}


RANGE = [advisory("TWA-2026-0001", "quayd", "3.0.0", "3.0.6")]


class MatchTest(TempCase):
    def affected(self, version, rules=RANGE):
        return [row["advisory"] for row in advisories.match([component("quayd", version)], rules)]

    def test_row_has_advisory_component_version_and_severity(self):
        self.assertEqual(advisories.match([component("quayd", "3.0.2")], RANGE), [
            {"advisory": "TWA-2026-0001", "component": "quayd", "version": "3.0.2", "severity": "high"},
        ])

    def test_range_includes_introduced_and_excludes_fixed(self):
        self.assertEqual(self.affected("3.0.0"), ["TWA-2026-0001"])
        self.assertEqual(self.affected("3.0.5"), ["TWA-2026-0001"])
        self.assertEqual(self.affected("3.0.6"), [])
        self.assertEqual(self.affected("2.9.9"), [])

    def test_versions_compare_as_integers(self):
        rules = [advisory("TWA-2026-0002", "quayd", "1.9", "1.10")]
        self.assertEqual(self.affected("1.9.3", rules), ["TWA-2026-0002"])
        self.assertEqual(self.affected("1.10", rules), [])
        self.assertEqual(self.affected("1.10.0", rules), [])
        self.assertEqual(self.affected("1.9.0.0", rules), ["TWA-2026-0002"])

    def test_null_introduced_and_null_fixed(self):
        self.assertEqual(self.affected("0.0.1", [advisory("TWA-2026-0003", "quayd", None, "2.0.0")]), ["TWA-2026-0003"])
        self.assertEqual(self.affected("2.0", [advisory("TWA-2026-0003", "quayd", None, "2.0.0")]), [])
        self.assertEqual(self.affected("99.1", [advisory("TWA-2026-0004", "quayd", "3.0.0", None)]), ["TWA-2026-0004"])
        self.assertEqual(self.affected("2.9", [advisory("TWA-2026-0004", "quayd", "3.0.0", None)]), [])

    def test_version_that_is_not_dotted_integers_is_skipped(self):
        for version in ("unknown", "3.0.2-rc1", "3.0.x", "", "v3.0.2"):
            self.assertEqual(self.affected(version), [], version)

    def test_names_match_exactly(self):
        rules = [advisory("TWA-2026-0005", "quay", None, None), advisory("TWA-2026-0006", "QuayD", None, None)]
        self.assertEqual(self.affected("1.0", rules), ["TWA-2026-0006"])

    def test_sorted_by_component_then_advisory(self):
        rules = [advisory("TWA-2026-0009", "quayd", None, None), advisory("TWA-2026-0007", "quayd", None, None),
                 advisory("TWA-2026-0008", "anchor", None, None)]
        rows = advisories.match([component("quayd", "1.0"), component("anchor", "1.0")], rules)
        self.assertEqual([(row["component"], row["advisory"]) for row in rows],
                         [("anchor", "TWA-2026-0008"), ("quayd", "TWA-2026-0007"), ("quayd", "TWA-2026-0009")])

    def test_load(self):
        path = write(self.tmp, "advisories.json", json.dumps(RANGE + [{**RANGE[0], "title": "kept"}]))
        self.assertEqual(advisories.load(path)[1]["title"], "kept")

    def test_load_rejects_a_file_of_the_wrong_shape(self):
        for wrong in ({"advisories": RANGE}, [{"id": "TWA-2026-0001"}], [advisory("TWA-2026-0001", "quayd", "three", None)]):
            with self.assertRaises(ValueError):
                advisories.load(write(self.tmp, "advisories.json", json.dumps(wrong)))
        with self.assertRaises(ValueError):
            advisories.load(write(self.tmp, "advisories.json", "not json"))
