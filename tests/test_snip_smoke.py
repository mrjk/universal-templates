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

    def test_sync_boilerplate_preserves_slot(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "boilerplate.sh"
            script.write_text(
                """#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# snip: path=files/src/_fixture/boilerplate.sh ref=old
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=old
FRAME_MARKER=stale
# >>> snip:slot=main
echo custom-user
# <<< snip:slot=main
echo old-tail
""",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, self.env):
                code = snip_cmd.main(["sync", str(script), "-y"])
            self.assertEqual(code, 0)
            text = script.read_text(encoding="utf-8")
            self.assertIn("FRAME_MARKER=v1", text)
            self.assertIn("echo custom-user", text)
            self.assertIn("echo done", text)
            self.assertNotIn("old-tail", text)
            h = anchors.parse_file_header(text)
            self.assertEqual(h.ref, "old")
            bodies = anchors.get_slot_bodies(text)
            self.assertIn("echo custom-user", bodies["main"])

    def test_list_boilerplate_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "b.sh"
            script.write_text(
                "# snip: path=files/src/_fixture/boilerplate.sh ref=main\n"
                "# >>> snip:slot=main\nx\n# <<< snip:slot=main\n",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, self.env):
                code = snip_cmd.main(["list", str(script)])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
