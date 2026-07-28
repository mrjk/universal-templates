"""seed CLI smoke tests (mocked subprocess where possible)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ut_cli import seed_cmd
from ut_cli import config


class TestSeedSmoke(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.env = {config.ENV_CATALOG_REPO: str(self.root)}

    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            seed_cmd.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_list(self):
        with mock.patch.dict(os.environ, self.env):
            code = seed_cmd.main(["list"])
        self.assertEqual(code, 0)

    def test_new_invokes_copier(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out"
            dest.mkdir()
            with mock.patch.dict(os.environ, self.env):
                with mock.patch("ut_cli.copier_wrap.proc.run") as run:
                    with mock.patch("ut_cli.copier_wrap.copier_bin", return_value="copier"):
                        code = seed_cmd.main(
                            ["new", "projects/_fixture", str(dest), "-y"]
                        )
            self.assertEqual(code, 0)
            self.assertTrue(run.called)
            cmd = run.call_args[0][0]
            self.assertEqual(cmd[0], "copier")
            self.assertEqual(cmd[1], "copy")
            self.assertIn("--defaults", cmd)

    def test_sync_requires_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, self.env):
                with self.assertRaises(SystemExit):
                    seed_cmd.main(["sync", tmp, "-y"])


if __name__ == "__main__":
    unittest.main()
