#!/usr/bin/env python3
"""Tests for the chat export importer.

Run directly, or with `python3 -m unittest discover -s aibos/tools -p 'test_*.py'`.
Standard library only, no pytest.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

# Load the importer by path rather than by name. It sits beside this file rather
# than on the import path, and loading it explicitly keeps every import at the
# top of the module and works whatever directory the tests are run from.
_MODULE_PATH = Path(__file__).resolve().parent / "import_chat_export.py"
_SPEC = importlib.util.spec_from_file_location("import_chat_export", _MODULE_PATH)
importer = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(importer)


CLAUDE_EXPORT = [
    {
        "uuid": "aaa-111",
        "name": "AIBOS voice layer providers",
        "created_at": "2026-08-14T09:12:00.000000Z",
        "updated_at": "2026-08-14T10:02:00.000000Z",
        "chat_messages": [
            {"sender": "human", "text": "Which TTS provider for the briefing?"},
            {
                "sender": "assistant",
                "content": [{"type": "text", "text": "ElevenLabs for quality."}],
            },
        ],
    },
    {
        "uuid": "ccc-333",
        "name": "Sourdough troubleshooting",
        "created_at": "2026-07-02T08:00:00.000000Z",
        "updated_at": "2026-07-02T08:30:00.000000Z",
        "chat_messages": [{"sender": "human", "text": "My starter is not rising."}],
    },
]

CHATGPT_EXPORT = [
    {
        "title": "Gibcom AIBOS leadgen filters",
        "conversation_id": "conv-1",
        "create_time": 1786000000.0,
        "update_time": 1786003600.0,
        "current_node": "n3",
        "mapping": {
            "root": {"id": "root", "message": None, "parent": None, "children": ["n1"]},
            "n1": {
                "id": "n1",
                "parent": "root",
                "message": {
                    "author": {"role": "system"},
                    "create_time": 1.0,
                    "content": {"content_type": "text", "parts": ["hidden preamble"]},
                },
            },
            "n2": {
                "id": "n2",
                "parent": "n1",
                "message": {
                    "author": {"role": "user"},
                    "create_time": 2.0,
                    "content": {"content_type": "text", "parts": ["Which SIC codes?"]},
                },
            },
            "n3": {
                "id": "n3",
                "parent": "n2",
                "message": {
                    "author": {"role": "assistant"},
                    "create_time": 3.0,
                    "content": {"content_type": "text", "parts": ["Start with 70229."]},
                },
            },
        },
    }
]


class TestSlugify(unittest.TestCase):
    def test_lowercases_and_hyphenates(self):
        self.assertEqual(importer.slugify("AIBOS Voice Layer"), "aibos-voice-layer")

    def test_strips_punctuation(self):
        self.assertEqual(importer.slugify("Gibcom: AIBOS (v2)!"), "gibcom-aibos-v2")

    def test_empty_input_falls_back(self):
        self.assertEqual(importer.slugify("!!!"), "untitled")

    def test_truncates_on_a_word_boundary(self):
        slug = importer.slugify("alpha bravo charlie delta echo foxtrot golf", 20)
        self.assertLessEqual(len(slug), 20)
        self.assertFalse(slug.endswith("-"))


class TestParseDate(unittest.TestCase):
    def test_iso_string(self):
        self.assertEqual(importer.parse_date("2026-08-14T09:12:00Z"), "2026-08-14")

    def test_unix_timestamp_is_read_as_utc(self):
        # 1786000000 is 2026-08-06T07:06:40Z. That is still 2026-08-05 in any
        # timezone west of UTC-08:00, so this also pins the conversion to UTC
        # rather than to whatever the machine running the import happens to be.
        self.assertEqual(importer.parse_date(1786000000.0), "2026-08-06")

    def test_missing_value(self):
        self.assertEqual(importer.parse_date(None), importer.UNKNOWN_DATE)
        self.assertEqual(importer.parse_date(""), importer.UNKNOWN_DATE)

    def test_unparseable_string_falls_back_to_prefix(self):
        self.assertEqual(importer.parse_date("2026-08-14 sometime"), "2026-08-14")


class TestDetectFormat(unittest.TestCase):
    def test_claude(self):
        self.assertEqual(importer.detect_format(CLAUDE_EXPORT), "claude")

    def test_chatgpt(self):
        self.assertEqual(importer.detect_format(CHATGPT_EXPORT), "chatgpt")

    def test_unknown(self):
        self.assertEqual(importer.detect_format([{"something": "else"}]), "unknown")

    def test_empty(self):
        self.assertEqual(importer.detect_format([]), "unknown")


class TestNormaliseClaude(unittest.TestCase):
    def setUp(self):
        self.record = importer.normalise_claude(CLAUDE_EXPORT[0])

    def test_metadata(self):
        self.assertEqual(self.record["title"], "AIBOS voice layer providers")
        self.assertEqual(self.record["created"], "2026-08-14")
        self.assertEqual(self.record["source"], "claude-web")

    def test_reads_both_message_shapes(self):
        texts = [message["text"] for message in self.record["messages"]]
        self.assertEqual(
            texts, ["Which TTS provider for the briefing?", "ElevenLabs for quality."]
        )


class TestNormaliseChatgpt(unittest.TestCase):
    def setUp(self):
        self.record = importer.normalise_chatgpt(CHATGPT_EXPORT[0])

    def test_metadata(self):
        self.assertEqual(self.record["title"], "Gibcom AIBOS leadgen filters")
        self.assertEqual(self.record["source"], "chatgpt")
        self.assertEqual(self.record["uuid"], "conv-1")

    def test_drops_system_messages(self):
        roles = [message["role"] for message in self.record["messages"]]
        self.assertNotIn("system", roles)

    def test_orders_messages_by_walking_back_from_current_node(self):
        texts = [message["text"] for message in self.record["messages"]]
        self.assertEqual(texts, ["Which SIC codes?", "Start with 70229."])

    def test_falls_back_to_timestamp_order_without_current_node(self):
        conversation = dict(CHATGPT_EXPORT[0])
        conversation.pop("current_node")
        record = importer.normalise_chatgpt(conversation)
        texts = [message["text"] for message in record["messages"]]
        self.assertEqual(texts, ["Which SIC codes?", "Start with 70229."])


class TestMatching(unittest.TestCase):
    def test_matches_on_title(self):
        record = importer.normalise_claude(CLAUDE_EXPORT[0])
        self.assertTrue(importer.matches(record, ["aibos"]))

    def test_rejects_unrelated_conversation(self):
        record = importer.normalise_claude(CLAUDE_EXPORT[1])
        self.assertFalse(importer.matches(record, importer.DEFAULT_TERMS))

    def test_matches_on_body_when_title_is_silent(self):
        record = importer.normalise_chatgpt(CHATGPT_EXPORT[0])
        record["title"] = "Untitled"
        self.assertTrue(importer.matches(record, ["sic codes"]))


class TestRender(unittest.TestCase):
    def test_claude_render_has_frontmatter_and_transcript(self):
        output = importer.render(importer.normalise_claude(CLAUDE_EXPORT[0]))
        self.assertTrue(output.startswith("---\n"))
        self.assertIn('title: "AIBOS voice layer providers"', output)
        self.assertIn("source: claude-web", output)
        self.assertIn("### Gibson", output)
        self.assertIn("### Claude", output)

    def test_chatgpt_render_attributes_the_right_assistant(self):
        output = importer.render(importer.normalise_chatgpt(CHATGPT_EXPORT[0]))
        self.assertIn("source: chatgpt", output)
        self.assertIn("### ChatGPT", output)
        self.assertNotIn("### Claude", output)

    def test_title_with_quotes_is_escaped(self):
        record = importer.normalise_claude(CLAUDE_EXPORT[0])
        record["title"] = 'A "quoted" title'
        self.assertIn(r'title: "A \"quoted\" title"', importer.render(record))


class TestUniquePath(unittest.TestCase):
    def test_appends_a_suffix_on_collision(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            first = importer.unique_path(directory, "2026-08-14", "topic")
            first.write_text("x", encoding="utf-8")
            second = importer.unique_path(directory, "2026-08-14", "topic")
            self.assertEqual(first.name, "2026-08-14-topic.md")
            self.assertEqual(second.name, "2026-08-14-topic-2.md")


class TestLoadExport(unittest.TestCase):
    """Both vendors email a zip, so the importer has to read one directly."""

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.directory = Path(self._temp.name)

    def tearDown(self):
        self._temp.cleanup()

    def _write_json(self, name="conversations.json", payload=None):
        path = self.directory / name
        path.write_text(
            json.dumps(payload if payload is not None else CLAUDE_EXPORT),
            encoding="utf-8",
        )
        return path

    def test_reads_a_plain_json_file(self):
        data, source = importer.load_export(self._write_json())
        self.assertEqual(len(data), len(CLAUDE_EXPORT))
        self.assertEqual(source, "conversations.json")

    def test_reads_conversations_json_out_of_a_zip(self):
        json_path = self._write_json("payload.json")
        archive = self.directory / "export.zip"
        with zipfile.ZipFile(archive, "w") as handle:
            handle.write(json_path, "conversations.json")
            handle.writestr("users.json", "[]")
        data, source = importer.load_export(archive)
        self.assertEqual(len(data), len(CLAUDE_EXPORT))
        self.assertIn("export.zip", source)
        self.assertIn("conversations.json", source)

    def test_prefers_the_shallowest_conversations_json(self):
        archive = self.directory / "export.zip"
        with zipfile.ZipFile(archive, "w") as handle:
            handle.writestr("backup/old/conversations.json", "[]")
            handle.writestr("conversations.json", json.dumps(CLAUDE_EXPORT))
        data, _ = importer.load_export(archive)
        self.assertEqual(
            len(data), len(CLAUDE_EXPORT), "should not pick the nested empty one"
        )

    def test_zip_without_an_export_names_what_it_found(self):
        archive = self.directory / "wrong.zip"
        with zipfile.ZipFile(archive, "w") as handle:
            handle.writestr("readme.txt", "not an export")
        with self.assertRaises(ValueError) as caught:
            importer.load_export(archive)
        self.assertIn("readme.txt", str(caught.exception))

    def test_a_zip_that_will_not_open_says_so(self):
        """The message must not blame JSON for a broken archive."""
        archive = self.directory / "corrupt.zip"
        archive.write_bytes(b"PK\x03\x04 truncated")
        with self.assertRaises(ValueError) as caught:
            importer.load_export(archive)
        message = str(caught.exception)
        self.assertIn("zip", message.lower())
        self.assertNotIn("JSON", message)

    def test_invalid_json_is_reported_as_such(self):
        path = self.directory / "conversations.json"
        path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            importer.load_export(path)
        self.assertIn("JSON", str(caught.exception))

    def test_json_that_is_not_a_list_is_rejected(self):
        """Wrong shape is a TypeError; wrong content is a ValueError."""
        path = self.directory / "conversations.json"
        path.write_text('{"conversations": []}', encoding="utf-8")
        with self.assertRaises(TypeError) as caught:
            importer.load_export(path)
        message = str(caught.exception)
        self.assertIn("list", message)
        self.assertIn("dict", message, "should name what it found instead")

    def test_main_exits_1_on_every_bad_input(self):
        """Whichever exception load_export raises, the CLI must not traceback."""
        cases = {
            "not-a-list.json": '{"conversations": []}',
            "bad.json": "{not json",
        }
        for name, payload in cases.items():
            path = self.directory / name
            path.write_text(payload, encoding="utf-8")
            with (
                self.subTest(case=name),
                contextlib.redirect_stderr(io.StringIO()) as err,
            ):
                self.assertEqual(importer.main([str(path)]), 1)
            self.assertTrue(err.getvalue().strip(), f"{name} should explain itself")

    def test_binary_input_is_reported_as_not_text(self):
        path = self.directory / "random.bin"
        path.write_bytes(bytes(range(256)))
        with self.assertRaises(ValueError) as caught:
            importer.load_export(path)
        self.assertIn("not text", str(caught.exception))


class TestArchiveReading(unittest.TestCase):
    """Cover read_frontmatter, index_rows, list and search against a real folder."""

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        directory = Path(self._temp.name)

        (directory / "2026-08-14-voice.md").write_text(
            '---\ntitle: "Voice layer providers"\ndate: 2026-08-14\n'
            "source: claude-web\ntopics: [voice, providers]\nstatus: active\n---\n\n"
            "# Voice layer providers\n\nElevenLabs for quality.\n",
            encoding="utf-8",
        )
        (directory / "2026-08-06-briefing.md").write_text(
            '---\ntitle: "Morning briefing"\ndate: 2026-08-06\n'
            "source: chatgpt\ntopics: [briefing]\nstatus: settled\n---\n\n"
            "# Morning briefing\n\nFires at 06:30 local.\n",
            encoding="utf-8",
        )
        # Neither of these is a captured conversation and both must be ignored.
        (directory / "_TEMPLATE.md").write_text(
            "---\ntitle: x\n---\n", encoding="utf-8"
        )
        (directory / "README.md").write_text("# Conversations\n", encoding="utf-8")

        self._original = importer.CONVERSATIONS_DIR
        importer.CONVERSATIONS_DIR = directory

    def tearDown(self):
        importer.CONVERSATIONS_DIR = self._original
        self._temp.cleanup()

    def test_captured_files_excludes_template_and_readme(self):
        names = [path.name for path in importer.captured_files()]
        self.assertEqual(names, ["2026-08-14-voice.md", "2026-08-06-briefing.md"])

    def test_read_frontmatter(self):
        path = importer.CONVERSATIONS_DIR / "2026-08-06-briefing.md"
        meta = importer.read_frontmatter(path)
        self.assertEqual(meta["title"], "Morning briefing")
        self.assertEqual(meta["source"], "chatgpt")
        self.assertEqual(meta["status"], "settled")

    def test_read_frontmatter_on_a_file_without_any(self):
        path = importer.CONVERSATIONS_DIR / "plain.md"
        path.write_text("no frontmatter here\n", encoding="utf-8")
        self.assertEqual(importer.read_frontmatter(path), {})

    def test_index_rows_are_newest_first(self):
        dates = [row[0] for row in importer.index_rows()]
        self.assertEqual(dates, ["2026-08-14", "2026-08-06"])

    def test_list_returns_every_conversation(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(importer.list_conversations(), 2)

    def test_list_filters_by_source(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            count = importer.list_conversations(source="chatgpt")
        self.assertEqual(count, 1)
        self.assertIn("Morning briefing", output.getvalue())
        self.assertNotIn("Voice layer", output.getvalue())

    def test_list_source_filter_is_case_insensitive(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(importer.list_conversations(source="ChatGPT"), 1)

    def test_list_filters_by_topic(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(importer.list_conversations(topic="providers"), 1)

    def test_list_with_no_matches_returns_zero(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(importer.list_conversations(source="nope"), 0)
        self.assertIn("No conversations match", output.getvalue())

    def test_search_finds_a_term_and_names_the_file(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(importer.search_conversations("ElevenLabs"), 1)
        self.assertIn("2026-08-14-voice.md", output.getvalue())

    def test_search_is_case_insensitive(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(importer.search_conversations("elevenlabs"), 1)

    def test_search_spans_sources(self):
        # "0" appears in both files' dates, so a hit in each proves the search
        # is not stopping at the first file or filtering by source.
        with contextlib.redirect_stdout(io.StringIO()) as output:
            importer.search_conversations("2026-08")
        self.assertIn("2026-08-14-voice.md", output.getvalue())
        self.assertIn("2026-08-06-briefing.md", output.getvalue())

    def test_search_with_no_match_returns_zero(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(importer.search_conversations("sourdough"), 0)
        self.assertIn("No matches", output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
