from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from MTS_V4.production import build_production_runtime
from MTS_V4.runtime_config import ProductionRuntimeConfig, ResearchDirectorRuntimeConfig, RuntimeConfigurationError


class V4ProductionRuntimeTests(unittest.TestCase):
    def test_env_loader_requires_explicit_runtime_identity_but_not_api_key(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {
                "MTS_V4_STATE_DIR": directory,
                "MTS_RD_BASE_URL": "http://127.0.0.1:8000",
                "MTS_RD_MODEL": "Qwen3-32B-AWQ",
            }
            with patch.dict(os.environ, env, clear=True):
                config = ProductionRuntimeConfig.from_env()
            self.assertEqual(config.state_dir, Path(directory))
            self.assertEqual(config.research_director.base_url, "http://127.0.0.1:8000")
            self.assertEqual(config.research_director.model, "Qwen3-32B-AWQ")
            self.assertEqual(config.research_director.api_key, "")
            self.assertEqual(config.nexus_path, Path(directory) / "research_nexus.json")
            self.assertEqual(config.checkpoint_path, Path(directory) / "active_campaign.json")

    def test_env_loader_fails_before_runtime_when_required_identity_is_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeConfigurationError, "MTS_V4_STATE_DIR"):
                ProductionRuntimeConfig.from_env()

    def test_production_bundle_assembles_without_network_call(self):
        with tempfile.TemporaryDirectory() as directory:
            config = ProductionRuntimeConfig(
                state_dir=Path(directory),
                research_director=ResearchDirectorRuntimeConfig(
                    base_url="http://127.0.0.1:8000",
                    model="Qwen3-32B-AWQ",
                ),
            )
            bundle = build_production_runtime(config)
            self.assertEqual(bundle.config, config)
            self.assertTrue(Path(directory).is_dir())
            self.assertGreater(len(bundle.runtime.catalog.all()), 3)
            self.assertGreater(len(bundle.runtime.concepts.all()), 10)
            self.assertIsNotNone(bundle.campaign_runner)
            # Assembly alone must not create durable scientific content.
            self.assertFalse(config.nexus_path.exists())
            self.assertFalse(config.checkpoint_path.exists())


if __name__ == "__main__":
    unittest.main()
