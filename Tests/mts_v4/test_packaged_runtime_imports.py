from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PackagedRuntimeImportTests(unittest.TestCase):
    def test_runtime_imports_work_outside_repository_checkout(self) -> None:
        """Catch packaging defects hidden by pytest's repository-root pythonpath."""
        repo_root = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)

        code = (
            "from Core.deterministic_computation import execute_computations; "
            "from MTS_V4.discovery_methods import discovery_method_catalog; "
            "assert callable(execute_computations); "
            "assert discovery_method_catalog().all()"
        )

        with tempfile.TemporaryDirectory() as outside_checkout:
            completed = subprocess.run(
                [sys.executable, "-I", "-c", code],
                cwd=outside_checkout,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(
            completed.returncode,
            0,
            msg=(
                "Packaged runtime imports failed outside the repository checkout. "
                "This usually means a runtime package is missing from distribution "
                "metadata or the active environment needs to be reinstalled after a "
                "packaging change.\n"
                f"repo_root={repo_root}\n"
                f"stdout={completed.stdout}\n"
                f"stderr={completed.stderr}"
            ),
        )


if __name__ == "__main__":
    unittest.main()
