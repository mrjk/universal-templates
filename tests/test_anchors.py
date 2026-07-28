"""Tests for snip anchor/slot parse/apply."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr

from ut_cli import anchors


SAMPLE = """#!/usr/bin/env bash
# >>> snip:id=logging-setup path=files/src/logging-setup ref=1.2.3
log() { echo hi; }
# <<< snip:id=logging-setup

# >>> snip:id=other path=files/src/other ref=main
OTHER=1
# <<< snip:id=other
"""

BOILERPLATE_CATALOG = """#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# snip: path=files/src/_fixture/boilerplate.sh ref=main
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=main
FRAME=v2
# >>> snip:slot=main
# <<< snip:slot=main
# >>> snip:slot=extra
# <<< snip:slot=extra
tail
"""

BOILERPLATE_CONSUMER = """#!/usr/bin/env bash
# snip: sync with: snip sync %FILE%
# snip: path=files/src/_fixture/boilerplate.sh ref=old
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=old
FRAME=v1
# >>> snip:slot=main
echo user-main
# <<< snip:slot=main
# >>> snip:slot=orphan
echo gone
# <<< snip:slot=orphan
# >>> snip:slot=extra
echo user-extra
# <<< snip:slot=extra
old-tail
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
# snip: path=files/bin/x.sh ref=1.2.3
# snip: source=https://github.com/mrjk/universal-templates.git
# snip: version=1.2.3
echo hi
"""
        h = anchors.parse_file_header(text)
        self.assertIn("universal-templates", h.template_source or "")
        self.assertEqual(h.curr_version, "1.2.3")
        self.assertEqual(h.path, "files/bin/x.sh")
        self.assertEqual(h.ref, "1.2.3")

    def test_file_header_legacy(self):
        text = """#!/usr/bin/env bash
# snip: path=files/bin/x.sh ref=1.2.3
# Template source: https://github.com/mrjk/universal-templates.git
# curr_version: 1.2.3
"""
        h = anchors.parse_file_header(text)
        self.assertIn("universal-templates", h.template_source or "")
        self.assertEqual(h.curr_version, "1.2.3")
        self.assertEqual(h.ref, "1.2.3")

    def test_parse_slots(self):
        slots = anchors.parse_slots(BOILERPLATE_CONSUMER)
        self.assertEqual([s.id for s in slots], ["main", "orphan", "extra"])
        bodies = anchors.get_slot_bodies(BOILERPLATE_CONSUMER)
        self.assertIn("echo user-main", bodies["main"])

    def test_merge_boilerplate_preserves_slots(self):
        bodies = anchors.get_slot_bodies(BOILERPLATE_CONSUMER)
        err = io.StringIO()
        with redirect_stderr(err):
            merged = anchors.merge_boilerplate(BOILERPLATE_CATALOG, bodies)
        self.assertIn("orphan", err.getvalue())
        self.assertIn("FRAME=v2", merged)
        self.assertIn("tail", merged)
        self.assertNotIn("old-tail", merged)
        self.assertNotIn("orphan", [s.id for s in anchors.parse_slots(merged)])
        merged_bodies = anchors.get_slot_bodies(merged)
        self.assertIn("echo user-main", merged_bodies["main"])
        self.assertIn("echo user-extra", merged_bodies["extra"])

    def test_bump_file_header_ref(self):
        bumped = anchors.bump_file_header_ref(BOILERPLATE_CONSUMER, "main")
        h = anchors.parse_file_header(bumped)
        self.assertEqual(h.ref, "main")
        self.assertEqual(h.curr_version, "main")


if __name__ == "__main__":
    unittest.main()
