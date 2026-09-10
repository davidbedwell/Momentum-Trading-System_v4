from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_provider import SolResearchPackageAwareResearchDirector


class _FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(
            {"choices": [{"message": {"content": "{\"continue_research\":false}"}}]}
        ).encode("utf-8")


class SolProviderTests(unittest.TestCase):
    def test_sol_chat_completion_omits_temperature(self):
        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return _FakeResponse()

        with tempfile.TemporaryDirectory() as tmp:
            provider = SolResearchPackageAwareResearchDirector(
                research_package_store=JsonResearchPackageStore(Path(tmp) / "research_packages"),
                base_url="https://api.openai.com",
                model="gpt-5.6-sol",
                api_key="test-key",
            )
            with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                content = provider._chat_completion(
                    [{"role": "user", "content": "transport test"}]
                )

        self.assertEqual(captured["url"], "https://api.openai.com/v1/chat/completions")
        self.assertEqual(captured["body"]["model"], "gpt-5.6-sol")
        self.assertNotIn("temperature", captured["body"])
        self.assertEqual(content, '{"continue_research":false}')


if __name__ == "__main__":
    unittest.main()
