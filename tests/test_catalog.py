"""Catalog resolution and listing tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ut_cli import catalog
from ut_cli import config


class TestCatalog(unittest.TestCase):
    def test_default_catalog_repo(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(config.ENV_CATALOG_REPO, None)
            self.assertEqual(config.catalog_repo(), config.DEFAULT_CATALOG_REPO)

    def test_list_local_projects(self):
        root = Path(__file__).resolve().parents[1]
        with mock.patch.dict(os.environ, {config.ENV_CATALOG_REPO: str(root)}):
            items = catalog.list_tree("projects")
        self.assertTrue(any(i.endswith("projects/_fixture") or i == "projects/_fixture" for i in items))

    def test_list_local_files(self):
        root = Path(__file__).resolve().parents[1]
        with mock.patch.dict(os.environ, {config.ENV_CATALOG_REPO: str(root)}):
            items = catalog.list_tree("files")
        self.assertTrue(any("_fixture" in i for i in items))

    def test_numbered_menu_select(self):
        with mock.patch("builtins.input", return_value="2"):
            choice = catalog.numbered_menu("T", ["a", "b", "c"])
        self.assertEqual(choice, "b")

    def test_local_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {config.ENV_CATALOG_REPO: tmp}):
                self.assertEqual(catalog.catalog_root(), Path(tmp).resolve())


if __name__ == "__main__":
    unittest.main()
