#!/usr/bin/env python3
"""Tests for the chat export importer.

Run directly, or with `python3 -m unittest discover -s aibos/tools -p 'test_*.py'`.
Standard library only, no pytest.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
