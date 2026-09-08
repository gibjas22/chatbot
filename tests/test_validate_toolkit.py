"""Tests for the Ogenic toolkit validator.

The validator is the thing that catches a skill which would silently fail to
load, so its own faults are expensive. These tests exercise it against
purpose-built toolkits written into a temporary directory.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_PATH = REPO_ROOT / "tools" / "ogenic" / "validate_toolkit.py"


def load_validator():
    """Import the validator by path, since tools/ is not a package."""
    spec = importlib.util.spec_from_file_location("validate_toolkit", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()

GOOD_DESCRIPTION = (
    "Does a specific and useful thing for the repository. "
    "Use when the task involves that specific thing."
)


def write_skill(root: Path, directory: str, body: str) -> Path:
    skill_dir = root / "skills" / directory
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / "SKILL.md"
    path.write_text(body, encoding="utf-8")
    return path


def valid_skill_text(name: str, description: str = GOOD_DESCRIPTION) -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n\n# Heading\n\nBody.\n"


class FrontmatterTests(unittest.TestCase):
    def test_parses_keys_and_returns_body(self):
        fields, body = validator.parse_frontmatter(
            "---\nname: thing\ndescription: what it does\n---\n\n# Title\n"
        )
        self.assertEqual(fields["name"], "thing")
        self.assertEqual(fields["description"], "what it does")
        self.assertIn("# Title", body)

    def test_strips_matching_quotes_from_values(self):
        fields, _ = validator.parse_frontmatter('---\nname: "quoted"\n---\nbody\n')
        self.assertEqual(fields["name"], "quoted")

    def test_keeps_colons_inside_a_value(self):
        fields, _ = validator.parse_frontmatter(
            "---\ndescription: Five stages: frame, plan, build\n---\nbody\n"
        )
        self.assertEqual(fields["description"], "Five stages: frame, plan, build")

    def test_returns_none_when_there_is_no_frontmatter(self):
        fields, body = validator.parse_frontmatter("# Just a heading\n")
        self.assertIsNone(fields)
        self.assertEqual(body, "# Just a heading\n")

    def test_returns_none_when_frontmatter_is_unterminated(self):
        fields, _ = validator.parse_frontmatter("---\nname: thing\n\n# No closing\n")
        self.assertIsNone(fields)


class SkillValidationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def messages(self, problems):
        return " | ".join(p.message for p in problems)

    def test_a_well_formed_skill_produces_no_problems(self):
        write_skill(self.root, "good-skill", valid_skill_text("good-skill"))
        problems = validator.validate_skill(self.root / "skills" / "good-skill")
        self.assertEqual(problems, [], self.messages(problems))

    def test_name_must_match_the_directory(self):
        write_skill(self.root, "actual-dir", valid_skill_text("different-name"))
        problems = validator.validate_skill(self.root / "skills" / "actual-dir")
        self.assertIn("does not match directory", self.messages(problems))

    def test_name_must_be_kebab_case(self):
        write_skill(self.root, "Bad_Name", valid_skill_text("Bad_Name"))
        problems = validator.validate_skill(self.root / "skills" / "Bad_Name")
        self.assertIn("kebab-case", self.messages(problems))

    def test_missing_skill_file_is_reported(self):
        (self.root / "skills" / "empty-dir").mkdir(parents=True)
        problems = validator.validate_skill(self.root / "skills" / "empty-dir")
        self.assertIn("missing SKILL.md", self.messages(problems))

    def test_missing_frontmatter_is_fatal(self):
        write_skill(self.root, "no-front", "# Heading only\n")
        problems = validator.validate_skill(self.root / "skills" / "no-front")
        self.assertTrue(any(p.fatal for p in problems))
        self.assertIn("frontmatter", self.messages(problems))

    def test_short_description_is_fatal(self):
        write_skill(self.root, "terse", valid_skill_text("terse", "too short"))
        problems = validator.validate_skill(self.root / "skills" / "terse")
        self.assertIn("needs", self.messages(problems))

    def test_description_without_a_trigger_phrase_is_only_a_warning(self):
        description = "A" * 60
        write_skill(
            self.root, "no-trigger", valid_skill_text("no-trigger", description)
        )
        problems = validator.validate_skill(self.root / "skills" / "no-trigger")
        self.assertTrue(problems)
        self.assertFalse(any(p.fatal for p in problems), self.messages(problems))

    def test_trigger_phrases_other_than_use_when_are_accepted(self):
        for phrase in ("Use whenever", "Use for", "Use at", "Use before"):
            with self.subTest(phrase=phrase):
                description = (
                    f"Does a specific job of real substance here. {phrase} it applies."
                )
                write_skill(self.root, "trig", valid_skill_text("trig", description))
                problems = validator.validate_skill(self.root / "skills" / "trig")
                self.assertEqual(problems, [], self.messages(problems))

    def test_empty_body_is_fatal(self):
        write_skill(
            self.root,
            "hollow",
            f"---\nname: hollow\ndescription: {GOOD_DESCRIPTION}\n---\n\n",
        )
        problems = validator.validate_skill(self.root / "skills" / "hollow")
        self.assertIn("body is empty", self.messages(problems))


class SecretScanTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def scan_text(self, text):
        path = self.root / "sample.md"
        path.write_text(text, encoding="utf-8")
        return validator.scan_for_secrets([path])

    def test_flags_an_openai_key(self):
        self.assertTrue(self.scan_text("key = 'sk-abcdefghijklmnopqrstuvwx'"))

    def test_flags_a_github_token(self):
        self.assertTrue(self.scan_text("token: ghp_abcdefghijklmnopqrstuvwxyz01"))

    def test_flags_an_aws_access_key(self):
        self.assertTrue(self.scan_text("aws: AKIAIOSFODNN7EXAMPLE"))

    def test_flags_a_private_key_block(self):
        self.assertTrue(self.scan_text("-----BEGIN RSA PRIVATE KEY-----"))

    def test_ignores_an_obvious_placeholder(self):
        self.assertEqual(self.scan_text("key = 'your-api-key-here'"), [])

    def test_reports_the_line_number(self):
        problems = self.scan_text("clean line\nkey = 'sk-abcdefghijklmnopqrstuvwx'\n")
        self.assertIn("line 2", problems[0].message)


class CommandValidationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write_command(self, text):
        path = self.root / "cmd.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_a_well_formed_command_passes(self):
        path = self.write_command("---\ndescription: Does a thing\n---\n\nBody.\n")
        self.assertEqual(validator.validate_command(path), [])

    def test_a_missing_description_is_only_a_warning(self):
        path = self.write_command("Just a body with no frontmatter.\n")
        problems = validator.validate_command(path)
        self.assertTrue(problems)
        self.assertFalse(any(p.fatal for p in problems))

    def test_an_empty_body_is_fatal(self):
        path = self.write_command("---\ndescription: Does a thing\n---\n")
        problems = validator.validate_command(path)
        self.assertTrue(any(p.fatal for p in problems))


class RealToolkitTests(unittest.TestCase):
    """The toolkit shipped in this repository must itself pass."""

    def test_every_shipped_skill_is_valid(self):
        skills_dir = REPO_ROOT / ".claude" / "skills"
        self.assertTrue(
            skills_dir.is_dir(), "the toolkit's skills directory is missing"
        )

        found = 0
        for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            with self.subTest(skill=skill_dir.name):
                problems = validator.validate_skill(skill_dir)
                fatal = [p for p in problems if p.fatal]
                self.assertEqual(fatal, [], " | ".join(p.message for p in fatal))
            found += 1
        self.assertGreater(found, 0, "no skills found to validate")

    def test_no_shipped_file_contains_a_credential(self):
        paths = list((REPO_ROOT / ".claude").rglob("*.md"))
        self.assertTrue(paths)
        problems = validator.scan_for_secrets(paths)
        self.assertEqual(problems, [], " | ".join(p.message for p in problems))


if __name__ == "__main__":
    unittest.main()
