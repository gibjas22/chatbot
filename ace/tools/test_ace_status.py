#!/usr/bin/env python3
"""Tests for the ACE status tracker and catalogue generator.

Run with `python3 -m unittest discover -s ace/tools -p 'test_*.py'`.
Standard library only, no pytest.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


status = _load("ace_status")
catalogue_doc = _load("build_catalogue_doc")


class TestCatalogueIntegrity(unittest.TestCase):
    """The matrix is fixed by the generator skill. Guard it against drift."""

    @classmethod
    def setUpClass(cls):
        cls.data = status.load_catalogue()

    def test_forty_eight_categories(self):
        self.assertEqual(len(self.data["categories"]), 48)

    def test_seven_lenses(self):
        self.assertEqual(len(self.data["lenses"]), 7)

    def test_matrix_is_336(self):
        self.assertEqual(len(self.data["categories"]) * len(self.data["lenses"]), 336)

    def test_sixteen_categories_per_business_line(self):
        for prefix in ("DM", "AI", "TR"):
            count = sum(
                1 for c in self.data["categories"] if c["code"].startswith(prefix)
            )
            self.assertEqual(count, 16, f"{prefix} should have 16 categories")

    def test_category_codes_are_unique(self):
        codes = [c["code"] for c in self.data["categories"]]
        self.assertEqual(len(codes), len(set(codes)))

    def test_lens_codes_are_l1_to_l7(self):
        codes = [lens["code"] for lens in self.data["lenses"]]
        self.assertEqual(codes, [f"L{n}" for n in range(1, 8)])

    def test_every_category_has_name_and_summary(self):
        for category in self.data["categories"]:
            self.assertTrue(category["name"].strip(), category["code"])
            self.assertTrue(category["summary"].strip(), category["code"])


class TestBriefPattern(unittest.TestCase):
    def test_matches_a_valid_brief_name(self):
        match = status.BRIEF_PATTERN.match("DM01-L2-local-service-authority.md")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1) + match.group(2), "DM01")
        self.assertEqual(match.group(3), "L2")

    def test_rejects_a_missing_lens(self):
        self.assertIsNone(status.BRIEF_PATTERN.match("DM01-local-service.md"))

    def test_rejects_an_out_of_range_lens(self):
        self.assertIsNone(status.BRIEF_PATTERN.match("DM01-L8-something.md"))

    def test_rejects_an_unknown_prefix(self):
        self.assertIsNone(status.BRIEF_PATTERN.match("XX01-L1-something.md"))

    def test_rejects_the_template_and_readme(self):
        self.assertIsNone(status.BRIEF_PATTERN.match("_TEMPLATE.md"))
        self.assertIsNone(status.BRIEF_PATTERN.match("README.md"))


class TestBuiltEngines(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.library = Path(self._temp.name)
        self._original = status.LIBRARY_DIR
        status.LIBRARY_DIR = self.library

    def tearDown(self):
        status.LIBRARY_DIR = self._original
        self._temp.cleanup()

    def test_empty_library(self):
        self.assertEqual(status.built_engines(), {})

    def test_counts_valid_briefs_and_ignores_the_rest(self):
        for name in (
            "DM01-L1-local.md",
            "AI16-L7-advisory.md",
            "README.md",
            "_TEMPLATE.md",
            "notes.md",
        ):
            (self.library / name).write_text("x", encoding="utf-8")
        built = status.built_engines()
        self.assertEqual(set(built), {("DM01", "L1"), ("AI16", "L7")})

    def test_missing_library_directory_is_not_an_error(self):
        status.LIBRARY_DIR = self.library / "does-not-exist"
        self.assertEqual(status.built_engines(), {})

    def test_summary_reports_the_right_totals(self):
        (self.library / "DM01-L1-local.md").write_text("x", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as output:
            status.print_summary(status.load_catalogue(), status.built_engines())
        text = output.getvalue()
        self.assertIn("1 of 336", text)

    def test_missing_excludes_what_is_built(self):
        (self.library / "DM01-L1-local.md").write_text("x", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            count = status.print_missing(
                status.load_catalogue(), status.built_engines(), "DM", "L1"
            )
        self.assertEqual(count, 15)


class TestBar(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(status.bar(0, 10, width=10), "." * 10)

    def test_full(self):
        self.assertEqual(status.bar(10, 10, width=10), "#" * 10)

    def test_half(self):
        self.assertEqual(status.bar(5, 10, width=10), "#####.....")

    def test_zero_total_does_not_divide_by_zero(self):
        self.assertEqual(status.bar(0, 0, width=4), "    ")


class TestCatalogueDoc(unittest.TestCase):
    def test_render_includes_every_category(self):
        data = status.load_catalogue()
        rendered = catalogue_doc.render(data)
        for category in data["categories"]:
            self.assertIn(category["code"], rendered)

    def test_render_is_stable(self):
        data = status.load_catalogue()
        self.assertEqual(catalogue_doc.render(data), catalogue_doc.render(data))

    def test_committed_doc_matches_the_json(self):
        """Guards against editing CATALOGUE.md by hand and leaving it drifted."""
        data = json.loads(catalogue_doc.CATALOGUE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(
            catalogue_doc.CATALOGUE_DOC.read_text(encoding="utf-8"),
            catalogue_doc.render(data),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
