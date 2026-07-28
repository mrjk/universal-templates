"""Tests for snip anchor parse/apply."""

from __future__ import annotations

import unittest

from ut_cli import anchors


SAMPLE = """#!/usr/bin/env bash
# >>> snip:id=logging-setup path=files/src/logging-setup ref=1.2.3
log() { echo hi; }
# <<< snip:id=logging-setup

# >>> snip:id=other path=files/src/other ref=main
OTHER=1
# <<< snip:id=other
"""


class TestAnchors(unittest.TestCase):
    def test_parse_two_anchors(self):
        found = anchors.parse_anchors(SAMPLE)
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].id, "logging-setup")
        self.assertEqual(found[0].path, "files/src/logging-setup")
        self.assertEqual(found[0].ref, "1.2.3")
        self.assertEqual(found[1].id, "other")

    def test_get_and_replace_body(self):
        found = anchors.parse_anchors(SAMPLE)
        a = found[0]
        body = anchors.get_body(SAMPLE, a)
        self.assertIn("log()", body)
        updated = anchors.replace_body(SAMPLE, a, "log() { echo new; }\n", new_ref="1.3.0")
        anew = anchors.parse_anchors(updated)
        self.assertEqual(anew[0].ref, "1.3.0")
        self.assertIn("echo new", anchors.get_body(updated, anew[0]))
        # other anchor preserved
        self.assertEqual(anew[1].id, "other")
        self.assertIn("OTHER=1", anchors.get_body(updated, anew[1]))

    def test_slash_slash_prefix(self):
        text = "// >>> snip:id=x path=files/a ref=1\nbody\n// <<< snip:id=x\n"
        found = anchors.parse_anchors(text)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, "x")

    def test_file_header(self):
        text = """#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# Template source: https://github.com/mrjk/universal-templates.git
# curr_version: 1.2.3
echo hi
"""
        h = anchors.parse_file_header(text)
        self.assertIn("universal-templates", h.template_source or "")
        self.assertEqual(h.curr_version, "1.2.3")


if __name__ == "__main__":
    unittest.main()
