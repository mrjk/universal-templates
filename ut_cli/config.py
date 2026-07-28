"""Defaults and shared flag parsing helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_CATALOG_REPO = "https://github.com/mrjk/universal-templates.git"
ENV_CATALOG_REPO = "UT_CATALOG_REPO"


@dataclass
class CommonOpts:
    yes: bool = False
    ref: str | None = None


def catalog_repo() -> str:
    value = os.environ.get(ENV_CATALOG_REPO, "").strip()
    return value or DEFAULT_CATALOG_REPO


def add_common_flags(parser) -> None:
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Non-interactive: accept catalog changes without confirm",
    )
    parser.add_argument(
        "--ref",
        metavar="REF",
        help="Catalog git ref (tag, branch, or sha)",
    )


def common_from_args(args) -> CommonOpts:
    return CommonOpts(yes=bool(getattr(args, "yes", False)), ref=getattr(args, "ref", None))
