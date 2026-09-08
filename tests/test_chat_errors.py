"""Tests for the error-text redaction used by the chat interface."""

import unittest

from chat_errors import MASK, safe_error_text


class SafeErrorTextTests(unittest.TestCase):
    def test_masks_a_classic_key(self):
        message = "Incorrect API key provided: sk-AbCdEf0123456789. Find it at ..."
        result = safe_error_text(message)
        self.assertNotIn("sk-AbCdEf0123456789", result)
        self.assertIn(MASK, result)

    def test_masks_a_project_scoped_key(self):
        message = "Incorrect API key provided: sk-proj-Zz09_aB-cDeFgHiJkLmNoP."
        result = safe_error_text(message)
        self.assertNotIn("Zz09_aB-cDeFgHiJkLmNoP", result)
        self.assertIn(MASK, result)

    def test_masks_every_occurrence(self):
        message = "keys sk-aaaaaaaaaaaa and sk-bbbbbbbbbbbb both rejected"
        result = safe_error_text(message)
        self.assertNotIn("sk-aaaaaaaaaaaa", result)
        self.assertNotIn("sk-bbbbbbbbbbbb", result)
        self.assertEqual(result.count(MASK), 2)

    def test_leaves_an_actionable_message_intact(self):
        message = "Rate limit reached for gpt-3.5-turbo in org-abc on requests per min"
        self.assertEqual(safe_error_text(message), message)

    def test_accepts_an_exception_not_only_a_string(self):
        error = ValueError("bad key sk-cccccccccccc supplied")
        result = safe_error_text(error)
        self.assertNotIn("sk-cccccccccccc", result)
        self.assertIn(MASK, result)

    def test_does_not_mask_unrelated_text_beginning_with_sk(self):
        message = "the skill sk-ip was not applied"
        self.assertEqual(safe_error_text(message), message)


if __name__ == "__main__":
    unittest.main()
