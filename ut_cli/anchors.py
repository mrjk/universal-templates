"""Parse and apply snip region anchors and boilerplate slots."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

# Comment prefix + >>> snip:id=NAME path=... ref=...
_BEGIN_RE = re.compile(
    r"^(?P<prefix>\s*(?:#|//|;|--)?\s*)"
    r">>>\s*snip:id=(?P<id>[^\s]+)"
    r"(?P<meta>(?:\s+\w+=\S+)*)\s*$"
)
_END_RE = re.compile(
    r"^(?P<prefix>\s*(?:#|//|;|--)?\s*)"
    r"<<<\s*snip:id=(?P<id>[^\s]+)\s*$"
)
_SLOT_BEGIN_RE = re.compile(
    r"^(?P<prefix>\s*(?:#|//|;|--)?\s*)"
    r">>>\s*snip:slot=(?P<id>[^\s]+)\s*$"
)
_SLOT_END_RE = re.compile(
    r"^(?P<prefix>\s*(?:#|//|;|--)?\s*)"
    r"<<<\s*snip:slot=(?P<id>[^\s]+)\s*$"
)
_META_RE = re.compile(r"(\w+)=(\S+)")
# snip: path=files/... ref=main  (optional mode=boilerplate)
_HEADER_SNIP_RE = re.compile(
    r"snip:\s+(?P<meta>(?:\w+=\S+\s*)+)$"
)


@dataclass
class Anchor:
    id: str
    path: str | None
    ref: str | None
    start_line: int  # 0-based index of begin marker
    end_line: int  # 0-based index of end marker
    begin_text: str
    end_text: str
    prefix: str

    @property
    def body_lines(self) -> slice:
        return slice(self.start_line + 1, self.end_line)


@dataclass
class Slot:
    id: str
    start_line: int
    end_line: int
    begin_text: str
    end_text: str
    prefix: str

    @property
    def body_lines(self) -> slice:
        return slice(self.start_line + 1, self.end_line)


def _parse_meta(meta: str) -> dict[str, str]:
    return {k: v for k, v in _META_RE.findall(meta or "")}


def parse_anchors(text: str) -> list[Anchor]:
    lines = text.splitlines(keepends=True)
    anchors: list[Anchor] = []
    open_anchor: dict | None = None

    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        m_begin = _BEGIN_RE.match(stripped)
        if m_begin:
            meta = _parse_meta(m_begin.group("meta"))
            open_anchor = {
                "id": m_begin.group("id"),
                "path": meta.get("path"),
                "ref": meta.get("ref"),
                "start_line": i,
                "begin_text": line,
                "prefix": m_begin.group("prefix"),
            }
            continue
        m_end = _END_RE.match(stripped)
        if m_end and open_anchor and m_end.group("id") == open_anchor["id"]:
            anchors.append(
                Anchor(
                    id=open_anchor["id"],
                    path=open_anchor["path"],
                    ref=open_anchor["ref"],
                    start_line=open_anchor["start_line"],
                    end_line=i,
                    begin_text=open_anchor["begin_text"],
                    end_text=line,
                    prefix=open_anchor["prefix"],
                )
            )
            open_anchor = None
    return anchors


def parse_slots(text: str) -> list[Slot]:
    lines = text.splitlines(keepends=True)
    slots: list[Slot] = []
    open_slot: dict | None = None

    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        m_begin = _SLOT_BEGIN_RE.match(stripped)
        if m_begin:
            open_slot = {
                "id": m_begin.group("id"),
                "start_line": i,
                "begin_text": line,
                "prefix": m_begin.group("prefix"),
            }
            continue
        m_end = _SLOT_END_RE.match(stripped)
        if m_end and open_slot and m_end.group("id") == open_slot["id"]:
            slots.append(
                Slot(
                    id=open_slot["id"],
                    start_line=open_slot["start_line"],
                    end_line=i,
                    begin_text=open_slot["begin_text"],
                    end_text=line,
                    prefix=open_slot["prefix"],
                )
            )
            open_slot = None
    return slots


def get_body(text: str, region: Anchor | Slot) -> str:
    lines = text.splitlines(keepends=True)
    return "".join(lines[region.body_lines])


def get_slot_bodies(text: str) -> dict[str, str]:
    return {s.id: get_body(text, s) for s in parse_slots(text)}


def replace_body(text: str, anchor: Anchor, new_body: str, *, new_ref: str | None = None) -> str:
    lines = text.splitlines(keepends=True)
    body = new_body
    if body and not body.endswith("\n"):
        body += "\n"
    begin = anchor.begin_text
    if new_ref is not None:
        begin = _bump_ref(begin, new_ref)
    if not begin.endswith("\n"):
        begin += "\n"
    body_lines = body.splitlines(keepends=True)
    new_lines = lines[: anchor.start_line] + [begin] + body_lines + lines[anchor.end_line :]
    return "".join(new_lines)


def _bump_ref(begin_line: str, new_ref: str) -> str:
    if re.search(r"\bref=", begin_line):
        return re.sub(r"\bref=\S+", f"ref={new_ref}", begin_line)
    # insert before EOL
    return begin_line.rstrip("\n") + f" ref={new_ref}\n"


def merge_boilerplate(
    catalog_text: str,
    slot_bodies: dict[str, str],
    *,
    warn_orphans: bool = True,
) -> str:
    """Apply consumer slot bodies onto a fresh catalog template.

    Catalog wins for frame; named slots take consumer bodies when present.
    Orphan consumer slots (not in catalog) are reported and dropped.
    """
    catalog_slots = parse_slots(catalog_text)
    catalog_ids = {s.id for s in catalog_slots}
    if warn_orphans:
        for name in sorted(set(slot_bodies) - catalog_ids):
            print(
                f"warning: orphan slot '{name}' not in catalog template; dropping",
                file=sys.stderr,
            )

    if not catalog_slots:
        return catalog_text

    lines = catalog_text.splitlines(keepends=True)
    # Apply from bottom to top so line indices stay valid
    for slot in sorted(catalog_slots, key=lambda s: s.start_line, reverse=True):
        body = slot_bodies.get(slot.id, get_body(catalog_text, slot))
        if body and not body.endswith("\n"):
            body += "\n"
        begin = slot.begin_text
        if not begin.endswith("\n"):
            begin += "\n"
        end = slot.end_text
        body_lines = body.splitlines(keepends=True) if body else []
        lines = lines[: slot.start_line] + [begin] + body_lines + [end] + lines[slot.end_line + 1 :]
    return "".join(lines)


@dataclass
class FileHeader:
    template_source: str | None = None
    curr_version: str | None = None
    path: str | None = None
    ref: str | None = None


# Legacy freeform lines (still accepted):
#   # Template source: URL
#   # curr_version: PIN
# Canonical (all snip-managed metadata uses the snip: prefix):
#   # snip: sync with: snip sync %FILE%
#   # snip: path=files/... ref=PIN
#   # snip: source=URL
#   # snip: version=PIN
_LEGACY_SOURCE_RE = re.compile(r"Template source:\s*(\S+)")
_LEGACY_VERSION_RE = re.compile(r"curr_version:\s*(\S+)")
_SNIP_VERSION_RE = re.compile(r"snip:\s+version=(\S+)")


def parse_file_header(text: str) -> FileHeader:
    source = None
    version = None
    path = None
    ref = None
    for line in text.splitlines()[:40]:
        m_src = _LEGACY_SOURCE_RE.search(line)
        if m_src:
            source = m_src.group(1)
        m_ver = _LEGACY_VERSION_RE.search(line)
        if m_ver:
            version = m_ver.group(1)
        m = _HEADER_SNIP_RE.search(line)
        if m:
            meta = _parse_meta(m.group("meta"))
            if "path" in meta:
                path = meta["path"]
            if "ref" in meta:
                ref = meta["ref"]
            if "source" in meta:
                source = meta["source"]
            if "version" in meta:
                version = meta["version"]
    if ref is None and version is not None:
        ref = version
    return FileHeader(
        template_source=source,
        curr_version=version,
        path=path,
        ref=ref,
    )


def bump_file_header_ref(text: str, new_ref: str) -> str:
    """Bump snip pin fields (ref= / version= / legacy curr_version:) in the first ~40 lines."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for i, line in enumerate(lines):
        if i >= 40:
            out.append(line)
            continue
        nl = "\n" if line.endswith("\n") else ""
        stripped = line.rstrip("\n")

        if _SNIP_VERSION_RE.search(stripped):
            out.append(re.sub(r"\bversion=\S+", f"version={new_ref}", stripped) + nl)
            continue
        if _LEGACY_VERSION_RE.search(stripped) and "snip:" not in stripped:
            prefix, _, _ = stripped.partition("curr_version:")
            out.append(f"{prefix}curr_version: {new_ref}{nl}")
            continue

        m = _HEADER_SNIP_RE.search(stripped)
        if m:
            meta = _parse_meta(m.group("meta"))
            # Only touch path/ref identity lines — not source= or version=-only lines
            if "path" in meta or "ref" in meta:
                if re.search(r"\bref=", stripped):
                    out.append(re.sub(r"\bref=\S+", f"ref={new_ref}", stripped) + nl)
                else:
                    out.append(f"{stripped} ref={new_ref}{nl}")
                continue

        out.append(line)
    return "".join(out)
