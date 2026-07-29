import unittest

from jewelry_assistant import SYSTEM_PROMPT, build_messages


class BuildMessagesTests(unittest.TestCase):
    def test_adds_system_prompt_and_keeps_recent_messages(self):
        history = [{"role": "user", "content": str(index)} for index in range(15)]

        result = build_messages(history, limit=3)

        self.assertEqual(result[0], {"role": "system", "content": SYSTEM_PROMPT})
        self.assertEqual([message["content"] for message in result[1:]], ["12", "13", "14"])

    def test_discards_unsupported_or_invalid_messages(self):
        history = [
            {"role": "tool", "content": "ignore"},
            {"role": "user", "content": None},
            {"role": "assistant", "content": "Welcome"},
        ]

        self.assertEqual(build_messages(history)[-1], {"role": "assistant", "content": "Welcome"})


if __name__ == "__main__":
    unittest.main()
