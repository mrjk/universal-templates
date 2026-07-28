"""snip CLI smoke tests."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ut_cli import snip_cmd, anchors
from ut_cli import config


class TestSnipSmoke(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.env = {config.ENV_CATALOG_REPO: str(self.root)}

    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            snip_cmd.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_list_catalog(self):
        with mock.patch.dict(os.environ, self.env):
            code = snip_cmd.main(["list"])
        self.assertEqual(code, 0)

    def test_list_anchors_in_file(self):
        consumer = self.root / "files/src/_fixture/consumer.sh"
        with mock.patch.dict(os.environ, self.env):
            code = snip_cmd.main(["list", str(consumer)])
        self.assertEqual(code, 0)

    def test_add_local_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            with mock.patch.dict(os.environ, self.env):
                # Local catalog uses directory contents; may need vendir OR filesystem.
                # fetch_bytes works without vendir for local.
                code = snip_cmd.main(
                    ["add", "files/src/_fixture/snippet.sh", "--dest", str(dest), "-y"]
                )
            self.assertEqual(code, 0)
            self.assertTrue((dest / "snippet.sh").is_file() or any(dest.rglob("snippet.sh")))

    def test_sync_file_anchors_yes(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "consumer.sh"
            shutil.copy(
                self.root / "files/src/_fixture/consumer.sh",
                script,
            )
            with mock.patch.dict(os.environ, self.env):
                code = snip_cmd.main(["sync", str(script), "-y"])
            self.assertEqual(code, 0)
            text = script.read_text(encoding="utf-8")
            found = anchors.parse_anchors(text)
            self.assertEqual(len(found), 2)
            for a in found:
                body = anchors.get_body(text, a)
                self.assertIn("FIXTURE_MARKER", body)


if __name__ == "__main__":
    unittest.main()
